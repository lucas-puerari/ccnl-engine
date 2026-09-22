"""Integration tests for variable work events in the period-first engine.

Verifies that each event type traverses all relevant accounting axes:
pay items, ledger entries (CASH_EARNINGS), INPS, IRPEF, net, and employer cost.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_MONTH = 3
_PID = PeriodId(year=_YEAR, month=_MONTH)
_PAYMENT = date(_YEAR, _MONTH, 28)


def _req(*events: object) -> PeriodCalculationRequest:

    return PeriodCalculationRequest(
        period_id=_PID,
        payment_date=_PAYMENT,
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=tuple(events),  # type: ignore[arg-type]
    )


def _base() -> PeriodCalculationRequest:
    return _req()


def _cash(result: object) -> Decimal:
    assert isinstance(result, PeriodCalculationResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.CASH_EARNINGS
        ),
        Decimal(0),
    )


def _inps_employee(result: object) -> Decimal:
    assert isinstance(result, PeriodCalculationResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
        ),
        Decimal(0),
    )


def _employer_contrib(result: object) -> Decimal:
    assert isinstance(result, PeriodCalculationResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYER_CONTRIBUTIONS
        ),
        Decimal(0),
    )


class TestNoEvents:
    """Without events the result is identical to the base calculation."""

    def test_no_events_matches_base(self) -> None:
        """A request with no events produces the same gross as the base case."""
        base = calculate_period(_base())
        with_empty = calculate_period(_req())
        assert base.period_gross == with_empty.period_gross
        assert base.period_net == with_empty.period_net


class TestOvertimeEventAccounting:
    """OvertimeEvent increases gross, INPS and IRPEF axes but not TFR."""

    def _overtime(self) -> OvertimeEvent:
        return OvertimeEvent(
            event_date=date(_YEAR, _MONTH, 5),
            hours=Decimal(8),
            hourly_rate=Decimal("12.50"),
            multiplier=Decimal("1.25"),
        )

    def test_gross_increases_by_overtime_amount(self) -> None:
        """period_gross increases by the overtime gross amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._overtime()))
        overtime_gross = Decimal(8) * Decimal("12.50") * Decimal("1.25")
        assert result.period_gross == base.period_gross + overtime_gross.quantize(
            Decimal("0.01")
        )

    def test_cash_earnings_equals_period_gross(self) -> None:
        """CASH_EARNINGS ledger sum equals period_gross (I13 invariant)."""
        result = calculate_period(_req(self._overtime()))
        assert _cash(result) == result.period_gross

    def test_inps_increases_with_overtime(self) -> None:
        """INPS employee contributions increase when overtime is added."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._overtime()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_employer_cost_increases_with_overtime(self) -> None:
        """Employer cost increases when overtime is added."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._overtime()))
        assert result.period_employer_cost > base.period_employer_cost

    def test_overtime_pay_item_in_result(self) -> None:
        """An OvertimeEarning pay item appears in the result."""
        result = calculate_period(_req(self._overtime()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "overtime_earning" in kinds

    def test_overtime_has_cash_earnings_entry(self) -> None:
        """The overtime event produces a CASH_EARNINGS ledger entry."""
        result = calculate_period(_req(self._overtime()))
        overtime_entries = [
            e
            for e in result.ledger_entries
            if e.account == AccountKind.CASH_EARNINGS
            and e.pay_item_kind == "overtime_earning"
        ]
        assert len(overtime_entries) == 1

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for an overtime period."""
        result = calculate_period(_req(self._overtime()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestNightShiftEventAccounting:
    """NightShiftEvent adds to gross, INPS and IRPEF but not TFR."""

    def _night(self) -> NightShiftEvent:
        return NightShiftEvent(
            event_date=date(_YEAR, _MONTH, 10), supplement_amount=Decimal("80.00")
        )

    def test_gross_increases(self) -> None:
        """period_gross increases by the night-shift supplement."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._night()))
        assert result.period_gross == base.period_gross + Decimal("80.00")

    def test_inps_increases(self) -> None:
        """INPS employee contributions increase for night-shift supplement."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._night()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_night_shift_pay_item_present(self) -> None:
        """A night_holiday_shift_earning pay item is present."""
        result = calculate_period(_req(self._night()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "night_holiday_shift_earning" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a night-shift period."""
        result = calculate_period(_req(self._night()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestHolidayWorkEventAccounting:
    """HolidayWorkEvent adds to gross and INPS but not TFR."""

    def _holiday(self) -> HolidayWorkEvent:
        return HolidayWorkEvent(
            event_date=date(_YEAR, _MONTH, 8), supplement_amount=Decimal("60.00")
        )

    def test_gross_increases(self) -> None:
        """period_gross increases by the holiday supplement."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._holiday()))
        assert result.period_gross == base.period_gross + Decimal("60.00")

    def test_inps_increases(self) -> None:
        """INPS increases for holiday supplement."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._holiday()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_holiday_pay_item_present(self) -> None:
        """A night_holiday_shift_earning pay item is present."""
        result = calculate_period(_req(self._holiday()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "night_holiday_shift_earning" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a holiday-work period."""
        result = calculate_period(_req(self._holiday()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestAbsenceEventAccounting:
    """AbsenceEvent reduces gross, INPS, TFR and IRPEF base."""

    def _absence(self) -> AbsenceEvent:
        return AbsenceEvent(
            event_date=date(_YEAR, _MONTH, 20),
            hours=Decimal(8),
            hourly_rate=Decimal("12.00"),
        )

    def test_gross_decreases(self) -> None:
        """period_gross decreases by the absence deduction."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._absence()))
        deduction = Decimal(8) * Decimal("12.00")
        assert result.period_gross == base.period_gross - deduction

    def test_inps_decreases(self) -> None:
        """INPS employee contributions decrease when gross decreases."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._absence()))
        assert _inps_employee(result) < _inps_employee(base)

    def test_absence_pay_item_present(self) -> None:
        """An absence_deduction pay item is present."""
        result = calculate_period(_req(self._absence()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "absence_deduction" in kinds

    def test_cash_earnings_equals_period_gross(self) -> None:
        """CASH_EARNINGS sum equals period_gross even with negative absence entry."""
        result = calculate_period(_req(self._absence()))
        assert _cash(result) == result.period_gross

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for an absence period."""
        result = calculate_period(_req(self._absence()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestSickLeaveEventAccounting:
    """SickLeaveEvent adds employer portion with INPS but no TFR."""

    def _sick(self) -> SickLeaveEvent:
        return SickLeaveEvent(
            event_date=date(_YEAR, _MONTH, 12), amount=Decimal("300.00")
        )

    def test_gross_increases(self) -> None:
        """period_gross increases by the sick-leave employer amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._sick()))
        assert result.period_gross == base.period_gross + Decimal("300.00")

    def test_inps_increases(self) -> None:
        """INPS increases for sick-leave employer portion."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._sick()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_sickness_pay_item_present(self) -> None:
        """A sickness_item pay item is present."""
        result = calculate_period(_req(self._sick()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "sickness_item" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a sick-leave period."""
        result = calculate_period(_req(self._sick()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestBonusEventAccounting:
    """BonusEvent adds to gross with INPS and IRPEF but not TFR."""

    def _bonus(self) -> BonusEvent:
        return BonusEvent(event_date=date(_YEAR, _MONTH, 28), amount=Decimal("1200.00"))

    def test_gross_increases(self) -> None:
        """period_gross increases by the bonus amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bonus()))
        assert result.period_gross == base.period_gross + Decimal("1200.00")

    def test_inps_increases(self) -> None:
        """INPS increases for bonus payment."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bonus()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_employer_cost_increases(self) -> None:
        """Employer cost increases with the bonus."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._bonus()))
        assert result.period_employer_cost > base.period_employer_cost

    def test_bonus_pay_item_present(self) -> None:
        """A bonus_earning pay item is present."""
        result = calculate_period(_req(self._bonus()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "bonus_earning" in kinds

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a bonus period."""
        result = calculate_period(_req(self._bonus()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestFringeEventAccounting:
    """FringeEvent is exempt below threshold and taxable above."""

    def _fringe_exempt(self) -> FringeEvent:
        return FringeEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("100.00"),
            exempt_threshold=Decimal("258.23"),
        )

    def _fringe_taxable(self) -> FringeEvent:
        return FringeEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("500.00"),
            exempt_threshold=Decimal("258.23"),
        )

    def test_exempt_fringe_does_not_increase_inps(self) -> None:
        """Fringe benefit below threshold does not affect INPS contributions."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_exempt()))
        assert _inps_employee(result) == _inps_employee(base)

    def test_exempt_fringe_adds_to_gross(self) -> None:
        """Fringe benefit below threshold still appears on the payslip (gross)."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_exempt()))
        assert result.period_gross == base.period_gross + Decimal("100.00")

    def test_taxable_fringe_increases_inps(self) -> None:
        """Fringe benefit above threshold is subject to INPS."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_taxable()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_taxable_fringe_adds_to_gross(self) -> None:
        """Fringe benefit above threshold appears on the payslip."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_taxable()))
        assert result.period_gross == base.period_gross + Decimal("500.00")

    def test_fringe_pay_item_present(self) -> None:
        """A fringe_benefit_item pay item is present."""
        result = calculate_period(_req(self._fringe_taxable()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "fringe_benefit_item" in kinds

    def test_reconcile_passes_exempt(self) -> None:
        """All reconciliation invariants hold for an exempt fringe period."""
        result = calculate_period(_req(self._fringe_exempt()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations

    def test_reconcile_passes_taxable(self) -> None:
        """All reconciliation invariants hold for a taxable fringe period."""
        result = calculate_period(_req(self._fringe_taxable()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


class TestWelfareEventAccounting:
    """WelfareEvent adds to gross but is exempt from INPS and IRPEF."""

    def _welfare(self) -> WelfareEvent:
        return WelfareEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("200.00"))

    def test_gross_increases(self) -> None:
        """period_gross increases by the welfare amount."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._welfare()))
        assert result.period_gross == base.period_gross + Decimal("200.00")

    def test_inps_unchanged(self) -> None:
        """Welfare benefit does not increase INPS contributions."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._welfare()))
        assert _inps_employee(result) == _inps_employee(base)

    def test_employer_contributions_unchanged(self) -> None:
        """Employer INPS contributions are not affected by welfare."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._welfare()))
        assert _employer_contrib(result) == _employer_contrib(base)

    def test_welfare_pay_item_present(self) -> None:
        """A welfare_item pay item is present."""
        result = calculate_period(_req(self._welfare()))
        kinds = {pi.kind for pi in result.pay_items}
        assert "welfare_item" in kinds

    def test_welfare_net_increases_by_full_amount(self) -> None:
        """Welfare benefit increases net by its full amount (no deductions)."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._welfare()))
        assert result.period_net == base.period_net + Decimal("200.00")

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a welfare period."""
        result = calculate_period(_req(self._welfare()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


def _tfr(result: object) -> Decimal:
    assert isinstance(result, PeriodCalculationResult)
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
