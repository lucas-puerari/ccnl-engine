"""The calendar windows the sickness of a CCNL is counted over."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

__all__ = ["months_after", "window_start"]


def window_start(day: date, years: int, months: int = 0) -> date:
    """Return the first day of the ``years`` and ``months`` that end on ``day``.

    Returns:
        The day after the same day ``years`` and ``months`` earlier, or
        after the last day of that month when it is shorter (28 February
        for a 29 February that year lacks).
    """
    total = (day.year - years) * 12 + day.month - 1 - months
    year, month = divmod(total, 12)
    last = calendar.monthrange(year, month + 1)[1]
    anchor = date(year, month + 1, min(day.day, last))
    return anchor + timedelta(days=1)


def months_after(day: date, months: int) -> date:
    """Return the day ``months`` calendar months after ``day``.

    Returns:
        The same day of the month, the last of a shorter month.
    """
    month = day.month - 1 + months
    year, month = day.year + month // 12, month % 12 + 1
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last))
