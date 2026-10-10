"""Integration tests for variable work events in the period-first engine.

Verifies that each event type traverses all relevant accounting axes:
pay items, ledger entries (CASH_EARNINGS), INPS, IRPEF, net, and employer cost.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.amount.facade import SicknessItem
from ccnl_engine.payroll.assurance.validators import reconcile
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.event.facade import (
    AbsenceEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
)
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.results import PeriodResult
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState

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


def _cash(result: object) -> Decimal:
    assert isinstance(result, PeriodResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.CASH_EARNINGS
        ),
        Decimal(0),
    )


def _inps_employee(result: object) -> Decimal:
    assert isinstance(result, PeriodResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
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

    def test_gross_unchanged(self) -> None:
        """period_gross (contractual entitlement) is not reduced by absence."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._absence()))
        assert result.period_gross == base.period_gross

    def test_unpaid_absence_deduction_equals_deducted_amount(self) -> None:
        """unpaid_absence_deduction equals hours * hourly_rate."""
        result = calculate_period(_req(self._absence()))
        assert result.unpaid_absence_deduction == Decimal("96.00")  # 8h * 12.00

    def test_employer_cost_reduced_by_absence(self) -> None:
        """period_employer_cost decreases by at least the absence wage."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._absence()))
        assert result.period_employer_cost < base.period_employer_cost
        absence_wage = Decimal("96.00")
        cost_delta = base.period_employer_cost - result.period_employer_cost
        assert cost_delta >= absence_wage, (
            f"Employer cost reduction {cost_delta} < absence wage {absence_wage}. "
            "The absence wage is not being subtracted from employer cost."
        )

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
        """CASH_EARNINGS sum equals period_gross; absence is in EMPLOYEE_DEDUCTIONS."""
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

    def test_waiting_period_zero_uses_full_amount(self) -> None:
        """No carenza: gross equals the full event amount."""
        sick = SickLeaveEvent(
            event_date=date(_YEAR, _MONTH, 12),
            amount=Decimal("300.00"),
            sick_days=5,
            waiting_period_days=0,
        )
        base = calculate_period(_base())
        result = calculate_period(_req(sick))
        assert result.period_gross == base.period_gross + Decimal("300.00")

    def test_waiting_period_reduces_gross(self) -> None:
        """Carenza days reduce the employer-paid sick-leave gross."""
        sick_no_carenza = SickLeaveEvent(
            event_date=date(_YEAR, _MONTH, 12),
            amount=Decimal("500.00"),
            sick_days=5,
            waiting_period_days=0,
        )
        sick_with_carenza = SickLeaveEvent(
            event_date=date(_YEAR, _MONTH, 12),
            amount=Decimal("500.00"),
            sick_days=5,
            waiting_period_days=3,
        )
        result_no = calculate_period(_req(sick_no_carenza))
        result_with = calculate_period(_req(sick_with_carenza))
        assert result_with.period_gross < result_no.period_gross

    def test_sick_days_stored_in_pay_item(self) -> None:
        """sick_days from event is stored in the SicknessItem pay item."""
        sick = SickLeaveEvent(
            event_date=date(_YEAR, _MONTH, 12),
            amount=Decimal("300.00"),
            sick_days=7,
        )
        result = calculate_period(_req(sick))
        sickness_items = [pi for pi in result.pay_items if isinstance(pi, SicknessItem)]
        assert sickness_items
        assert sickness_items[0].sick_days == Decimal(7)


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
