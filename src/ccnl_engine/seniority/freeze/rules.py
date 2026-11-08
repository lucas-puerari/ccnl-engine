"""Months of a seniority freeze taken out of the months the increments count."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.seniority.freeze.models import SeniorityFreeze

__all__ = ["months_in_cohort", "months_without_freeze"]


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


def months_in_cohort(
    months: int,
    hired_until: date | None,
    competence: date,
    hired_on: date | None = None,
) -> int:
    """Return ``months``, or 0 for a worker hired after ``hired_until``.

    CED art. 166: the increments, abrogated from 1 January 2019, keep
    maturing "esclusivamente per il personale in forza al 31-12-2018".
    The hire date decides when stated; else the service of ``months``
    ending on ``competence``, which at month precision counts a worker
    hired in the month after ``hired_until`` as in service.

    Returns:
        ``months`` for a worker in service on ``hired_until``, else 0.
    """
    if hired_until is None:
        return months
    if hired_on is not None:
        return months if hired_on <= hired_until else 0
    return months if months >= _whole_months(hired_until, competence) else 0
