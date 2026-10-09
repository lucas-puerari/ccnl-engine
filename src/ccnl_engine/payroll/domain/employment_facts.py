"""Employment fact value objects: hours and employment period."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    require_date,
    require_decimal,
    require_int,
)

#: Feature reported by the errors of employment facts.
FEATURE = "employment_facts"

_ZERO = Decimal(0)


class PublicEndOfService(StrEnum):
    """End-of-service regime of a public employee (DPCM 20 dicembre 1999).

    Values:
        TFS: Trattamento di fine servizio (buonuscita or indennità premio
            di servizio) of INPS Gestione Dipendenti Pubblici: the worker
            pays 2.50% of the contribution base, the administration the rest.
        TFR_INPS: Trattamento di fine rapporto accrued notionally by INPS
            (art. 1 c. 6): the administration pays the whole contribution and
            the gross is reduced by the 2.50% the worker no longer pays (c. 3).
        TFR_EMPLOYER: Trattamento di fine rapporto the employer accrues and
            pays (art. 1 c. 6 and 8: enti pubblici non economici, enti di
            ricerca): no contribution to the Gestione, no reduction.
    """

    TFS = "tfs"
    TFR_INPS = "tfr_inps"
    TFR_EMPLOYER = "tfr_employer"


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
        require_int(self.value, "WeeklyHours.value", feature=FEATURE, minimum=1)


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
        require_decimal(
            self.value, "ContributableHours.value", feature=FEATURE, minimum=_ZERO
        )


@dataclass(frozen=True, slots=True)
class EmploymentPeriod:
    """Start and optional end of the employment relationship.

    Attributes:
        started_on: First day of employment.
        ended_on: Last day of employment, or ``None`` for an open-ended
            relationship.  Must not precede ``started_on``.

    Raises:
        InvalidInputError: When a date is not a ``date`` or ``ended_on`` is
            before ``started_on``.
    """

    started_on: date
    ended_on: date | None = None

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
