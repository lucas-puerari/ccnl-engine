"""Integration tests for event treatment across accounting axes.

Verifies the TFR treatment policy per event type, combined events in one
period and the arrears reference period.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
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

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_MONTH = 3
_PID = PeriodId(year=_YEAR, month=_MONTH)
_PAYMENT = date(_YEAR, _MONTH, 28)


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


class TestArrearsEventReferencePeriod:
    """ArrearsEvent.reference_period stores the origin competence period."""

    def test_reference_period_stored(self) -> None:
        """reference_period is retrievable from the event."""
        ref = PeriodId(year=2025, month=6)
        evt = ArrearsEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("1000.00"),
            separate_tax_rate=Decimal("0.23"),
            reference_period=ref,
        )
        assert evt.reference_period == ref

    def test_reference_period_defaults_none(self) -> None:
        """reference_period defaults to None when omitted."""
        evt = ArrearsEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("1000.00"),
            separate_tax_rate=Decimal("0.23"),
        )
        assert evt.reference_period is None

    def test_arrears_with_reference_period_runs(self) -> None:
        """calculate_period succeeds when ArrearsEvent carries a reference_period."""
        evt = ArrearsEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("500.00"),
            separate_tax_rate=Decimal("0.20"),
            reference_period=PeriodId(year=2025, month=3),
        )
        result = calculate_period(_req(evt))
        assert result.period_gross > Decimal(0)


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
        assert _tfr(result) == _tfr(base)

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
        assert _tfr(result) == _tfr(base)

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
        assert _tfr(result) == _tfr(base)

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
