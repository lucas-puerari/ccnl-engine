"""Employment fact value objects: hours, seniority, employment period."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.shared.domain.errors import InvalidInputError

#: Feature reported by the errors of employment facts.
FEATURE = "employment_facts"


def _require_int(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        msg = f"{name} must be an int; got {value!r}"
        raise InvalidInputError(msg, feature=FEATURE)


@dataclass(frozen=True, slots=True)
class WeeklyHours:
    """Weekly working hours, contracted or full-time.

    Attributes:
        value: Hours per week, ``> 0``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is not positive.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        _require_int(self.value, "weekly_hours")
        if self.value <= 0:
            msg = f"weekly_hours must be > 0; got {self.value}"
            raise InvalidInputError(msg, feature=FEATURE)


@dataclass(frozen=True, slots=True)
class SeniorityMonths:
    """Months of continuous service used for seniority increments.

    Attributes:
        value: Completed months of service, ``>= 0``.

    Raises:
        InvalidInputError: When ``value`` is not an int or is negative.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        _require_int(self.value, "seniority_months")
        if self.value < 0:
            msg = f"seniority_months must be >= 0; got {self.value}"
            raise InvalidInputError(msg, feature=FEATURE)


@dataclass(frozen=True, slots=True)
class ContributableHours:
    """Hours worked and paid in a period that are subject to INPS contributions.

    Zero is valid (a period with no paid hours).

    Attributes:
        value: Finite :class:`~decimal.Decimal` number of hours, ``>= 0``.

    Raises:
        InvalidInputError: When ``value`` is not a finite Decimal or is negative.
    """

    value: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            msg = f"contributable_hours must be a finite Decimal; got {self.value!r}"
            raise InvalidInputError(msg, feature=FEATURE)
        if self.value < 0:
            msg = f"contributable_hours must be >= 0; got {self.value}"
            raise InvalidInputError(msg, feature=FEATURE)


@dataclass(frozen=True, slots=True)
class EmploymentPeriod:
    """Start and optional end of the employment relationship.

    Attributes:
        started_on: First day of employment.
        ended_on: Last day of employment, or ``None`` for an open-ended
            relationship.  Must not precede ``started_on``.

    Raises:
        InvalidInputError: When ``ended_on`` is before ``started_on``.
    """

    started_on: date
    ended_on: date | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.ended_on is not None and self.ended_on < self.started_on:
            msg = (
                f"ended_on ({self.ended_on}) must not precede "
                f"started_on ({self.started_on})"
            )
            raise InvalidInputError(msg, feature=FEATURE)

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

    def days_in_year(self, year: int) -> int:
        """Return the calendar days of ``year`` the employment covers.

        Args:
            year: Calendar year.

        Returns:
            Days from the later of 1 January and ``started_on`` to the
            earlier of 31 December and ``ended_on``, inclusive; zero when
            the employment has no day in ``year``.
        """
        first = max(date(year, 1, 1), self.started_on)
        last = date(year, 12, 31)
        if self.ended_on is not None:
            last = min(last, self.ended_on)
        return max(0, (last - first).days + 1)

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


def check_within_full_time(
    weekly_hours: WeeklyHours | None, full_time_weekly_hours: WeeklyHours | None
) -> None:
    """Reject contracted weekly hours above the full-time weekly hours.

    Raises:
        InvalidInputError: When both are given and ``weekly_hours`` exceeds
            ``full_time_weekly_hours``.
    """
    if (
        weekly_hours is not None
        and full_time_weekly_hours is not None
        and weekly_hours.value > full_time_weekly_hours.value
    ):
        msg = (
            f"weekly_hours ({weekly_hours.value}) must not exceed "
            f"full_time_weekly_hours ({full_time_weekly_hours.value})"
        )
        raise InvalidInputError(msg, feature=FEATURE)
