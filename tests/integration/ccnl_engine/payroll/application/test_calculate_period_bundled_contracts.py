"""Every level of every bundled CCNL computes a regular run with sane totals.

A smoke check over the whole bundle, asserting invariants only: no expected
amount is frozen here, because values produced by the engine itself detect
no systematic error. Amounts are owned by the reference cases, the oracle
tests and the per-contract loader tests.
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
)
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.inputs import (
    ContributableHours,
    CurrentYearTaxFacts,
    EmploymentPeriod,
    WeeklyHours,
)
from ccnl_engine.results import CalculationStatus
from tests.fixtures.residence import resident
from tests.fixtures.seniority import new_hire, pricing_category

_ENGINE = PayrollEngine.bundled()
_SLUGS = [f"{info.ccnl_id}.json" for info in PayrollEngine.list_contracts()]
#: Domestic contracts need declared weekly and contributable hours for INPS.
_DOMESTIC = frozenset({
    "lavoro-domestico-convivente.json",
    "lavoro-domestico-non-convivente.json",
})
_DOMESTIC_FACTS = PeriodFacts(contributable_hours=ContributableHours(Decimal(173)))
_COMPUTED = frozenset({CalculationStatus.FINAL, CalculationStatus.PROVISIONAL})
#: Hired on 1 September with no other employment in 2026: the September run
#: is the first of the employment, so the zero opening state is the fact.
_HIRED = EmploymentPeriod(date(2026, 9, 1))
_ONLY_EMPLOYMENT = CurrentYearTaxFacts.employment_only(2026, date(2026, 9, 1))


def test_bundle_lists_contracts() -> None:
    """The parametrization below runs on the real bundle, not an empty list."""
    assert len(_SLUGS) > 100


@pytest.mark.parametrize("slug", _SLUGS)
def test_every_level_computes_sane_totals(slug: str) -> None:
    """Gross and net are positive, contributions non-negative, cost covers gross.

    Net may exceed gross when tax credits such as the trattamento integrativo
    are paid, so only its sign is checked.
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
                    weekly_hours=WeeklyHours(40) if slug in _DOMESTIC else None,
                    seniority=new_hire(),
                    category=pricing_category(increments, level.code),
                    employment_period=_HIRED,
                ),
                employer=EmployerProfile(headcount=Headcount(50)),
                facts=_DOMESTIC_FACTS if slug in _DOMESTIC else resident(),
                current_year=_ONLY_EMPLOYMENT,
            )
        )
        gross = result.period_gross
        if not (
            result.assurance.calculation in _COMPUTED
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
