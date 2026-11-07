"""Hand oracle: the ferie of a live-in domestic worker at the end of the job.

CCNL lavoro domestico of 28 October 2025: 26 days of ferie a year (Art. 17
c. 1), a twelfth for each month of service (c. 9), a month of 15 days or
more counted whole (Chiarimenti a verbale, point 4), a day of ferie paid
1/26 of the monthly pay (c. 6).

Level B convivente, 983.16 a month, hired 1 January 2026, 5 days of ferie
taken in July:

- ended 15 October: 10 months, 26 x 10 / 12 = 21.6667 days, 16.6667 left,
  16.6667 x 983.16 / 26 = 630.23;
- ended 14 October: 9 months, 26 x 9 / 12 = 19.5 days, 14.5 left,
  14.5 x 983.16 / 26 = 548.30.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
)
from ccnl_engine.events import LeaveBucket, LeaveTakenEvent
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_HIRED = date(2026, 1, 1)
_FACTS = PeriodFacts(
    regione="IT-25",
    comune_belfiore="A005",
    family_composition=FamilyComposition(),
    contributable_hours=ContributableHours(Decimal(173)),
)


@pytest.mark.parametrize(
    ("ended_on", "accrued", "paid"),
    [
        (date(2026, 10, 15), Decimal(26) * 10 / 12, Decimal("630.23")),
        (date(2026, 10, 14), Decimal("19.5"), Decimal("548.30")),
    ],
    ids=["fifteen-days-count", "fourteen-do-not"],
)
def test_the_ferie_left_are_paid_at_a_twenty_sixth(
    ended_on: date, accrued: Decimal, paid: Decimal
) -> None:
    """The October fraction counts from its 15th day; the rest is paid."""
    employment = Employment(
        ccnl_id="lavoro-domestico-convivente",
        level_code="B",
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(_HIRED, ended_on),
        seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
        roles=frozenset(),
        sector=EmploymentSector.PRIVATE,
        pension_fund=NoPensionFund(),
        weekly_hours=WeeklyHours(Decimal(54)),
    )
    taken = (LeaveTakenEvent(date(2026, 7, 6), LeaveBucket.FERIE, Decimal(5)),)
    year = PayrollEngine.bundled().calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=employment,
            employer=EmployerProfile(headcount=Headcount(1)),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(15000)),
            default_facts=_FACTS,
            periods={7: replace(_FACTS, events=taken)},
        )
    )
    october = next(
        r
        for r in year.period_results
        if r.run is not None and str(r.run.run_id) == "2026-10-regular"
    )

    ((bucket, got, residual),) = [
        (b.bucket, b.accrued, b.residual) for b in october.leave_balances
    ]
    assert (bucket, got.quantize(Decimal("0.0001")), residual) == (
        LeaveBucket.FERIE,
        accrued.quantize(Decimal("0.0001")),
        Decimal(0),
    )
    assert [
        i.amount for i in october.pay_items if i.kind == "leave_settlement_item"
    ] == [paid]
