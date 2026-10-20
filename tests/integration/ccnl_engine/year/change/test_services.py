"""A competence year with a change of level or hours: Commercio, 4th level.

Hired on 1 January 2025, 40 of 40 hours, 10 employees.  Monthly pay of the
4th level (paga base, contingenza, terzo elemento) 1,783.75 EUR to
October, 1,818.75 from 1 November 2026; the 3rd level 1,983.91 and
2,024.38.  The quattordicesima is paid on 1 July and accrues July 2025 to
June 2026, the tredicesima in December over the calendar year.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
)
from ccnl_engine.inputs import (
    EmploymentChange,
    EmploymentPeriod,
    FamilyComposition,
    NoPensionFund,
    PeriodState,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_HIRED = date(2025, 1, 1)
_EMPLOYMENT = Employment(
    ccnl_id="commercio-confcommercio",
    level_code="4",
    contract_type=Permanent(),
    employment_period=EmploymentPeriod(_HIRED, None),
    seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
    pension_fund=NoPensionFund(),
    weekly_hours=WeeklyHours(Decimal(40)),
    full_time_weekly_hours=WeeklyHours(Decimal(40)),
    tfr_treasury_fund=False,
)


def _year(
    *changes: EmploymentChange, employment: Employment = _EMPLOYMENT
) -> CompetenceYearResult:
    return PayrollEngine.bundled().calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=employment,
            employer=EmployerProfile(
                headcount=Headcount(10), provincial_pay_element=False
            ),
            employment_changes=changes,
            default_facts=PeriodFacts(family_composition=FamilyComposition()),
            opening_state=PeriodState.zero(),
        )
    )


def _gross(year: CompetenceYearResult) -> dict[str, Decimal]:
    # Keyed by payment date: the 14th is paid on 1 July, the 13th on 24 December.
    return {r.payment_date.isoformat(): r.period_gross for r in year.period_results}


def test_a_promotion_prices_the_months_from_its_date() -> None:
    """3rd level from July: June at the 4th, July and the tredicesima at the 3rd."""
    gross = _gross(_year(EmploymentChange(date(2026, 7, 1), level_code="3")))

    assert gross["2026-06-28"] == Decimal("1783.75")
    assert gross["2026-07-28"] == Decimal("1983.91")
    assert gross["2026-07-01"] == Decimal("1783.75")
    assert gross["2026-12-24"] == Decimal("2024.38")


def test_part_time_from_july_splits_the_tredicesima() -> None:
    """20 of 40 hours from July.

    The quattordicesima (accrued July 2025 to June 2026 at full time) stays
    whole; the tredicesima pays six twelfths at full time and six at part
    time of the December pay: (6 x 1 + 6 x 0.5) / 12 x 1,818.75 = 1,364.06,
    1,364.08 once each element of the part-time pay is rounded to the cent
    before the rateo.
    """
    gross = _gross(
        _year(EmploymentChange(date(2026, 7, 1), weekly_hours=WeeklyHours(Decimal(20))))
    )

    assert gross["2026-07-28"] == Decimal("891.88")
    assert gross["2026-07-01"] == Decimal("1783.75")
    assert gross["2026-12-24"] == Decimal("1364.08")


def test_a_termination_settles_each_stretch_at_its_hours() -> None:
    """Ended on 30 September, part time from July.

    The tredicesima settled on the September run holds six months at full
    time and three at part time of the 1,783.75 EUR pay: 6/12 x 1,783.75 +
    3/12 x 891.88 = 1,114.85, against 668.91 for nine months all at part
    time.
    """
    ending = replace(
        _EMPLOYMENT, employment_period=EmploymentPeriod(_HIRED, date(2026, 9, 30))
    )
    plain = _year(employment=replace(ending, weekly_hours=WeeklyHours(Decimal(20))))
    split = _year(
        EmploymentChange(date(2026, 7, 1), weekly_hours=WeeklyHours(Decimal(20))),
        employment=ending,
    )

    def settled(year: CompetenceYearResult) -> Decimal:
        (september,) = [
            r for r in year.period_results if r.payment_date == date(2026, 9, 28)
        ]
        return sum(
            (i.amount for i in september.pay_items if "thirteenth" in i.item_id),
            Decimal(0),
        )

    assert settled(plain) == Decimal("668.91")
    assert settled(split) == Decimal("1114.85")
