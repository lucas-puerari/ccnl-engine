"""The national holidays a holiday target in a sickness covers."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.sickness.holiday.rules import covered_holidays

if TYPE_CHECKING:
    from ccnl_engine.sickness.integration.models import SicknessRules


def _rules(excluded: tuple[str, ...] | None) -> SicknessRules:
    holiday = None if excluded is None else SimpleNamespace(excluded_days=excluded)
    return cast("SicknessRules", SimpleNamespace(holiday=holiday))


def test_the_weekday_holidays_of_three_years() -> None:
    """2027 and the two years before; 4 October 2027 is a Monday."""
    days = covered_holidays(_rules(()), load_national_holidays(), 2027)
    assert date(2027, 10, 4) in days
    assert date(2025, 12, 8) in days
    assert date(2024, 12, 31) not in days


def test_a_sunday_holiday_and_an_excluded_code_are_left_out() -> None:
    """1 November 2026 is a Sunday; 10-04 is not in the clause."""
    days = covered_holidays(_rules(("10-04",)), load_national_holidays(), 2027)
    assert date(2026, 11, 1) not in days
    assert date(2027, 10, 4) not in days
    assert date(2027, 11, 1) in days


def test_no_target_covers_nothing() -> None:
    """Without a holiday target the rule covers no day."""
    assert covered_holidays(_rules(None), load_national_holidays(), 2027) == frozenset()
