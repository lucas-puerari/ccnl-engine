"""Employment facts must shape the payroll or be rejected when impossible."""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollYearRequest,
    WorkerCategory,
)
from ccnl_engine.payroll.domain.run import RunKind
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    DOMESTIC,
    ENGINE,
    POSTAL_FISE,
    regular_period,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.payroll.application.calculate_year import (
        YearCalculationResult,
    )

pytestmark = pytest.mark.legal_scenario


def _three_month_year() -> YearCalculationResult:
    return ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug=COMMERCIO,
            level_code="4",
            employment_facts=EmploymentFacts(
                started_on=date(2026, 7, 1), ended_on=date(2026, 9, 30)
            ),
        )
    )


def test_three_month_employment_has_no_runs_outside_the_period() -> None:
    """Commercio L4 hired 1 July and terminated 30 September 2026.

    Expected: runs only for July, August and September; a worker who is not
    employed cannot be paid a monthly salary (art. 2094 c.c.).  Both extra
    months are paid outside the employment (June and December), so neither
    has its own run.
    """
    year = _three_month_year()
    runs = [(r.run.month, r.run.run_kind) for r in year.period_results if r.run]

    assert runs == [(month, RunKind.REGULAR) for month in (7, 8, 9)]


def test_three_month_employment_pays_the_accrued_extra_months() -> None:
    """The same employment accrues 3/12 of tredicesima and quattordicesima.

    Commercio L4 in September 2026 (bundled table): base 1,257.46,
    contingenza/EDR 524.22, terzo elemento 2.07, monthly gross 1,783.75.
    Every component is paid in both extra months (no ``months_per_year``).

    - Tredicesima: window January to December 2026, clipped to the hire on
      1 July and closed on 30 September: July, August, September, 3/12.
    - Quattordicesima: its next payment is June 2027, window July 2026 to
      June 2027, clipped likewise: 3/12.
    - A rateo is each component times 3/12 rounded to cents: 314.37 +
      131.06 + 0.52 = 445.95.

    Expected: both ratei are paid on the September payslip, so the year
    grosses 3 * 1,783.75 + 2 * 445.95 = 6,243.15, and September 2,675.65.

    Observed on 26 September 2026 before the fix: 5,351.25, only the three
    regular months.
    """
    year = _three_month_year()

    assert year.annual_gross == Decimal("6243.15")
    assert year.period_results[-1].period_gross == Decimal("2675.65")


def test_hire_in_march_accrues_a_third_of_the_quattordicesima() -> None:
    """Commercio L4 hired 15 March 2026, open-ended.

    March has 17 employed days, at least 15, so it counts as a month.

    - Quattordicesima paid in June: window July 2025 to June 2026, clipped
      to the hire: March to June, 4/12.  On 1,783.75: 1,257.46 / 3 =
      419.15, 524.22 / 3 = 174.74, 2.07 / 3 = 0.69, total 594.58.
    - Tredicesima paid in December: March to December, 10/12 of the
      December pay 1,818.75 (base 1,292.46 from November): 1,077.05 +
      436.85 + 1.73 = 1,515.63.

    Observed before the fix: the quattordicesima paid 10/12, counting the
    six months before January as accrued.
    """
    year = ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug=COMMERCIO,
            level_code="4",
            employment_facts=EmploymentFacts(started_on=date(2026, 3, 15)),
        )
    )
    extra = {
        r.run.run_kind: r.period_gross
        for r in year.period_results
        if r.run is not None and r.run.run_kind is not RunKind.REGULAR
    }

    assert extra == {
        RunKind.FOURTEENTH: Decimal("594.58"),
        RunKind.THIRTEENTH: Decimal("1515.63"),
    }


@pytest.mark.parametrize("hire_month", range(1, 11))
def test_three_month_employment_never_pays_a_full_year(hire_month: int) -> None:
    """Any three whole months of Commercio L4 pay three months plus 2 * 3/12.

    Expected: the extra months together pay at most 3/12 of two monthly
    pays, whichever window they fall in (a quattordicesima split across
    the June run and the termination run included), so the year never
    approaches the fourteen monthly pays of a full year.
    """
    last_month = hire_month + 2
    last_day = calendar.monthrange(2026, last_month)[1]
    year = ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug=COMMERCIO,
            level_code="4",
            employment_facts=EmploymentFacts(
                started_on=date(2026, hire_month, 1),
                ended_on=date(2026, last_month, last_day),
            ),
        )
    )
    regular_runs = [
        r for r in year.period_results if r.run and r.run.run_kind is RunKind.REGULAR
    ]
    monthly = max(
        r.period_gross
        - sum(
            (i.amount for i in r.pay_items if i.kind == "extra_month_earning"),
            Decimal(0),
        )
        for r in regular_runs
    )

    assert len(regular_runs) == 3
    # Each rateo rounds its three components to cents: at most 0.03 above.
    assert year.annual_gross <= monthly * Decimal("3.5") + Decimal("0.06")
    assert year.annual_gross > monthly * 3


# Servizi Postali in Appalto FISE, level 2, base 1,650.74 + allowances 63.33
# and 10.33 = 1,724.40 EUR without seniority.  CCNL table "Scatti di
# anzianita" (bundled source ccnl-servizi-postali-versione-stampa-250624,
# extraction marked unverified): operaio first increment after 24 months,
# at most one, 56.66 EUR; impiegato first increment after 48 months, then
# every 24, 62.62 EUR.  At 60 months each category has exactly one increment.
_FISE_BASE_GROSS = Decimal("1724.40")


@pytest.mark.parametrize(
    ("category", "increment"),
    [
        (WorkerCategory.OPERAIO, Decimal("56.66")),
        (WorkerCategory.IMPIEGATO, Decimal("62.62")),
    ],
)
def test_worker_category_selects_the_seniority_increment(
    category: WorkerCategory, increment: Decimal
) -> None:
    """Gross is base plus one category-specific increment at 60 months.

    Expected: 1,781.06 for operaio and 1,787.02 for impiegato.
    """
    result = regular_period(
        ccnl_slug=POSTAL_FISE,
        level_code="2",
        facts=EmploymentFacts(seniority_months=60, category=category),
    )

    assert result.period_gross == _FISE_BASE_GROSS + increment


def test_missing_required_worker_category_is_rejected() -> None:
    """FISE increments exist only per category, so no category cannot be priced."""
    with pytest.raises(ValueError, match="category"):
        regular_period(
            ccnl_slug=POSTAL_FISE,
            level_code="2",
            facts=EmploymentFacts(seniority_months=60, category=None),
        )


def _negative_headcount() -> None:
    regular_period(employer=Employer(headcount=Headcount(-1)))


def _negative_seniority() -> None:
    regular_period(facts=EmploymentFacts(seniority_months=-12))


def _end_before_start() -> None:
    facts = EmploymentFacts(started_on=date(2026, 9, 30), ended_on=date(2026, 7, 1))
    regular_period(facts=facts)


def _hours_above_full_time() -> None:
    regular_period(facts=EmploymentFacts(weekly_hours=60, full_time_weekly_hours=40))


def _negative_contributable_hours() -> None:
    regular_period(
        ccnl_slug=DOMESTIC,
        level_code="B",
        facts=EmploymentFacts(weekly_hours=25, contributable_hours=Decimal(-160)),
        employer=Employer(headcount=Headcount(1)),
    )


@pytest.mark.parametrize(
    "compute",
    [
        pytest.param(_negative_headcount, id="negative-headcount"),
        pytest.param(_negative_seniority, id="negative-seniority"),
        pytest.param(_end_before_start, id="end-before-start"),
        pytest.param(_hours_above_full_time, id="hours-over-full"),
        pytest.param(_negative_contributable_hours, id="negative-contrib-hours"),
    ],
)
def test_impossible_employment_facts_are_rejected(compute: Callable[[], None]) -> None:
    """Impossible facts raise instead of computing a payslip.

    Observed on 26 September 2026 (all accepted):

    - Commercio L4 cases: gross 1,783.75, net 1,489.92, as for valid facts;
    - domestic level B, 25 weekly hours, -160 contributable hours: gross
      1,212.73, employee contributions -49.60, employer -148.80, net
      1,274.68 above gross.
    """
    with pytest.raises(ValueError):  # noqa: PT011
        compute()
