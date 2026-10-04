"""Integration tests for fringe and welfare events in the period-first engine.

Verifies non-cash benefit postings, the benefit breakdown, the fringe YTD
accumulation and the dependent-children threshold.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.events import FringeEvent, WelfareEvent
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import FringeYtd
from tests.fixtures.period_requests import account_total, period_request

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
        assert result.closing_state.cash.fringe.value == Decimal(0)

    def test_fringe_ytd_accumulates(self) -> None:
        """fringe_ytd closing equals opening.fringe_ytd + period fringe value."""
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("300.00"))
        opening = PeriodState(
            cash=TaxCashState(fringe=FringeYtd(value=Decimal("500.00")))
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
        assert result.closing_state.cash.fringe.value == Decimal("800.00")

    def test_fringe_taxed_ytd_zero_without_crossing(self) -> None:
        """No threshold crossing: fringe_taxed_ytd stays zero."""
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("100.00"))
        result = calculate_period(_req(evt))
        assert result.closing_state.cash.fringe.taxed == Decimal(0)

    def test_fringe_taxed_ytd_set_on_crossing(self) -> None:
        """Threshold crossing: fringe_taxed_ytd equals full retroactive base."""
        # opening fringe_ytd=600 (untaxed) + 600 new = 1200 > 1000 → retroactive 1200
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("600.00"))
        opening = PeriodState(
            cash=TaxCashState(fringe=FringeYtd(value=Decimal("600.00")))
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
        assert result.closing_state.cash.fringe.taxed == Decimal("1200.00")

    def test_ytd_fringe_triggers_taxability(self) -> None:
        """Opening fringe_ytd near threshold makes a small new event taxable."""
        # threshold_standard=1000; after 900 YTD, 200 more = 1100 > 1000 → taxable
        evt = FringeEvent(event_date=date(_YEAR, _MONTH, 1), amount=Decimal("200.00"))
        opening = PeriodState(
            cash=TaxCashState(fringe=FringeYtd(value=Decimal("900.00")))
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


# ---------------------------------------------------------------------------
# welfare da 100 → cash earnings e lordo aumentano di 100
# ---------------------------------------------------------------------------


def test_welfare_does_not_increase_cash_earnings() -> None:
    """A WelfareEvent must not increase period_gross or CASH_EARNINGS.

    After the fix calculate_period with WelfareEvent(100) must produce the
    same period_gross and CASH_EARNINGS as a calculation with no events.
    Currently welfare increases both by 100.
    """
    welfare = WelfareEvent(event_date=date(_YEAR, 1, 15), amount=Decimal("100.00"))
    result_with = calculate_period(period_request(events=(welfare,)))
    result_without = calculate_period(period_request())

    assert result_with.period_gross == result_without.period_gross, (
        f"period_gross with welfare ({result_with.period_gross}) must equal "
        f"period_gross without ({result_without.period_gross})"
    )

    cash_with = account_total(result_with, AccountKind.CASH_EARNINGS)
    cash_without = account_total(result_without, AccountKind.CASH_EARNINGS)
    assert cash_with == cash_without, (
        f"CASH_EARNINGS with welfare ({cash_with}) must equal "
        f"CASH_EARNINGS without ({cash_without})"
    )
