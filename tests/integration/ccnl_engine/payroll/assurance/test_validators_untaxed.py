"""Invariant of a household employer: no tax posted, net not above gross."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.assurance.types import RunFacts
from ccnl_engine.payroll.assurance.validators_untaxed import (
    check_non_agent_untaxed,
)
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.employment.inputs_fact import (
    ContributableHours,
    WeeklyHours,
)
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState

_INVARIANT = "non_agent_untaxed"
_NOT_AGENT = RunFacts(withholding_agent=False)


def _request(ccnl_slug: str, level_code: str) -> PeriodCalculationRequest:
    domestic = ccnl_slug.startswith("lavoro-domestico")
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(1)),
        period_id=PeriodId(year=2026, month=9),
        payment_date=date(2026, 9, 28),
        ccnl_slug=ccnl_slug,
        level_code=level_code,
        opening_state=PeriodState.zero(),
        weekly_hours=WeeklyHours(40) if domestic else None,
        contributable_hours=(ContributableHours(Decimal(173)) if domestic else None),
    )


def test_domestic_run_holds() -> None:
    """A domestic run posts no tax and pays gross less contributions."""
    result = calculate_period(_request("lavoro-domestico-convivente.json", "A"))

    assert check_non_agent_untaxed(result, _NOT_AGENT) == []


def test_withholding_agent_is_not_checked() -> None:
    """The invariant does not apply to an employer that withholds tax."""
    result = calculate_period(_request("commercio-confcommercio.json", "4"))

    assert check_non_agent_untaxed(result, RunFacts()) == []


def test_tax_posted_by_a_non_agent_is_reported() -> None:
    """IRPEF posted for an employer that is not a withholding agent fails."""
    result = calculate_period(_request("commercio-confcommercio.json", "4"))

    violations = check_non_agent_untaxed(result, _NOT_AGENT)

    assert {v.invariant_id for v in violations} == {_INVARIANT}
    assert any("ordinary_tax" in v.message for v in violations)


def test_net_above_gross_is_reported() -> None:
    """A net one euro above the gross of a domestic run fails."""
    result = calculate_period(_request("lavoro-domestico-convivente.json", "A"))
    bad = replace(result, period_net=result.period_gross + 1)

    (violation,) = check_non_agent_untaxed(bad, _NOT_AGENT)

    assert violation.invariant_id == _INVARIANT
    assert violation.actual == result.period_gross + 1
