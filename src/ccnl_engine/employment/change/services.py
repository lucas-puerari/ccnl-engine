"""The employment in force on a run, and the hours its ratei were accrued at.

A change of level or category prices the months from its date; the extra
months are paid on the pay in force when they are paid ("retribuzione in
atto", e.g. Commercio Art. 221, Turismo art. 161), so a promotion raises
the whole rateo.  A change of hours does not: a worker who moved from full
time to part time accrued the months before at full time, so the rateo of
each stretch of the window is paid at its own hours (D.Lgs. 81/2015 art. 7
c. 1, the part-time worker's pay proportional to the hours worked).
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.extra_month.models import absence_days
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.employment.inputs import Employment
    from ccnl_engine.extra_month.models import ExtraMonthAccrual
    from ccnl_engine.run.models import PayrollRun

__all__ = ["hours_ratio", "in_force_on", "rateo_scale", "terms_day"]

#: The employment from each date: the first entry is the employment of the
#: plan, dated by the first day it can apply to.
type Timeline = tuple[tuple[date, Employment], ...]

_ONE = Decimal(1)


def in_force_on(timeline: Timeline, day: date) -> Employment:
    """Return the employment of ``timeline`` in force on ``day``.

    Returns:
        The employment of the latest entry dated on or before ``day``, the
        first entry when every date follows it.
    """
    current = timeline[0][1]
    for start, employment in timeline:
        if start <= day:
            current = employment
    return current


def terms_day(run: PayrollRun) -> date:
    """Return the day whose terms a run pays.

    A regular or termination run pays its month at the terms of its last
    day, whose promotion inside the month splits it
    (:mod:`~ccnl_engine.compensation.change.rules`); an extra-month run at
    the terms of the first day of its month.

    Returns:
        The last or the first day of the month of ``run``.
    """
    if run.run_kind in {RunKind.REGULAR, RunKind.TERMINATION}:
        return date(run.year, run.month, calendar.monthrange(run.year, run.month)[1])
    return date(run.year, run.month, 1)


def hours_ratio(employment: Employment) -> Decimal:
    """Return the part-time ratio of ``employment``.

    Returns:
        The weekly hours over the full-time hours, ``1`` when either is not
        stated.
    """
    hours, full = employment.weekly_hours, employment.full_time_weekly_hours
    if hours is None or full is None:
        return _ONE
    return hours.value / full.value


def rateo_scale(
    accrual: Callable[[frozenset[date]], ExtraMonthAccrual],
    timeline: Timeline,
    paid_with: Employment,
) -> Decimal:
    """Return the factor that pays each stretch of a rateo at its own hours.

    Args:
        accrual: The rateo of the window with the given days not accruing.
        timeline: The employment from each date.
        paid_with: The employment of the run that pays the rateo.

    Returns:
        The months accrued at each stretch, times its ratio, over the months
        accrued times the ratio of ``paid_with``; ``1`` when the hours do not
        change or nothing accrues.
    """
    paid = hours_ratio(paid_with)
    if all(hours_ratio(e) == paid for _, e in timeline):
        return _ONE
    whole = accrual(frozenset())
    if not whole.accrued:
        return _ONE
    window = whole.window
    weighted = Decimal(0)
    for i, (start, employment) in enumerate(timeline):
        end = timeline[i + 1][0] - timedelta(days=1) if i + 1 < len(timeline) else None
        outside: frozenset[date] = frozenset()
        if start > window.start:
            outside = absence_days(window.start, start - timedelta(days=1))
        if end is not None:
            outside |= absence_days(end + timedelta(days=1), window.end)
        weighted += accrual(outside).accrued * hours_ratio(employment)
    return weighted / (whole.accrued * paid)
