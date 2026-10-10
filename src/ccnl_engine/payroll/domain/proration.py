"""Share of a monthly pay a partly employed month carries.

A worker hired or terminated during a month is paid the daily quotas of the
days of that month the employment covers, never the full monthly pay.  The
daily quota is the one the CCNL sets for its unpaid absences
(:class:`~ccnl_engine.contract.absence.models.DailyDivisorMethod`), so a
hire, a termination and an absence count the same payable days:

- ``by_26``: one twenty-sixth per employed Monday to Saturday; Sundays are
  not paid days, a public holiday on a weekday is;
- ``by_30``: one thirtieth per employed day of a 30-day commercial month: a
  span that reaches the last day of the month runs to day 30, and day 31
  counts as day 30;
- ``by_hourly``: ``daily_hours / hourly_divisor`` per employed Monday to
  Friday;
- ``by_25``: the CCNL states the quota but not which days of a month are
  payable, so a partly employed month has no proration and is not paid.

The share never exceeds one monthly pay: a month with more payable days
than the divisor (27 Mondays to Saturdays) pays the full month.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from ccnl_engine.contract.absence.models import DailyDivisorMethod

__all__ = ["MonthProration", "payable_days"]

_ONE = Decimal(1)
_COMMERCIAL_MONTH = 30
_SATURDAY = 5
_FRIDAY = 4
_DIVISORS = {
    DailyDivisorMethod.BY_26: Decimal(26),
    DailyDivisorMethod.BY_30: Decimal(_COMMERCIAL_MONTH),
}


def _weekdays(first: date, last: date, last_weekday: int) -> int:
    """Return the days from ``first`` to ``last`` up to ``last_weekday``.

    Returns:
        Days whose ``date.weekday()`` is at most ``last_weekday``.
    """
    span = (last - first).days + 1
    return sum(
        1 for i in range(span) if (first + timedelta(days=i)).weekday() <= last_weekday
    )


def _commercial_days(first: date, last: date) -> int:
    """Return the days of a 30-day commercial month from ``first`` to ``last``.

    Returns:
        ``end - start + 1``, with ``end`` 30 when ``last`` closes its month
        and ``start`` capped at 30.
    """
    month_end = calendar.monthrange(last.year, last.month)[1]
    end = _COMMERCIAL_MONTH if last.day == month_end else last.day
    return end - min(first.day, _COMMERCIAL_MONTH) + 1


def payable_days(method: DailyDivisorMethod, first: date, last: date) -> int:
    """Return the payable days of the employed span ``first``-``last``.

    Both days are in the same calendar month, ``first`` not after ``last``.

    Returns:
        Mondays to Saturdays for ``by_26``, commercial-month days for
        ``by_30``, Mondays to Fridays for ``by_hourly``.
    """
    if method is DailyDivisorMethod.BY_30:
        return _commercial_days(first, last)
    if method is DailyDivisorMethod.BY_26:
        return _weekdays(first, last, _SATURDAY)
    return _weekdays(first, last, _FRIDAY)


@dataclass(frozen=True)
class MonthProration:
    """Payable days of a partly employed month and the share they pay.

    Attributes:
        method: Daily divisor method of the CCNL.
        first: First employed day of the month.
        last: Last employed day of the month.
        days: Payable days from ``first`` to ``last``.
        divisor: Days (``by_26``, ``by_30``) or hours (``by_hourly``) of one
            monthly pay.
        daily_hours: Hours of one payable day, ``by_hourly`` only.
    """

    method: DailyDivisorMethod
    first: date
    last: date
    days: int
    divisor: Decimal
    daily_hours: Decimal | None = None

    @classmethod
    def of(
        cls,
        method: DailyDivisorMethod,
        span: tuple[date, date],
        *,
        hourly_divisor: Decimal | None = None,
        daily_hours: Decimal | None = None,
    ) -> MonthProration | None:
        """Return the proration of ``span`` under ``method``.

        Args:
            method: Daily divisor method of the CCNL.
            span: First and last employed day of the month.
            hourly_divisor: Monthly hours of the CCNL, read by ``by_hourly``.
            daily_hours: Hours of one day, read by ``by_hourly``.

        Returns:
            The proration, ``None`` for ``by_25``, whose payable days are not
            defined, and for ``by_hourly`` without both hour figures: the
            rule is then incomplete.
        """
        if method is DailyDivisorMethod.BY_25:
            return None
        first, last = span
        divisor = _DIVISORS.get(method, hourly_divisor)
        hourly = method is DailyDivisorMethod.BY_HOURLY
        if divisor is None or (hourly and daily_hours is None):
            return None
        return cls(
            method=method,
            first=first,
            last=last,
            days=payable_days(method, first, last),
            divisor=divisor,
            daily_hours=daily_hours if hourly else None,
        )

    @property
    def units(self) -> Decimal:
        """Payable days, or payable hours for ``by_hourly``."""
        return Decimal(self.days) * (self.daily_hours or _ONE)

    @property
    def full(self) -> bool:
        """Whether the span is worth at least one monthly pay."""
        return self.units >= self.divisor
