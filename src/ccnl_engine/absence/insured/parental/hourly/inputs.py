"""A parental leave taken by the hour (art. 32 c. 1-ter D.Lgs. 151/2001).

Without a collective rule, the leave by the hour is half the average daily
hours the contract sets in the pay period before the leave, on each day it
is taken (INPS circ. 152/2015 par. 2.2); INPS counts and pays it by the
day: two such days are one day of leave.  The event states the days and
that average; it must hold whole days of leave, as INPS counts them.  The
engine does not check the days against the leave of another child, the
rests of artt. 39-40 or the hours of artt. 33 c. 2 and 42 c. 1, which the
same day excludes without a collective rule (INPS msg. 6704/2015).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveTaken
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.base.inputs import InpsSicknessBase
from ccnl_engine.validators import (
    require_bool,
    require_date,
    require_decimal,
    require_instance,
)

__all__ = ["HourlyParentalLeaveEvent"]

_PARENTAL = "parental_leave"
_FIELD = "HourlyParentalLeaveEvent.hours"
_DAY_HOURS = Decimal(24)
_HALF = Decimal(2)


def _reject(msg: str, field: str = _FIELD) -> InvalidInputError:
    return InvalidInputError(msg, field=field, feature=_PARENTAL)


@dataclass(frozen=True, slots=True)
class HourlyParentalLeaveEvent:
    """Days of parental leave taken by the hour, for one child.

    Attributes:
        hours: The hours of leave of each day, in order, each day once, an
            even number of days; each half of ``average_daily_hours``.
        child_born_on: Birth day of the child.
        taken: The indemnified leave taken for the child before the event.
        average_daily_hours: Average daily hours the contract sets in the
            pay period before the leave.  No default: an assumed day would
            take more or fewer hours of leave than the worker's.
        protection_ended_on: Last day of the maternity or paternity leave
            that ended last; ``None`` when not stated.
        single_parent: Whether the parent is the only one.
        parental_base_pay: Pay of the month before the leave; ``None`` when
            not stated.

    Raises:
        InvalidInputError: When a field is of the wrong type, the days are
            not in order, are odd in number or precede the birth, or a day
            is not half the average daily hours.
    """

    hours: tuple[LeaveHours, ...]
    child_born_on: date
    taken: ParentalLeaveTaken
    average_daily_hours: Decimal
    protection_ended_on: date | None = None
    single_parent: bool = False
    parental_base_pay: InpsSicknessBase | None = None

    def __post_init__(self) -> None:  # noqa: D105
        name = "HourlyParentalLeaveEvent"
        require_date(self.child_born_on, f"{name}.child_born_on", feature=_PARENTAL)
        if self.protection_ended_on is not None:
            field = f"{name}.protection_ended_on"
            require_date(self.protection_ended_on, field, feature=_PARENTAL)
        require_instance(
            self.taken, ParentalLeaveTaken, f"{name}.taken", feature=_PARENTAL
        )
        require_bool(self.single_parent, f"{name}.single_parent", feature=_PARENTAL)
        require_instance(
            self.parental_base_pay,
            InpsSicknessBase,
            f"{name}.parental_base_pay",
            feature=_PARENTAL,
            optional=True,
        )
        require_decimal(
            self.average_daily_hours,
            f"{name}.average_daily_hours",
            feature=_PARENTAL,
            positive=True,
            maximum=_DAY_HOURS,
        )
        self._check_hours()

    def _check_hours(self) -> None:
        if not isinstance(self.hours, tuple) or not self.hours:
            msg = f"{_FIELD} must be a non-empty tuple of LeaveHours"
            raise _reject(msg)
        for item in self.hours:
            require_instance(item, LeaveHours, _FIELD, feature=_PARENTAL)
        problem = self._days_problem()
        if problem is not None:
            raise _reject(problem)

    def _days_problem(self) -> str | None:
        days = [item.day for item in self.hours]
        half = self.average_daily_hours / _HALF
        if days != sorted(set(days)):
            return f"{_FIELD} must be in order, each day once"
        if len(days) % 2:
            return f"{_FIELD} must hold whole days of leave: an even number"
        if days[0] < self.child_born_on:
            return f"{_FIELD} must not precede child_born_on"
        if any(item.hours != half for item in self.hours):
            return (
                f"{_FIELD} must be half of average_daily_hours ({half}) on each "
                "day: the general criterion of art. 32 c. 1-ter"
            )
        return None

    @property
    def event_date(self) -> date:
        """First day of leave."""
        return self.hours[0].day

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the first and last day of leave within ``first``-``last``.

        Returns:
            Those days, ``None`` when none.
        """
        inside = [i.day for i in self.hours if first <= i.day <= last]
        return (inside[0], inside[-1]) if inside else None

    def hours_within(self, first: date, last: date) -> Decimal:
        """Return the hours of leave within ``first``-``last``.

        Returns:
            Their sum, zero when none.
        """
        return sum((i.hours for i in self.hours if first <= i.day <= last), Decimal(0))
