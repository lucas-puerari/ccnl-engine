"""Every level of every bundled CCNL computes a regular run with sane totals.

A smoke check over the whole bundle, asserting invariants only: no expected
amount is frozen here, because values produced by the engine itself detect
no systematic error. Amounts are owned by the reference cases, the oracle
tests and the per-contract loader tests.

The same scan checks the minimum INPS base of every level
(:mod:`tests.knowledge.ccnl_engine.contribution.oracles`): a full month
of a full-time worker is contributed on at least 26 daily floors, unless
art. 7 c. 5 D.L. 463/1983 excludes the worker or a blocker on the INPS
amounts says the minimum is undetermined.
"""

from __future__ import annotations

from dataclasses import replace
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
from ccnl_engine.agreement.facade import CCNL, TaxSector
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import (
    AgriculturalZone,
    ContributableHours,
    CurrentYearTaxFacts,
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    PublicEndOfService,
    WeeklyHours,
)
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.integration.ccnl_engine.surtax.residence.builders import resident
from tests.knowledge.ccnl_engine.contribution.oracles import (
    FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR,
    contribution_base,
)
from tests.knowledge.ccnl_engine.seniority.builders import (
    new_hire,
    pricing_category,
)

_ENGINE = PayrollEngine.bundled()
_SLUGS = [info.ccnl_id for info in PayrollEngine.bundled().list_contracts()]
#: Domestic contracts need declared weekly and contributable hours for INPS:
#: a full-time week, 54 hours for conviventi and 40 for non conviventi (the
#: weeks the bundle derives the monthly minimum from), the 30-hour ceiling
#: of the reduced-hours conviventi.
_DOMESTIC = {
    "lavoro-domestico-convivente": WeeklyHours(Decimal(54)),
    "lavoro-domestico-convivente-orario-ridotto": WeeklyHours(Decimal(30)),
    "lavoro-domestico-non-convivente": WeeklyHours(Decimal(40)),
}
_DOMESTIC_FACTS = PeriodFacts(contributable_hours=ContributableHours(Decimal(173)))
#: Ordinary hours of a full month of a worker paid by the hour.
_FULL_MONTH_HOURS = ContributableHours(Decimal(173))
_COMPUTED = frozenset({CalculationStatus.FINAL, CalculationStatus.PROVISIONAL})
#: Hired on 1 September with no other employment in 2026: the September run
#: is the first of the employment, so the zero opening state is the fact.
_HIRED = EmploymentPeriod(date(2026, 9, 1))
_ONLY_EMPLOYMENT = CurrentYearTaxFacts.employment_only(2026, date(2026, 9, 1))
#: Issue of a run whose minimum INPS base the bundle cannot fix.
_MINIMUM_UNDETERMINED = "inps_minimum_base_undetermined"
#: Incomplete issues the scan accepts: the open minimum base, and the
#: contractual fund contribution of a category the scan does not state.
_ACCEPTED = frozenset({
    _MINIMUM_UNDETERMINED,
    "contractual_fund_category_unknown",
    "contractual_fund_not_computed",
    "contractual_fund_hours_unknown",
})
_INPS = frozenset({"inps_employee", "inps_employer"})


def _minimum_held(result: PeriodResult) -> bool:
    """Whether the INPS base respects the minimum, or says it cannot.

    Returns:
        True for a base at or above 26 daily floors to the whole euro
        (INPS circ. 208/2001), a worker
        art. 7 c. 5 excludes, or an undetermined minimum that blocks both
        INPS amounts.
    """
    (decision,) = (d for d in result.decisions if d.capability == "inps_employee")
    if decision.inputs.get("minimum_base_reason") == "category_excluded":
        return True
    if any(i.code == _MINIMUM_UNDETERMINED for i in result.issues):
        causes = {BlockerCode.MISSING_FACT, BlockerCode.CALCULATION_ISSUE}
        return {b.feature for b in result.blockers if b.code in causes} >= _INPS
    base = decision.inputs["base"]
    floor = contribution_base(FULL_TIME_MONTHLY_CONTRIBUTION_FLOOR)
    return isinstance(base, Decimal) and base >= floor


def _computed(result: PeriodResult) -> bool:
    """Whether the run computed, or only an accepted issue is open.

    Returns:
        True for a final or provisional result, or an incomplete one whose
        incomplete issues are all accepted (:data:`_ACCEPTED`).
    """
    if result.assurance.calculation in _COMPUTED:
        return True
    return all(
        i.code in _ACCEPTED
        for i in result.issues
        if i.status is CalculationStatus.INCOMPLETE
    )


def _public_regime(ccnl: CCNL) -> PublicEndOfService | None:
    """Return the regime of a public employee hired in 2026: the TFR at INPS.

    Returns:
        ``tfr_inps`` on a CCNL of the public administrations, else ``None``.
    """
    public = ccnl.meta.tax_sector is TaxSector.PUBBLICA_AMMINISTRAZIONE
    return PublicEndOfService.TFR_INPS if public else None


def _facts(slug: str, ccnl: CCNL) -> PeriodFacts:
    """Return the facts of the scan: a full month of hours where they are paid.

    Returns:
        The hours of the domestic contracts; the resident facts with 173
        ordinary hours worked on a CCNL that pays by the hour.
    """
    if slug in _DOMESTIC:
        return _DOMESTIC_FACTS
    if ccnl.parameters.hourly_pay is not None:
        return replace(resident(), ordinary_hours_worked=_FULL_MONTH_HOURS)
    return resident()


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
                    ccnl_id=slug,
                    level_code=level.code,
                    weekly_hours=_DOMESTIC.get(slug),
                    full_time_weekly_hours=_DOMESTIC.get(slug),
                    seniority=new_hire(),
                    category=pricing_category(increments, level.code),
                    employment_period=_HIRED,
                    roles=frozenset(),
                    pension_fund=NoPensionFund(),
                    contract_type=Permanent(),
                    public_end_of_service=_public_regime(ccnl),
                ),
                employer=EmployerProfile(
                    headcount=Headcount(50),
                    provincial_pay_element=False,
                    second_level_premium=False,
                    cigs_indotto=False,
                    agricultural_zone=AgriculturalZone.ORDINARY,
                    public_life_insurance=False if _public_regime(ccnl) else None,
                    inps_sector=ccnl.meta.tax_sector,
                    contractual_funds=frozenset(),
                ),
                facts=_facts(slug, ccnl),
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
