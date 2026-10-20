"""Absences an insurer pays: a maternity leave and a work injury.

Each is one absence over its days, like a sickness episode: pass the same
event to every regular run whose month it touches, and each run pays the
days of its month within the employment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date

__all__ = ["MaternityLeaveEvent", "WorkInjuryEvent"]

_MATERNITY = "maternity_leave"
_INJURY = "workplace_injury"


def _clip(
    first: date, last: date, period: tuple[date, date]
) -> tuple[date, date] | None:
    """Return the days of ``first``-``last`` within ``period``, if any.

    Returns:
        The first and last day in common, ``None`` when they share none.
    """
    start, end = max(first, period[0]), min(last, period[1])
    return None if end < start else (start, end)


@dataclass(frozen=True, slots=True)
class MaternityLeaveEvent:
    """A compulsory maternity leave (congedo di maternità).

    Attributes:
        started_on: First day of the leave.
        ended_on: Last day of the leave.

    Raises:
        InvalidInputError: When a day is not a date or the leave ends
            before it starts.
    """

    started_on: date
    ended_on: date

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("started_on", "ended_on"):
            require_date(
                getattr(self, name), f"MaternityLeaveEvent.{name}", feature=_MATERNITY
            )
        if self.ended_on < self.started_on:
            msg = "MaternityLeaveEvent.ended_on must not precede started_on"
            raise InvalidInputError(
                msg, field="MaternityLeaveEvent.ended_on", feature=_MATERNITY
            )

    @property
    def event_date(self) -> date:
        """First day of the leave."""
        return self.started_on

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the days of the leave within ``first``-``last``.

        Returns:
            The first and last day in common, ``None`` when none.
        """
        return _clip(self.started_on, self.ended_on, (first, last))


@dataclass(frozen=True, slots=True)
class WorkInjuryEvent:
    """A temporary absolute inability after a work injury.

    Attributes:
        injury_on: Day of the injury, paid in full by the employer.
        ended_on: Last day of the inability.

    Raises:
        InvalidInputError: When a day is not a date or the inability ends
            before the injury.
    """

    injury_on: date
    ended_on: date

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("injury_on", "ended_on"):
            require_date(
                getattr(self, name), f"WorkInjuryEvent.{name}", feature=_INJURY
            )
        if self.ended_on < self.injury_on:
            msg = "WorkInjuryEvent.ended_on must not precede injury_on"
            raise InvalidInputError(
                msg, field="WorkInjuryEvent.ended_on", feature=_INJURY
            )

    @property
    def event_date(self) -> date:
        """Day of the injury."""
        return self.injury_on

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the days of the inability within ``first``-``last``.

        Returns:
            The first and last day in common, the injury day included,
            ``None`` when none.
        """
        return _clip(self.injury_on, self.ended_on, (first, last))
