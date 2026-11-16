"""Holidays on a Sunday of the operai agricoli and florovivaisti, Area2.

Art. 41: up to 2026 the national holidays of the law and 4 November,
celebrated on the first Sunday of November; from 1 January 2027 the
festività infrasettimanali too.  Art. 42: the florovivaisti have every
listed holiday on a Sunday.  1398.09 / 26 = 53.77 a day.
"""

from __future__ import annotations

from datetime import date

import pytest

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


def _paid(year: int, month: int, subsector: str | None = None) -> list[str]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10), subsector=subsector),
            period_id=PeriodId(year=year, month=month),
            payment_date=date(year, month, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area2",
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return [
        f"{d.inputs['days']}:{d.amount}"
        for d in result.decisions
        if d.capability == "sunday_holiday" and d.amount
    ]


@pytest.mark.parametrize(
    ("year", "month", "subsector", "paid"),
    [
        (2026, 11, None, ["2026-11-01:53.77"]),
        (2026, 10, None, []),
        (2027, 8, None, ["2027-08-15:53.77"]),
        (2026, 10, "florovivaisti", ["2026-10-04:53.77"]),
    ],
    ids=["4-november", "4-october-2026", "15-august-2027", "florovivaisti"],
)
def test_the_holidays_on_a_sunday(
    year: int, month: int, subsector: str | None, paid: list[str]
) -> None:
    """The art. 41 list grows in 2027; the florovivaisti have it already."""
    assert _paid(year, month, subsector) == paid


def test_the_added_holidays_start_on_their_day() -> None:
    """The clause pays 15 August from 2027 only."""
    rules = load_ccnl("operai-agricoli-florovivaisti").work_rules
    assert rules is not None
    clause = rules.sunday_holidays
    assert clause is not None
    assert "08-15" not in clause.holidays_on(date(2026, 12, 31))
    assert "08-15" in clause.holidays_on(date(2027, 1, 1))
