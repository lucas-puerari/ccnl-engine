"""The permits to assist a disabled person (L. 104/1992 art. 33 c. 3).

Three days a month for each person assisted, taken as whole days.  Pass
the event to the run of every month that holds one of its days; each run
pays the days of its month.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date

__all__ = ["DisabilityPermitEvent"]

_PERMITS = "disability_permits"


@dataclass(frozen=True, slots=True)
class DisabilityPermitEvent:
    """Whole days of permit to assist a person with a serious disability.

    INPS pays them in full and the employer advances the indemnity (art. 43
    D.Lgs. 151/2001, which art. 33 c. 4 L. 104/1992 applies); they are
    covered by figurative contributions (art. 44 c. 2).  A worker who
    assists more than one person has three days for each.

    Attributes:
        days: The days of permit, in order, each once.

    Raises:
        InvalidInputError: When ``days`` is empty, not a tuple, holds a day
            that is not a date, or a day twice or out of order.
    """

    days: tuple[date, ...]

    def __post_init__(self) -> None:  # noqa: D105
        field = "DisabilityPermitEvent.days"
        if not isinstance(self.days, tuple) or not self.days:
            msg = f"{field} must be a non-empty tuple of days"
            raise InvalidInputError(msg, field=field, feature=_PERMITS)
        for day in self.days:
            require_date(day, field, feature=_PERMITS)
        if list(self.days) != sorted(set(self.days)):
            msg = f"{field} must be in order, each day once"
            raise InvalidInputError(msg, field=field, feature=_PERMITS)

    @property
    def event_date(self) -> date:
        """First day of permit."""
        return self.days[0]

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the first and last day of permit within ``first``-``last``.

        Returns:
            The first and last day of permit in the span, ``None`` when none.
        """
        inside = self.days_within(first, last)
        return (inside[0], inside[-1]) if inside else None

    def days_within(self, first: date, last: date) -> tuple[date, ...]:
        """Return the days of permit within ``first``-``last``.

        Returns:
            Those days, in order.
        """
        return tuple(day for day in self.days if first <= day <= last)
