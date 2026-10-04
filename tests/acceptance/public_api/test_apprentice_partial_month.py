"""A part-time apprentice hired mid-month: each scaling rounds in turn.

Metalmeccanico Federmeccanica C3 operaio, March 2026: monthly minimo
2,158.26, no fixed allowance, daily quota one twenty-sixth
(``work_rules.absence_rules``: ``by_26``) on the Mondays to Saturdays of
the employment, sickness integrated to 100% from the first day.  The
apprentice is on track ``professionalizzante_36`` at month 0 (85%), works
20 of 40 weekly hours and is hired on Monday 16 March: 16-21, 23-28 and
30-31 March are 14 payable days.

The pay chain applies the apprenticeship, then the part-time ratio, then
the proration, rounding half up to the cent after each step:

1. apprenticeship: 2,158.26 x 0.85 = 1,834.521 -> 1,834.52;
2. part-time: 1,834.52 x 20 / 40 = 917.26;
3. proration: 917.26 x 14 / 26 = 493.909... -> 493.91.

Every amount is computed by hand from the bundle figures, never read from
the engine output.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    Apprentice,
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    WeeklyHours,
    WorkerCategory,
)
from tests.fixtures.seniority import new_hire
from tests.fixtures.sickness_episode import sickness_episode

_ENGINE = PayrollEngine.bundled()
_HIRED = date(2026, 3, 16)


def _run(facts: PeriodFacts | None = None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                category=WorkerCategory.OPERAIO,
                contract_type=Apprentice(
                    months_elapsed=0, track="professionalizzante_36"
                ),
                seniority=new_hire(),
                employment_period=EmploymentPeriod(_HIRED),
                weekly_hours=WeeklyHours(20),
                full_time_weekly_hours=WeeklyHours(40),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=facts or PeriodFacts(),
        )
    )


def _base_salary(result: PeriodResult) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


def test_apprentice_hired_mid_month_rounds_each_step() -> None:
    """Apprenticeship, part-time, proration: 493.91."""
    result = _run()
    assert _base_salary(result) == Decimal("493.91")
    assert result.period_gross == Decimal("493.91")


def test_sick_apprentice_in_the_hire_month_is_paid_on_the_scaled_quota() -> None:
    """Sick Monday 23 to Friday 27 March: the quota is the scaled month's.

    The daily quota is one twenty-sixth of 917.26, the apprentice and
    part-time chain of a full month:

    - days 1-3 (23-25 March), carenza paid by the employer:
      917.26 x 3 / 26 = 105.837... -> 105.84;
    - days 4-5 (26-27 March), INPS at 50%: 917.26 x 2 / 26 = 70.558... ->
      70.56, of which INPS 35.28 and the employer 35.28;
    - absence deduction: 105.84 + 70.56 = 176.40.

    The prorated pay of the month is still 493.91.
    """
    episode = sickness_episode("2026-03-23", date(2026, 3, 23), date(2026, 3, 27))
    result = _run(PeriodFacts(events=(episode,)))
    amounts: dict[str, Decimal] = {}
    for item in result.pay_items:
        if "_evt" in item.item_id:
            amounts[item.kind] = amounts.get(item.kind, Decimal(0)) + item.amount
    assert amounts == {
        "sickness_inps_item": Decimal("35.28"),
        "sickness_item": Decimal("141.12"),
        "absence_deduction": Decimal("176.40"),
    }
    assert _base_salary(result) == Decimal("493.91")
