"""The weekly rest day of the employment, Sunday unless stated."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.employment.fact.inputs import WeeklyHours, WorkPattern
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.errors import InvalidInputError

_D = Decimal


def _employment(**fields: object) -> Employment:
    return Employment(
        ccnl_id="turismo-federalberghi",
        level_code="4",
        contract_type=Permanent(),
        **fields,  # type: ignore[arg-type]
    )


def test_the_rest_day_is_sunday_unless_stated() -> None:
    """L. 370/1934 art. 3."""
    assert _employment().weekly_rest_day is Weekday.SUNDAY


def test_the_rest_day_reads_its_name() -> None:
    """The string value is accepted and normalized."""
    assert _employment(weekly_rest_day="monday").weekly_rest_day is Weekday.MONDAY


def test_an_unknown_day_is_rejected() -> None:
    """A value that names no day of the week."""
    with pytest.raises(InvalidInputError, match="weekly_rest_day"):
        _employment(weekly_rest_day="domenica")


@pytest.mark.parametrize(
    ("day", "on"),
    [
        (Weekday.MONDAY, date(2026, 4, 6)),
        (Weekday.WEDNESDAY, date(2026, 11, 4)),
        (Weekday.SUNDAY, date(2026, 11, 1)),
    ],
)
def test_the_day_matches_its_dates(day: Weekday, on: date) -> None:
    """Monday 0 to Sunday 6, as the weekday of a date."""
    assert day.is_day_of(on)
    assert day.number == on.weekday()
    assert not day.is_day_of(date(2026, 11, 3))


_PATTERN = WorkPattern(weekday_hours=(_D(8),) * 5 + (_D(0),) * 2)


def test_the_rest_day_is_a_day_off_the_pattern() -> None:
    """Saturday has no hours in a Monday-to-Friday pattern."""
    employment = _employment(
        weekly_hours=WeeklyHours(_D(40)),
        work_pattern=_PATTERN,
        weekly_rest_day=Weekday.SATURDAY,
    )

    assert employment.weekly_rest_day is Weekday.SATURDAY


def test_a_rest_day_with_hours_is_rejected() -> None:
    """A pattern that works on the stated rest day."""
    with pytest.raises(InvalidInputError, match="8 hours worked on"):
        _employment(
            weekly_hours=WeeklyHours(_D(40)),
            work_pattern=_PATTERN,
            weekly_rest_day=Weekday.FRIDAY,
        )


def test_a_pattern_of_months_only_takes_any_rest_day() -> None:
    """Without weekday hours there is nothing to check against."""
    pattern = WorkPattern(months=frozenset({1, 2}))

    assert _employment(work_pattern=pattern, weekly_rest_day="friday").weekly_rest_day
