"""Employment fact value objects: hours, work pattern and employment period."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from enum import StrEnum
from typing import cast

from ccnl_engine.collection.validators import frozenset_of, tuple_of
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
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


#: Hours in a week: no contract can state more weekly hours.
MAX_WEEKLY_HOURS = Decimal(168)
#: Smallest unit of an hour value (37.5, 37.25): a hundredth of an hour.
_HUNDREDTH = Decimal("0.01")


def _require_hours(value: object, path: str, *, positive: bool) -> None:
    """Reject an hour value that is not a Decimal of at most two places.

    Raises:
        InvalidInputError: When ``value`` is not a finite Decimal in
            ``[0, 168]`` (``(0, 168]`` when ``positive``) with at most two
            decimal places.
    """
    require_decimal(
        value,
        path,
        feature=FEATURE,
        minimum=None if positive else _ZERO,
        maximum=MAX_WEEKLY_HOURS,
        positive=positive,
    )
    hours = cast("Decimal", value)
    if hours != hours.quantize(_HUNDREDTH, rounding=ROUND_DOWN):
        msg = f"{path} must have at most two decimal places; got {hours}"
        raise InvalidInputError(msg, field=path, feature=FEATURE)


@dataclass(frozen=True, slots=True)
class WeeklyHours:
    """Weekly working hours, contracted or full-time.

    Attributes:
        value: Hours per week, a :class:`~decimal.Decimal` ``> 0`` and at
            most 168 with at most two decimal places (``Decimal("37.5")``).

    Raises:
        InvalidInputError: When ``value`` is not a finite Decimal, is not
            positive, exceeds 168 or has more than two decimal places.
    """

    value: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        _require_hours(self.value, "WeeklyHours.value", positive=True)


#: Days of a week, Monday first, as :attr:`WorkPattern.weekday_hours` lists them.
WEEK_DAYS = 7
#: Hours in a day: no day of a pattern can state more.
_MAX_DAY_HOURS = Decimal(24)


def _day_hours(value: object, path: str) -> Decimal:
    """Return the hours of one day of a weekly pattern, validated.

    Returns:
        ``value``, a Decimal in ``[0, 24]`` with at most two decimal places.

    Raises:
        InvalidInputError: When ``value`` is not such a Decimal.
    """
    _require_hours(value, path, positive=False)
    hours = cast("Decimal", value)
    if hours > _MAX_DAY_HOURS:
        msg = f"{path} must not exceed {_MAX_DAY_HOURS} hours; got {hours}"
        raise InvalidInputError(msg, field=path, feature=FEATURE)
    return hours


def _weekday_hours(value: object) -> tuple[Decimal, ...]:
    """Return the hours of the seven days of a weekly pattern, validated.

    Returns:
        ``value`` as a tuple of seven day hours, Monday first.

    Raises:
        InvalidInputError: When ``value`` is not a tuple or list of seven
            valid day hours, at least one positive.
    """
    path = "WorkPattern.weekday_hours"
    days = tuple_of(value, path, _day_hours, feature=FEATURE)
    if len(days) != WEEK_DAYS or sum(days, _ZERO) <= _ZERO:
        msg = (
            f"{path} must list the hours of the {WEEK_DAYS} days of the "
            f"week, Monday first, at least one positive; got {days}"
        )
        raise InvalidInputError(msg, field=path, feature=FEATURE)
    return days


def _month(value: object, path: str) -> int:
    """Return a calendar month of a pattern, validated.

    Returns:
        ``value``, an int from 1 to 12.
    """
    require_int(value, path, feature=FEATURE, minimum=1, maximum=12)
    return cast("int", value)


@dataclass(frozen=True, slots=True)
class WorkPattern:
    """How the contracted hours are spread over the week and the year.

    A horizontal part time needs no pattern: :class:`WeeklyHours` below the
    full time scale every month.  A pattern states a vertical or mixed part
    time (D.Lgs. 81/2015 art. 5 c. 2): the hours of each day of the week,
    and the months of the year the worker works.  In a month the worker
    works the pay is the weekly-hours ratio of a horizontal part time; a
    month outside :attr:`months` pays nothing and accrues no extra-month
    rateo.

    Attributes:
        weekday_hours: Hours worked on each day of the week, Monday first:
            seven Decimals in ``[0, 24]`` with at most two decimal places,
            at least one positive.  Their sum must equal the contracted
            ``weekly_hours`` of the employment.  ``None`` when not stated.
        months: Calendar months (1-12) the worker works, at least one.
            ``None`` for every month.

    Raises:
        InvalidInputError: When neither field is stated, ``weekday_hours``
            is not seven valid day hours or sums to zero, or ``months`` is
            not a non-empty frozenset of months.
    """

    weekday_hours: tuple[Decimal, ...] | None = None
    months: frozenset[int] | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.weekday_hours is None and self.months is None:
            msg = "a WorkPattern states weekday_hours, months or both"
            raise InvalidInputError(msg, field="WorkPattern", feature=FEATURE)
        if self.weekday_hours is not None:
            object.__setattr__(
                self, "weekday_hours", _weekday_hours(self.weekday_hours)
            )
        if self.months is not None:
            path = "WorkPattern.months"
            months = frozenset_of(self.months, path, _month, feature=FEATURE)
            if not months:
                msg = f"{path} must name at least one month"
                raise InvalidInputError(msg, field=path, feature=FEATURE)
            object.__setattr__(self, "months", months)

    @property
    def weekly_hours(self) -> Decimal | None:
        """Hours of the week the pattern states, ``None`` without days."""
        if self.weekday_hours is None:
            return None
        return sum(self.weekday_hours, _ZERO)

    def works_in(self, month: int) -> bool:
        """Return whether the worker works in a calendar month.

        Returns:
            ``True`` for every month when :attr:`months` is not stated.
        """
        return self.months is None or month in self.months

    def idle_days(self, first: date, last: date) -> frozenset[date]:
        """Return the days from ``first`` to ``last`` of the months not worked.

        Returns:
            Every day of the range whose month is outside :attr:`months`;
            empty when every month is worked or ``last`` precedes ``first``.
        """
        if self.months is None:
            return frozenset()
        span = (last - first).days + 1
        days = (first + timedelta(days=i) for i in range(max(0, span)))
        return frozenset(d for d in days if not self.works_in(d.month))


def check_pattern_hours(
    weekly_hours: WeeklyHours | None, pattern: WorkPattern | None
) -> None:
    """Reject a weekly pattern whose days do not sum to the weekly hours.

    Raises:
        InvalidInputError: When ``pattern`` states ``weekday_hours`` and
            ``weekly_hours`` is missing or differs from their sum.
    """
    hours = None if pattern is None else pattern.weekly_hours
    if hours is None:
        return
    stated = None if weekly_hours is None else weekly_hours.value
    if stated != hours:
        msg = (
            f"WorkPattern.weekday_hours sum to {hours} hours a week; "
            f"weekly_hours must state the same hours, got {stated}"
        )
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
        require_decimal(
            self.value, "ContributableHours.value", feature=FEATURE, minimum=_ZERO
        )


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
