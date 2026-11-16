"""Holidays on the weekly rest day of the Multiservizi ANIP, art. 41.

The festività of letters b) and c) falling on the weekly rest day of art. 40
pay a further daily quota of the global monthly pay; 4 November is paid on
the first Sunday of November.  1 November 2026 is a Sunday.
"""

from __future__ import annotations

from datetime import date

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _days(year: int, month: int) -> list[str]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10)),
            period_id=PeriodId(year=year, month=month),
            payment_date=date(year, month, 27),
            ccnl_id="multiservizi-anip",
            level_code="2",
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return sorted(
        str(d.inputs["days"])
        for d in result.decisions
        if d.capability == "sunday_holiday" and d.amount
    )


def test_the_clause_is_sourced() -> None:
    """Art. 41 lists the religious holidays too, not only the civil ones."""
    rules = load_ccnl("multiservizi-anip").work_rules
    assert rules is not None
    clause = rules.sunday_holidays
    assert clause is not None
    assert {"01-01", "08-15", "12-26", "11-04"} <= clause.holidays_on(date(2026, 1, 1))


def test_november_2026_pays_the_sunday_holiday() -> None:
    """1 November 2026 is a Sunday: a further daily quota."""
    assert _days(2026, 11)
