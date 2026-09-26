"""Employment facts must shape the payroll or be rejected when impossible."""

from __future__ import annotations

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

pytestmark = pytest.mark.legal_scenario


@pytest.mark.xfail(
    strict=True,
    reason="employment start and end dates do not select the payroll runs",
)
def test_three_month_employment_has_no_runs_outside_the_period() -> None:
    """Commercio L4 hired 1 July and terminated 30 September 2026.

    Expected: regular runs only for July, August and September; a worker
    who is not employed cannot be paid a monthly salary (art. 2094 c.c.).

    Observed on 26 September 2026: 14 runs (all 12 months plus both extra
    months), annual gross 25,077.50, identical to a full-year employment.
    """
    year = ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug=COMMERCIO,
            level_code="4",
            employment_facts=EmploymentFacts(
                started_on=date(2026, 7, 1), ended_on=date(2026, 9, 30)
            ),
        )
    )
    regular_months = {
        r.run.month
        for r in year.period_results
        if r.run is not None and r.run.run_kind is RunKind.REGULAR
    }

    assert regular_months == {7, 8, 9}


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
