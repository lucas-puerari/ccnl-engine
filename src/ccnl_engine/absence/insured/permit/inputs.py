"""The permits to assist a disabled person (L. 104/1992 art. 33 c. 3).

Three days a month for each person assisted, taken as whole days or split
into hours.  Pass the event to the run of every month that holds one of
its days; each run pays the days and the hours of its month.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_decimal, require_instance

__all__ = ["DisabilityPermitEvent", "PermitHours"]

_PERMITS = "disability_permits"
_DAY_HOURS = Decimal(24)


@dataclass(frozen=True, slots=True)
class PermitHours:
    """Hours of permit taken on one day.

    Attributes:
        day: The day of the hours.
        hours: The hours of permit, above 0 and at most 24.

    Raises:
        InvalidInputError: When ``day`` is not a date or ``hours`` is not a
            ``Decimal`` within its bounds.
    """

    day: date
    hours: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.day, "PermitHours.day", feature=_PERMITS)
        require_decimal(
            self.hours,
            "PermitHours.hours",
            feature=_PERMITS,
            positive=True,
            maximum=_DAY_HOURS,
        )


def _check_order(days: tuple[date, ...], field: str) -> None:
    if list(days) != sorted(set(days)):
        msg = f"{field} must be in order, each day once"
        raise InvalidInputError(msg, field=field, feature=_PERMITS)


@dataclass(frozen=True, slots=True)
class DisabilityPermitEvent:
    """Days and hours of permit to assist a person with a serious disability.

    INPS pays them in full and the employer advances the indemnity (art. 43
    D.Lgs. 151/2001, which art. 33 c. 4 L. 104/1992 applies); they are
    covered by figurative contributions (art. 44 c. 2).  A worker who
    assists more than one person has three days for each.  Hours a month
    are at most the three days as hours: the weekly hours over the working
    days of the week, times three (INPS msg. 16866/2007); the engine pays
    the hours stated and does not check that limit.

    Attributes:
        days: The whole days of permit, in order, each once; ``()`` when
            the permits of the event are all in hours.
        hours: The days of permit taken in hours, in order, each once and
            none of them a whole day of permit.

    Raises:
        InvalidInputError: When neither ``days`` nor ``hours`` holds a day,
            either is not a tuple, holds a value of the wrong type, or a
            day twice or out of order, or a day is both whole and in hours.
    """

    days: tuple[date, ...]
    hours: tuple[PermitHours, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("days", "hours"):
            if not isinstance(getattr(self, name), tuple):
                msg = f"DisabilityPermitEvent.{name} must be a tuple"
                raise InvalidInputError(
                    msg, field=f"DisabilityPermitEvent.{name}", feature=_PERMITS
                )
        if not self.days and not self.hours:
            field = "DisabilityPermitEvent.days"
            msg = f"{field} or DisabilityPermitEvent.hours must hold a day"
            raise InvalidInputError(msg, field=field, feature=_PERMITS)
        for day in self.days:
            require_date(day, "DisabilityPermitEvent.days", feature=_PERMITS)
        for item in self.hours:
            require_instance(
                item, PermitHours, "DisabilityPermitEvent.hours", feature=_PERMITS
            )
        _check_order(self.days, "DisabilityPermitEvent.days")
        hour_days = tuple(item.day for item in self.hours)
        _check_order(hour_days, "DisabilityPermitEvent.hours")
        if set(self.days).intersection(hour_days):
            msg = "DisabilityPermitEvent.hours must not hold a whole day of permit"
            raise InvalidInputError(
                msg, field="DisabilityPermitEvent.hours", feature=_PERMITS
            )

    @property
    def event_date(self) -> date:
        """First day of permit, whole or in hours."""
        return min(self._all_days())

    def _all_days(self) -> tuple[date, ...]:
        return self.days + tuple(item.day for item in self.hours)

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the first and last day of permit within ``first``-``last``.

        Returns:
            The first and last day of permit, whole or in hours, in the
            span; ``None`` when none.
        """
        inside = [day for day in self._all_days() if first <= day <= last]
        return (min(inside), max(inside)) if inside else None

    def days_within(self, first: date, last: date) -> tuple[date, ...]:
        """Return the whole days of permit within ``first``-``last``.

        Returns:
            Those days, in order.
        """
        return tuple(day for day in self.days if first <= day <= last)

    def hours_within(self, first: date, last: date) -> Decimal:
        """Return the hours of permit within ``first``-``last``.

        Returns:
            Their sum, zero when none.
        """
        return sum(
            (item.hours for item in self.hours if first <= item.day <= last),
            Decimal(0),
        )
