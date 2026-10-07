"""Integration tests for event treatment across accounting axes.

Verifies the TFR treatment policy per event type, combined events in one
period and the arrears reference period.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BonusEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.shared.domain.errors import InvalidInputError

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_MONTH = 3
_PID = PeriodId(year=_YEAR, month=_MONTH)
_PAYMENT = date(_YEAR, _MONTH, 28)
#: L. 297/1982 art. 3 c. 15: 0.30% from July 1982 plus 0.20% from 1983.
_ADDITIONAL_IVS = Decimal("0.0050")


def _req(*events: object) -> PeriodCalculationRequest:

    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
    )


def _base() -> PeriodCalculationRequest:
    return _req()


def _arrears(reference: PeriodId | None) -> ArrearsEvent:
    return ArrearsEvent(
        event_date=date(_YEAR, _MONTH, 1),
        amount=Decimal("2000.00"),
        separate_tax_rate=Decimal("0.23"),
        reference_period=reference,
    )


def _account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _arrears_decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "contract_renewal_arrears" and d.rule == "tuir-art17-c1-b"
    )
    return decision


class TestArrearsEventReferencePeriod:
    """The reference year selects the taxation of renewal arrears.

    Art. 17 c. 1 lett. b TUIR (in force until 31 December 2026,
    https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.repubblica:decreto:1986-12-22;917~art17)
    taxes separately the "emolumenti arretrati per prestazioni di lavoro
    dipendente riferibili ad anni precedenti"; arrears of the tax year of
    the run are ordinary income of the year (art. 51 c. 1 TUIR).
    """

    def test_earlier_year_is_taxed_separately(self) -> None:
        """2025 arrears paid in March 2026: 2,000.00 x 0.23 = 460.00 separate."""
        result = calculate_period(_req(_arrears(PeriodId(year=2025, month=6))))
        decision = _arrears_decision(result)

        assert _account(result, AccountKind.SEPARATE_TAX) == Decimal("460.00")
        assert decision.reason_code == "separate_taxation"
        assert decision.status is CalculationStatus.FINAL
        assert decision.inputs["reference_period"] == "2025-06"
        assert decision.amount == Decimal("460.00")
        assert all(b.detail != "reference_period" for b in result.blockers)

    def test_same_year_enters_the_ordinary_irpef_base(self) -> None:
        """January 2026 arrears paid in March 2026 are ordinary income.

        No separate tax; the taxable income grows by the arrears less the
        employee contributions they add (art. 51 c. 2 lett. a TUIR).
        """
        base = calculate_period(_base())
        result = calculate_period(_req(_arrears(PeriodId(year=_YEAR, month=1))))
        added_inps = _account(result, AccountKind.EMPLOYEE_CONTRIBUTIONS) - _account(
            base, AccountKind.EMPLOYEE_CONTRIBUTIONS
        )
        taxable = (
            result.closing_state.cash.earnings.taxable
            - base.closing_state.cash.earnings.taxable
        )

        assert _account(result, AccountKind.SEPARATE_TAX) == Decimal(0)
        assert taxable == Decimal("2000.00") - added_inps
        assert result.tax_computation.ordinary_tax > base.tax_computation.ordinary_tax
        assert _arrears_decision(result).reason_code == "ordinary_taxation"
        assert reconcile(result, PeriodState.zero()).ok

    def test_unknown_year_blocks_the_run(self) -> None:
        """Without reference_period the taxation is undetermined: a blocker."""
        result = calculate_period(_req(_arrears(None)))
        decision = _arrears_decision(result)

        assert _account(result, AccountKind.SEPARATE_TAX) == Decimal("460.00")
        assert decision.reason_code == "reference_period_unknown"
        assert decision.status is CalculationStatus.INCOMPLETE
        assert decision.inputs["reference_period"] == "unknown"
        assert (BlockerCode.MISSING_FACT, "reference_period") in {
            (b.code, b.detail) for b in result.blockers
        }
        assert not result.is_payable

    def test_later_year_is_rejected(self) -> None:
        """Arrears cannot refer to a year after the tax year of the run."""
        with pytest.raises(InvalidInputError, match="after the tax year 2026"):
            calculate_period(_req(_arrears(PeriodId(year=2027, month=1))))


def _tfr(result: object) -> Decimal:
    assert isinstance(result, PeriodResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.TFR_ACCRUAL
        ),
        Decimal(0),
    )


def _quota(result: PeriodResult) -> Decimal:
    """Return the art. 2120 c.c. quota of the run.

    Returns:
        The quota the TFR decision records, before the deduction.
    """
    (decision,) = (d for d in result.decisions if d.capability == "tfr")
    quota = decision.inputs["quota"]
    assert isinstance(quota, Decimal)
    return quota


def _assert_event_out_of_tfr(result: PeriodResult, base: PeriodResult) -> None:
    """Assert the event leaves the quota unchanged but bears the extra IVS.

    L. 297/1982 art. 3 cc. 15-16: the 0.50% additional IVS is charged on
    the whole INPS taxable pay, the event included, and deducted from the
    TFR quota of the period.
    """
    assert _quota(result) == _quota(base)
    deduction = money(result.period_gross * _ADDITIONAL_IVS)
    assert _tfr(result) == _quota(result) - deduction
    assert _tfr(result) < _tfr(base)


class TestEventTreatmentPolicy:
    """Treatment table governs TFR axis: absence=True, overtime/night/bonus=False."""

    def test_overtime_does_not_increase_tfr(self) -> None:
        """OvertimeEvent gross does not enter the TFR accrual base."""
        base = calculate_period(_base())
        result = calculate_period(
            _req(
                OvertimeEvent(
                    event_date=date(_YEAR, _MONTH, 5),
                    hours=Decimal(8),
                    hourly_rate=Decimal("12.50"),
                    multiplier=Decimal("1.25"),
                )
            )
        )
        _assert_event_out_of_tfr(result, base)

    def test_night_shift_does_not_increase_tfr(self) -> None:
        """NightShiftEvent supplement does not enter the TFR accrual base."""
        base = calculate_period(_base())
        result = calculate_period(
            _req(
                NightShiftEvent(
                    event_date=date(_YEAR, _MONTH, 10),
                    supplement_amount=Decimal("80.00"),
                )
            )
        )
        _assert_event_out_of_tfr(result, base)

    def test_bonus_does_not_increase_tfr(self) -> None:
        """BonusEvent amount does not enter the TFR accrual base."""
        base = calculate_period(_base())
        result = calculate_period(
            _req(
                BonusEvent(
                    event_date=date(_YEAR, _MONTH, 28), amount=Decimal("1000.00")
                )
            )
        )
        _assert_event_out_of_tfr(result, base)

    def test_absence_decreases_tfr(self) -> None:
        """AbsenceEvent deduction reduces the TFR accrual base."""
        base = calculate_period(_base())
        result = calculate_period(
            _req(
                AbsenceEvent(
                    event_date=date(_YEAR, _MONTH, 20),
                    hours=Decimal(8),
                    hourly_rate=Decimal("12.00"),
                )
            )
        )
        assert _tfr(result) < _tfr(base)


class TestMultipleEvents:
    """Multiple events in a single period are all accounted correctly."""

    def test_two_events_gross_cumulates(self) -> None:
        """Gross from two events sums correctly with the base salary."""
        base = calculate_period(_base())
        overtime = OvertimeEvent(
            event_date=date(_YEAR, _MONTH, 5),
            hours=Decimal(4),
            hourly_rate=Decimal("12.50"),
            multiplier=Decimal("1.25"),
        )
        bonus = BonusEvent(event_date=date(_YEAR, _MONTH, 28), amount=Decimal("500.00"))
        result = calculate_period(_req(overtime, bonus))
        overtime_gross = (Decimal(4) * Decimal("12.50") * Decimal("1.25")).quantize(
            Decimal("0.01")
        )
        assert result.period_gross == (
            base.period_gross + overtime_gross + Decimal("500.00")
        )

    def test_reconcile_passes_with_multiple_events(self) -> None:
        """All reconciliation invariants hold with multiple event types."""
        events = (
            OvertimeEvent(
                event_date=date(_YEAR, _MONTH, 5),
                hours=Decimal(8),
                hourly_rate=Decimal("12.50"),
            ),
            NightShiftEvent(
                event_date=date(_YEAR, _MONTH, 10), supplement_amount=Decimal("50.00")
            ),
            WelfareEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("100.00")),
        )
        result = calculate_period(_req(*events))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations

    def test_pay_item_count_matches_events_plus_base(self) -> None:
        """Pay item count = base items + event count (6 base + 2 events here)."""
        events = (
            BonusEvent(event_date=date(_YEAR, _MONTH, 28), amount=Decimal("300.00")),
            WelfareEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("150.00")),
        )
        result = calculate_period(_req(*events))
        # Base items: base_salary, inps_employee, irpef, inps_employer, tfr, tratt_integ
        base_result = calculate_period(_base())
        assert len(result.pay_items) == len(base_result.pay_items) + 2

    def test_ledger_entry_count_matches_events_plus_base(self) -> None:
        """Ledger entry count = base entries + event count."""
        events = (
            BonusEvent(event_date=date(_YEAR, _MONTH, 28), amount=Decimal("300.00")),
            SickLeaveEvent(
                event_date=date(_YEAR, _MONTH, 12), amount=Decimal("200.00")
            ),
        )
        result = calculate_period(_req(*events))
        base_result = calculate_period(_base())
        assert len(result.ledger_entries) == len(base_result.ledger_entries) + 2
