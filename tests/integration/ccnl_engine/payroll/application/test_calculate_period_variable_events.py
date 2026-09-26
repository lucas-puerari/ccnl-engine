"""Integration tests for variable work events in the period-first engine.

Verifies that each event type traverses all relevant accounting axes:
pay items, ledger entries (CASH_EARNINGS), INPS, IRPEF, net, and employer cost.
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
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import SicknessItem
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import FringeYtd

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


def _ncb(result: object) -> Decimal:
    assert isinstance(result, PeriodResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.NON_CASH_BENEFITS
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


def _employer_contrib(result: object) -> Decimal:
    assert isinstance(result, PeriodResult)
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


class TestFringeEventAccounting:
    """FringeEvent posts to NON_CASH_BENEFITS; taxable above threshold."""

    def _fringe_exempt(self) -> FringeEvent:
        # 100 EUR is well below the 2026 standard threshold (1000 EUR)
        return FringeEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("100.00"),
        )

    def _fringe_taxable(self) -> FringeEvent:
        # 1100 EUR exceeds the 2026 standard threshold (1000 EUR)
        return FringeEvent(
            event_date=date(_YEAR, _MONTH, 1),
            amount=Decimal("1100.00"),
        )

    def test_exempt_fringe_does_not_increase_inps(self) -> None:
        """Fringe benefit below threshold does not affect INPS contributions."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_exempt()))
        assert _inps_employee(result) == _inps_employee(base)

    def test_exempt_fringe_in_non_cash_benefits(self) -> None:
        """Fringe benefit is posted to NON_CASH_BENEFITS, not CASH_EARNINGS."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_exempt()))
        assert _ncb(result) == Decimal("100.00")
        assert result.period_gross == base.period_gross

    def test_taxable_fringe_increases_inps(self) -> None:
        """Fringe benefit above threshold is subject to INPS."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_taxable()))
        assert _inps_employee(result) > _inps_employee(base)

    def test_taxable_fringe_in_non_cash_benefits(self) -> None:
        """Fringe benefit above threshold still posts to NON_CASH_BENEFITS."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._fringe_taxable()))
        assert _ncb(result) == Decimal("1100.00")
        assert result.period_gross == base.period_gross

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


class TestBenefitBreakdown:
    """benefit_breakdown captures fringe axes per period."""

    def test_no_fringe_zero_breakdown(self) -> None:
        """With no fringe events, benefit_breakdown is all zeros."""
        result = calculate_period(_base())
        bb = result.benefit_breakdown
        assert bb.value == Decimal(0)
        assert bb.irpef_base == Decimal(0)
        assert bb.inps_base == Decimal(0)
        assert bb.employer_cost == Decimal(0)

    def test_exempt_fringe_value_nonzero_bases_zero(self) -> None:
        """Below-threshold fringe: value is set, irpef_base/inps_base are zero."""
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("100.00"))
        result = calculate_period(_req(evt))
        bb = result.benefit_breakdown
        assert bb.value == Decimal("100.00")
        assert bb.irpef_base == Decimal(0)
        assert bb.inps_base == Decimal(0)
        assert bb.employer_cost == Decimal("100.00")

    def test_taxable_fringe_all_axes_set(self) -> None:
        """Above-threshold fringe: value, irpef_base, inps_base are all nonzero."""
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("1100.00"))
        result = calculate_period(_req(evt))
        bb = result.benefit_breakdown
        assert bb.value == Decimal("1100.00")
        assert bb.irpef_base == Decimal("1100.00")
        assert bb.inps_base == Decimal("1100.00")
        assert bb.employer_cost == Decimal("1100.00")


class TestFringeYtdAccumulation:
    """fringe_ytd in closing_state tracks cumulative fringe across periods."""

    def test_fringe_ytd_zero_without_fringe(self) -> None:
        """No fringe events leaves fringe_ytd unchanged."""
        result = calculate_period(_base())
        assert result.closing_state.ytd.fringe.value == Decimal(0)

    def test_fringe_ytd_accumulates(self) -> None:
        """fringe_ytd closing equals opening.fringe_ytd + period fringe value."""
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("300.00"))
        opening = PeriodState(
            ytd=TaxYearState(fringe=FringeYtd(value=Decimal("500.00")))
        )
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=_MONTH),
            payment_date=date(_YEAR, _MONTH, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=opening,
            events=(evt,),
        )
        result = calculate_period(req)
        assert result.closing_state.ytd.fringe.value == Decimal("800.00")

    def test_fringe_taxed_ytd_zero_without_crossing(self) -> None:
        """No threshold crossing: fringe_taxed_ytd stays zero."""
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("100.00"))
        result = calculate_period(_req(evt))
        assert result.closing_state.ytd.fringe.taxed == Decimal(0)

    def test_fringe_taxed_ytd_set_on_crossing(self) -> None:
        """Threshold crossing: fringe_taxed_ytd equals full retroactive base."""
        # opening fringe_ytd=600 (untaxed) + 600 new = 1200 > 1000 → retroactive 1200
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("600.00"))
        opening = PeriodState(
            ytd=TaxYearState(fringe=FringeYtd(value=Decimal("600.00")))
        )
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=_MONTH),
            payment_date=date(_YEAR, _MONTH, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=opening,
            events=(evt,),
        )
        result = calculate_period(req)
        assert result.closing_state.ytd.fringe.taxed == Decimal("1200.00")

    def test_ytd_fringe_triggers_taxability(self) -> None:
        """Opening fringe_ytd near threshold makes a small new event taxable."""
        # threshold_standard=1000; after 900 YTD, 200 more = 1100 > 1000 → taxable
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("200.00"))
        opening = PeriodState(
            ytd=TaxYearState(fringe=FringeYtd(value=Decimal("900.00")))
        )
        req = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=_MONTH),
            payment_date=date(_YEAR, _MONTH, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=opening,
            events=(evt,),
        )
        result = calculate_period(req)
        base_result = calculate_period(_base())
        assert _inps_employee(result) > _inps_employee(base_result)


class TestHasDependentChildrenThreshold:
    """has_dependent_children selects the higher fringe threshold."""

    def test_children_threshold_higher(self) -> None:
        """Worker with dependent children: 1500 EUR fringe is exempt."""
        # threshold_with_children=2000 for 2026; 1500 < 2000 → exempt
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("1500.00"))
        req_no_children = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=_MONTH),
            payment_date=date(_YEAR, _MONTH, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            events=(evt,),
            has_dependent_children=False,
        )
        req_with_children = PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=_MONTH),
            payment_date=date(_YEAR, _MONTH, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            events=(evt,),
            has_dependent_children=True,
        )
        result_no_children = calculate_period(req_no_children)
        result_with_children = calculate_period(req_with_children)
        # Without children: 1500 > 1000 → taxable; with children: 1500 < 2000 → exempt
        assert _inps_employee(result_no_children) > _inps_employee(result_with_children)


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


class TestWelfareEventAccounting:
    """WelfareEvent posts to NON_CASH_BENEFITS; exempt from INPS, IRPEF and net."""

    def _welfare(self) -> WelfareEvent:
        return WelfareEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("200.00"))

    def test_welfare_in_non_cash_benefits(self) -> None:
        """Welfare benefit is posted to NON_CASH_BENEFITS, not CASH_EARNINGS."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._welfare()))
        assert _ncb(result) == Decimal("200.00")
        assert result.period_gross == base.period_gross

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

    def test_welfare_does_not_change_net(self) -> None:
        """Welfare (non-cash) does not affect cash net pay."""
        base = calculate_period(_base())
        result = calculate_period(_req(self._welfare()))
        assert result.period_net == base.period_net

    def test_reconcile_passes(self) -> None:
        """All reconciliation invariants hold for a welfare period."""
        result = calculate_period(_req(self._welfare()))
        r = reconcile(result, PeriodState.zero())
        assert r.ok, r.violations


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
