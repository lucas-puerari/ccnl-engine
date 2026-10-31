"""The span of an employment and how it ends."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import parse_enum, require_bool, require_date

__all__ = ["EmploymentPeriod", "TerminationCause"]

FEATURE = "employment_facts"


class TerminationCause(StrEnum):
    """How an employment ends.

    Attributes:
        DISMISSAL: The employer dismisses the worker (licenziamento).
        RESIGNATION: The worker resigns (dimissioni).
        DEATH: The worker dies.
        MUTUAL_AGREEMENT: The parties agree to end it (risoluzione
            consensuale).
    """

    DISMISSAL = "dismissal"
    RESIGNATION = "resignation"
    DEATH = "death"
    MUTUAL_AGREEMENT = "mutual_agreement"


_JUST_CAUSE = frozenset({TerminationCause.DISMISSAL, TerminationCause.RESIGNATION})


@dataclass(frozen=True, slots=True)
class EmploymentPeriod:
    """Start and optional end of the employment relationship.

    Attributes:
        started_on: First day of employment.
        ended_on: Last day of employment, or ``None`` for an open-ended
            relationship.  Must not precede ``started_on``.
        ended_by: How the employment ends, with ``ended_on``; ``None`` when
            not stated (a run that needs it reports the missing fact).
        just_cause: Whether a dismissal or a resignation has a just cause
            (art. 2119 c.c.); ``None`` when not stated or not either.

    Raises:
        InvalidInputError: When a date is not a ``date``, ``ended_on`` is
            before ``started_on``, ``ended_by`` comes without ``ended_on``,
            or ``just_cause`` with a cause other than a dismissal or a
            resignation.
    """

    started_on: date
    ended_on: date | None = None
    ended_by: TerminationCause | None = None
    just_cause: bool | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.started_on, "EmploymentPeriod.started_on", feature=FEATURE)
        require_date(
            self.ended_on, "EmploymentPeriod.ended_on", feature=FEATURE, optional=True
        )
        if self.ended_on is not None and self.ended_on < self.started_on:
            msg = (
                f"ended_on ({self.ended_on}) must not precede "
                f"started_on ({self.started_on})"
            )
            raise InvalidInputError(
                msg, field="EmploymentPeriod.ended_on", feature=FEATURE
            )
        if self.ended_by is not None:
            object.__setattr__(self, "ended_by", self._cause())
        self._check_just_cause()

    def _cause(self) -> TerminationCause:
        cause = parse_enum(
            self.ended_by,
            TerminationCause,
            "EmploymentPeriod.ended_by",
            feature=FEATURE,
        )
        if self.ended_on is None:
            msg = "EmploymentPeriod.ended_by needs ended_on"
            raise InvalidInputError(
                msg, field="EmploymentPeriod.ended_by", feature=FEATURE
            )
        return cause

    def _check_just_cause(self) -> None:
        if self.just_cause is None:
            return
        require_bool(self.just_cause, "EmploymentPeriod.just_cause", feature=FEATURE)
        if self.ended_by not in _JUST_CAUSE:
            msg = "EmploymentPeriod.just_cause applies to a dismissal or a resignation"
            raise InvalidInputError(
                msg, field="EmploymentPeriod.just_cause", feature=FEATURE
            )

    @classmethod
    def from_dates(
        cls, started_on: date | None, ended_on: date | None
    ) -> EmploymentPeriod | None:
        """Build a period from optional dates, as supplied by callers.

        Returns:
            ``None`` when neither date is given, otherwise the validated period.

        Raises:
            InvalidInputError: When only ``ended_on`` is given, or when
                ``ended_on`` precedes ``started_on``.
        """
        if started_on is None:
            if ended_on is not None:
                msg = f"ended_on ({ended_on}) requires started_on"
                raise InvalidInputError(msg, feature=FEATURE)
            return None
        return cls(started_on=started_on, ended_on=ended_on)

    def overlaps_month(self, year: int, month: int) -> bool:
        """Return whether the employment covers at least one day of a month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``True`` when the month has at least one employed day.
        """
        first, last = _month_bounds(year, month)
        return self.started_on <= last and (
            self.ended_on is None or self.ended_on >= first
        )

    def covers_month(self, year: int, month: int) -> bool:
        """Return whether the employment covers every day of a month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``True`` when the employment starts on or before the first day
            and does not end before the last day of the month.
        """
        first, last = _month_bounds(year, month)
        return self.started_on <= first and (
            self.ended_on is None or self.ended_on >= last
        )

    def span_in_month(self, year: int, month: int) -> tuple[date, date] | None:
        """Return the first and last employed day of a calendar month.

        Args:
            year: Calendar year of the month.
            month: Calendar month, 1-12.

        Returns:
            ``(first, last)`` employed days of the month, inclusive; ``None``
            when the employment has no day in it.
        """
        first, last = _month_bounds(year, month)
        first = max(first, self.started_on)
        if self.ended_on is not None:
            last = min(last, self.ended_on)
        return None if last < first else (first, last)

    def clip_start(self, day: date) -> date:
        """Return ``day``, or the hire date when ``day`` precedes it.

        Args:
            day: A date, typically the first day of an accrual window.

        Returns:
            ``max(day, started_on)``.
        """
        return max(day, self.started_on)


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    """Return the first and last day of a calendar month.

    Returns:
        ``(first, last)`` dates of ``month`` in ``year``.
    """
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    return first, last
