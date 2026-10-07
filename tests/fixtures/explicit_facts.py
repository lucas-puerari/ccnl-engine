"""Concia D2 requests of 2026 with every public fact stated explicitly.

The scenario of :mod:`tests.fixtures.normative_oracles.payslips.concia_d2_2026`
(an industrial tannery with 50 employees, level D2 hired on 1 January 2026,
resident in Alghero, 2025 income of 40,000 EUR), with each field a caller
could leave to its default given its value: hours, contribution history,
sector, the TFR kept in the company (not paid to the Fondo Tesoreria),
employer activity, residence, an empty family and the current-year
income, which states no other employment.  Its June run, opened with the
state May closed, has one blocker, ``rule_source_weak somma_esente``, so a
test that drops or changes one fact sees exactly the blockers that fact adds
or removes.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import (
    ContributionHistory,
    CurrentYearTaxFacts,
    EmployerActivity,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    PeriodState,
    PriorYearTaxFacts,
    WeeklyHours,
)
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine.events import WorkEvent

__all__ = [
    "CONCIA_D2",
    "EMPLOYER",
    "FACTS",
    "competence_year",
    "regular_run",
]

#: Concia D2, full time on a 40-hour week, enrolled after 1995.
CONCIA_D2 = Employment(
    ccnl_slug="concia-unic.json",
    level_code="D2",
    seniority=new_hire(),
    employment_period=EmploymentPeriod(date(2026, 1, 1)),
    weekly_hours=WeeklyHours(40),
    full_time_weekly_hours=WeeklyHours(40),
    contribution_history=ContributionHistory(date(2005, 3, 1)),
    sector=EmploymentSector.PRIVATE,
    tfr_treasury_fund=False,
)
EMPLOYER = EmployerProfile(headcount=Headcount(50), activity=EmployerActivity.OTHER)
#: Resident in Alghero (Sardegna), no dependant.
FACTS = PeriodFacts(
    regione="IT-88",
    comune_belfiore="A192",
    family_composition=FamilyComposition(),
)
_PRIOR = PriorYearTaxFacts(employment_income=Decimal(40_000))
_CURRENT = CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1))


def regular_run(
    month: int = 6,
    *,
    employment: Employment = CONCIA_D2,
    facts: PeriodFacts = FACTS,
    events: tuple[WorkEvent, ...] = (),
    opening_state: PeriodState | None = None,
) -> PeriodInput:
    """Return the request of the regular run of ``month`` 2026, paid on the 28th.

    ``opening_state`` left to ``None`` keeps the default of
    :class:`~ccnl_engine.PeriodInput`, the zero state, the one fact this
    builder does not state: it is the fact of the January run only, and a
    later month without the state of the months before has a
    ``missing_fact opening_state`` blocker.

    Returns:
        The request with every other fact explicit.
    """
    request = PeriodInput(
        run=PayrollRun.regular(2026, month),
        payment_date=date(2026, month, 28),
        employment=employment,
        employer=EMPLOYER,
        facts=replace(facts, events=events),
        prior_year=_PRIOR,
        current_year=_CURRENT,
    )
    if opening_state is None:
        return request
    return replace(request, opening_state=opening_state)


def competence_year(
    *,
    employment: Employment = CONCIA_D2,
    periods: dict[int, PeriodFacts] | None = None,
) -> CompetenceYearPlan:
    """Return the plan of the 2026 competence year with every fact explicit.

    Returns:
        The plan; ``periods`` replaces the facts of the months it lists.
    """
    return CompetenceYearPlan(
        year=2026,
        employment=employment,
        employer=EMPLOYER,
        default_facts=FACTS,
        periods=periods or {},
        prior_year=_PRIOR,
        current_year=_CURRENT,
    )
