"""Months of a seniority freeze taken out of the months the increments count."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.seniority.freeze.models import SeniorityFreeze

__all__ = ["months_without_freeze"]


def _whole_months(start: date, end: date) -> int:
    months = (end.year - start.year) * 12 + end.month - start.month
    return months - (end.day < start.day)


def months_without_freeze(
    months: int,
    freezes: tuple[SeniorityFreeze, ...],
    counted_on: date,
    competence: date,
) -> int:
    """Return ``months`` less the frozen months aged since ``counted_on``.

    The months stated on ``counted_on`` are the caller's recognised
    service and are kept as they are; only the months the engine ages from
    that date to ``competence`` lose their overlap with a freeze.

    Returns:
        The months the increments count, never below zero.
    """
    frozen = 0
    for freeze in freezes:
        start = max(counted_on, freeze.valid_from)
        end = min(competence, freeze.valid_until)
        if start < end:
            frozen += _whole_months(start, end)
    return max(months - frozen, 0)
