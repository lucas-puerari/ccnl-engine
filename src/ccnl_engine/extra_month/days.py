"""The calendar days of an absence."""

from __future__ import annotations

from datetime import date, timedelta

__all__ = ["absence_days"]


def absence_days(first: date, last: date) -> frozenset[date]:
    """Return every calendar day from ``first`` to ``last`` inclusive.

    Returns:
        The days of the range, empty when ``last`` precedes ``first``.
    """
    span = (last - first).days + 1
    return frozenset(first + timedelta(days=i) for i in range(max(0, span)))
