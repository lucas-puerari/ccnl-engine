"""The day of the week the worker takes the weekly rest.

L. 370/1934 art. 3 sets the weekly rest on Sunday; art. 5 lets the
activities it lists (hotels and public establishments among them) give it
on another day.  Some CCNLs pay a holiday that falls on the worker's rest
day (Turismo art. 127 c. 4), whatever day of the week that is.
"""

from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import parse_enum

if TYPE_CHECKING:
    from ccnl_engine.employment.fact.inputs import WorkPattern

__all__ = ["Weekday", "check_rest_day"]

_PATH = "Employment.weekly_rest_day"
_FEATURE = "employment_facts"


class Weekday(StrEnum):
    """A day of the week, Monday first."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @property
    def number(self) -> int:
        """Position of the day in the week, Monday 0 and Sunday 6."""
        return list(Weekday).index(self)

    def is_day_of(self, day: dt.date) -> bool:
        """Return whether ``day`` falls on this day of the week.

        Returns:
            True when the weekday of ``day`` is this one.
        """
        return day.weekday() == self.number


def check_rest_day(value: object, pattern: WorkPattern | None) -> Weekday:
    """Return the weekly rest day, validated against the weekly pattern.

    Returns:
        ``value`` as a :class:`Weekday`.

    Raises:
        InvalidInputError: When ``value`` names no day of the week, or the
            pattern states hours worked on it.
    """
    day = parse_enum(value, Weekday, _PATH, feature=_FEATURE)
    hours = None if pattern is None else pattern.weekday_hours
    if hours is not None and hours[day.number] > 0:
        msg = (
            f"{_PATH} is {day.value}, a day the work_pattern states "
            f"{hours[day.number]} hours worked on"
        )
        raise InvalidInputError(msg, field=_PATH, feature=_FEATURE)
    return day
