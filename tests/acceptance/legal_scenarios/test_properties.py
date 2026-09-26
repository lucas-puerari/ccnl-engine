"""Metamorphic properties that must hold for every valid input."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ccnl_engine import (
    ContributableHours,
    EmployerProfile,
    Employment,
    Headcount,
    WeeklyHours,
)
from ccnl_engine.events import OvertimeEvent
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    DOMESTIC,
    regular_period,
)

pytestmark = pytest.mark.legal_scenario

_FULL_TIME = 40
_WEEKLY_HOURS = st.integers(min_value=1, max_value=_FULL_TIME)
_CONTRIBUTABLE_HOURS = st.decimals(
    min_value=Decimal(0), max_value=Decimal(400), places=2, allow_nan=False
)
_OVERTIME_HOURS = st.decimals(
    min_value=Decimal("0.5"), max_value=Decimal(60), places=1, allow_nan=False
)
_OVERTIME_RATE = Decimal("12.50")


def _part_time(weekly_hours: int) -> Employment:
    return Employment(
        ccnl_slug=COMMERCIO,
        level_code="4",
        weekly_hours=WeeklyHours(weekly_hours),
        full_time_weekly_hours=WeeklyHours(_FULL_TIME),
    )


@given(weekly_hours=_WEEKLY_HOURS)
@settings(max_examples=20)
def test_part_time_contributions_are_never_negative(weekly_hours: int) -> None:
    """Ordinary INPS contributions are a rate times a non-negative base."""
    breakdown = regular_period(
        employment=_part_time(weekly_hours)
    ).contribution_breakdown

    assert breakdown.employee >= 0
    assert breakdown.employer >= 0


@given(hours=_CONTRIBUTABLE_HOURS)
@settings(max_examples=20)
def test_domestic_contributions_are_never_negative(hours: Decimal) -> None:
    """Domestic INPS is an hourly flat rate times non-negative paid hours."""
    employment = Employment(
        ccnl_slug=DOMESTIC, level_code="B", weekly_hours=WeeklyHours(25)
    )
    breakdown = regular_period(
        employment=employment,
        contributable_hours=ContributableHours(hours),
        employer=EmployerProfile(headcount=Headcount(1)),
    ).contribution_breakdown

    assert breakdown.employee >= 0
    assert breakdown.employer >= 0


@given(first=_WEEKLY_HOURS, second=_WEEKLY_HOURS)
@settings(max_examples=20)
def test_gross_does_not_decrease_with_contracted_hours(first: int, second: int) -> None:
    """More part-time hours never lower the pre-tax gross."""
    low, high = sorted((first, second))
    gross_low = regular_period(employment=_part_time(low)).period_gross
    gross_high = regular_period(employment=_part_time(high)).period_gross

    assert gross_low <= gross_high


@given(first=_OVERTIME_HOURS, second=_OVERTIME_HOURS)
@settings(max_examples=20)
def test_gross_does_not_decrease_with_overtime_hours(
    first: Decimal, second: Decimal
) -> None:
    """More overtime hours never lower the pre-tax gross."""
    low, high = sorted((first, second))

    def gross(hours: Decimal) -> Decimal:
        event = OvertimeEvent(
            event_date=date(2026, 1, 15), hours=hours, hourly_rate=_OVERTIME_RATE
        )
        return regular_period(events=(event,)).period_gross

    assert gross(low) <= gross(high)
