"""Every level of every bundled CCNL computes a regular run with sane totals.

A smoke check over the whole bundle, asserting invariants only: no expected
amount is frozen here, because values produced by the engine itself detect
no systematic error. Amounts are owned by the reference cases, the oracle
tests and the per-contract loader tests.

The same scan checks the minimum INPS base of every level
(:mod:`tests.fixtures.normative_oracles.contributions_2026`): a full month
of a full-time worker is contributed on at least 26 daily floors, unless
art. 7 c. 5 D.L. 463/1983 excludes the worker or a blocker on the INPS
amounts says the minimum is undetermined.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.inputs import (
    ContributableHours,
    CurrentYearTaxFacts,
    EmploymentPeriod,
    NoPensionFund,
    WeeklyHours,
)
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.fixtures.normative_oracles.contributions_2026 import (
    FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR,
)
from tests.fixtures.residence import resident
from tests.fixtures.seniority import new_hire, pricing_category

_ENGINE = PayrollEngine.bundled()
_SLUGS = [f"{info.ccnl_id}.json" for info in PayrollEngine.list_contracts()]
#: Domestic contracts need declared weekly and contributable hours for INPS:
#: a full-time week, 54 hours for conviventi and 40 for non conviventi (the
#: weeks the bundle derives the monthly minimum from).
_DOMESTIC = {
    "lavoro-domestico-convivente.json": WeeklyHours(54),
    "lavoro-domestico-non-convivente.json": WeeklyHours(40),
}
_DOMESTIC_FACTS = PeriodFacts(contributable_hours=ContributableHours(Decimal(173)))
_COMPUTED = frozenset({CalculationStatus.FINAL, CalculationStatus.PROVISIONAL})
#: Hired on 1 September with no other employment in 2026: the September run
#: is the first of the employment, so the zero opening state is the fact.
_HIRED = EmploymentPeriod(date(2026, 9, 1))
_ONLY_EMPLOYMENT = CurrentYearTaxFacts.employment_only(2026, date(2026, 9, 1))
#: Issue of a run whose minimum INPS base the bundle cannot fix.
_MINIMUM_UNDETERMINED = "inps_minimum_base_undetermined"
_INPS = frozenset({"inps_employee", "inps_employer"})


def _minimum_held(result: PeriodResult) -> bool:
    """Whether the INPS base respects the minimum, or says it cannot.

    Returns:
        True for a base at or above 26 daily floors, a worker
        art. 7 c. 5 excludes, or an undetermined minimum that blocks both
        INPS amounts.
    """
    (decision,) = (d for d in result.decisions if d.capability == "inps_employee")
    if decision.inputs.get("minimum_base_reason") == "category_excluded":
        return True
    if any(i.code == _MINIMUM_UNDETERMINED for i in result.issues):
        issues = BlockerCode.CALCULATION_ISSUE
        return {b.feature for b in result.blockers if b.code is issues} >= _INPS
    base = decision.inputs["base"]
    return isinstance(base, Decimal) and base >= FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR


def _computed(result: PeriodResult) -> bool:
    """Whether the run computed, or only its minimum INPS base is open.

    Returns:
        True for a final or provisional result, or an incomplete one whose
        incomplete issues are all the undetermined minimum base.
    """
    if result.assurance.calculation in _COMPUTED:
        return True
    return all(
        i.code == _MINIMUM_UNDETERMINED
        for i in result.issues
        if i.status is CalculationStatus.INCOMPLETE
    )


def test_bundle_lists_contracts() -> None:
    """The parametrization below runs on the real bundle, not an empty list."""
    assert len(_SLUGS) > 100


@pytest.mark.parametrize("slug", _SLUGS)
def test_every_level_computes_sane_totals(slug: str) -> None:
    """Gross and net are positive, contributions non-negative, cost covers gross.

    Net may exceed gross when tax credits such as the trattamento integrativo
    are paid, so only its sign is checked.  The INPS base holds the minimum
    of the sector or a blocker says it cannot be fixed.
    """
    failures: list[str] = []
    ccnl = load_ccnl(slug)
    increments = ccnl.parameters.seniority_increments
    for level in ccnl.levels:
        result = _ENGINE.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(year=2026, month=9),
                payment_date=date(2026, 9, 27),
                employment=Employment(
                    ccnl_slug=slug,
                    level_code=level.code,
                    weekly_hours=_DOMESTIC.get(slug),
                    full_time_weekly_hours=_DOMESTIC.get(slug),
                    seniority=new_hire(),
                    category=pricing_category(increments, level.code),
                    employment_period=_HIRED,
                    roles=frozenset(),
                    pension_fund=NoPensionFund(),
                ),
                employer=EmployerProfile(headcount=Headcount(50)),
                facts=_DOMESTIC_FACTS if slug in _DOMESTIC else resident(),
                current_year=_ONLY_EMPLOYMENT,
            )
        )
        gross = result.period_gross
        if not (
            _computed(result)
            and (slug in _DOMESTIC or _minimum_held(result))
            and gross > 0
            and result.period_net > 0
            and result.contribution_breakdown.employee >= 0
            and result.period_employer_cost >= gross
        ):
            failures.append(
                f"{level.code}: status={result.assurance.calculation} gross={gross} "
                f"net={result.period_net} cost={result.period_employer_cost}"
            )
    assert failures == []
