"""The daily rests of the first year of a child (D.Lgs. 151/2001 artt. 39-41).

Two rests of an hour a day, one when the working day is shorter than six
hours, half an hour each with a nursery of the employer (art. 39); the
father's in the cases of art. 40; doubled for a multiple birth (art. 41).
The event states the hours taken: the engine does not check them against
those limits.  Pass the event to the run of every month that holds one of
its days; each run pays the hours of its month.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_instance

__all__ = ["NursingRestEvent"]

_RESTS = "nursing_rests"


def _first_birthday(born: date) -> date:
    year = born.year + 1
    return born.replace(
        year=year, day=min(born.day, calendar.monthrange(year, born.month)[1])
    )


@dataclass(frozen=True, slots=True)
class NursingRestEvent:
    """Hours of daily rest in the first year of a child.

    INPS pays them in full and the employer advances the indemnity (art. 43
    c. 1); they count as hours worked for the pay (art. 39 c. 2) and are
    covered by figurative contributions (art. 44 c. 1).

    Attributes:
        hours: The hours of rest of each day, in order, each day once.
        child_born_on: Birth day of the child.

    Raises:
        InvalidInputError: When ``hours`` is empty or not a tuple of
            :class:`LeaveHours`, holds a day twice or out of order, or a
            day before the birth or from the child's first birthday.
    """

    hours: tuple[LeaveHours, ...]
    child_born_on: date

    def __post_init__(self) -> None:  # noqa: D105
        field = "NursingRestEvent.hours"
        require_date(
            self.child_born_on, "NursingRestEvent.child_born_on", feature=_RESTS
        )
        if not isinstance(self.hours, tuple) or not self.hours:
            msg = f"{field} must be a non-empty tuple of LeaveHours"
            raise InvalidInputError(msg, field=field, feature=_RESTS)
        for item in self.hours:
            require_instance(item, LeaveHours, field, feature=_RESTS)
        days = [item.day for item in self.hours]
        if days != sorted(set(days)):
            msg = f"{field} must be in order, each day once"
            raise InvalidInputError(msg, field=field, feature=_RESTS)
        if days[0] < self.child_born_on or days[-1] >= _first_birthday(
            self.child_born_on
        ):
            msg = f"{field} must fall in the first year of the child (art. 39 c. 1)"
            raise InvalidInputError(msg, field=field, feature=_RESTS)

    @property
    def event_date(self) -> date:
        """First day of rest."""
        return self.hours[0].day

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the first and last day of rest within ``first``-``last``.

        Returns:
            Those days, ``None`` when none.
        """
        inside = [i.day for i in self.hours if first <= i.day <= last]
        return (inside[0], inside[-1]) if inside else None

    def hours_within(self, first: date, last: date) -> Decimal:
        """Return the hours of rest within ``first``-``last``.

        Returns:
            Their sum, zero when none.
        """
        return sum((i.hours for i in self.hours if first <= i.day <= last), Decimal(0))
