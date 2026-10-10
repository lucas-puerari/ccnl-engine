"""Minimum INPS base of a run: the CCNL pay and the daily minimale.

The base contributions are computed on is never below two floors (INPS
circ. 6/2026 par. 1):

- the pay of the collective agreement (D.L. 338/1989 art. 1 c. 1), read in
  the comparatively most representative CCNL of the category (L. 549/1995
  art. 2 c. 25).  The engine computes the pay of the CCNL of the request
  from its tables, so this floor is the pay chain itself; whether that CCNL
  is the most representative one of the category is not a fact the engine
  holds;
- the minimum daily pay of D.L. 463/1983 art. 7 c. 1, counted on the 26
  days of a fully paid month (full time), or for part time on the hourly
  minimum of D.Lgs. 81/2015 art. 11 c. 1 times the contracted hours of the
  month (the weekly hours over a month of 26 days of a six-day week).

Art. 7 c. 5 excludes apprentices and operai agricoli (domestic work has its
own hourly contributions and no ordinary INPS rules).  The pay compared is
the INPS base of the run that posts the monthly pay of a fully employed
month.  The day count of a partial month, of a month with an absence or
sick leave (whose reduced pay circ. 6/2026 par. 1 and the Uniemens element
``<RispettoMinimale>`` exempt), of a sector without a sourced monthly day
count, and whether pay a later run adds to the month (an extra month, an
adjustment) or the extra-month ratei settled at termination count toward
the minimum (INPS circ. 196/1995 leaves the ratei out for the Fondo Volo
only), are not sourced: when the base is
below the highest minimum the month can have, the minimum is undetermined
instead of guessed, and the run is not payable.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.contribution.models_minimum_base import (
    MinimumBase,
    MinimumBaseReason,
    MonthPosition,
)

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.tax.contribution.models_minimum_base import MinimumBaseRule

__all__ = ["resolve_minimum_base"]

_DAY = timedelta(days=1)
#: Days of the week INPS counts the daily minimum on, Monday to Saturday.
_SIX_DAY_WEEK = 6
#: Most days of a six-day week a calendar month holds (31 days from Monday).
_MOST_MONTH_DAYS = 27


def _working_days(span: tuple[date, date]) -> int:
    """Return the days of a six-day week, Monday to Saturday, in ``span``.

    Returns:
        The days of the span, both ends included, other than Sundays.
    """
    first, last = span
    days = (first + _DAY * n for n in range((last - first).days + 1))
    return sum(1 for day in days if day.weekday() < _SIX_DAY_WEEK)


def _bound_days(rule: MinimumBaseRule, span: tuple[date, date] | None) -> int:
    """Return the most days the minimum of the month can be counted on.

    A fully paid month counts the sourced monthly days.  Without them the
    count is not known, even on a shorter normal week: INPS counts the days
    of a six-day week also when the hours are spread on five, so the bound
    is the most days of a six-day week a calendar month holds (27).  A
    partly employed month counts no more than the days of a six-day week in
    its employed span.

    Returns:
        The days the highest minimum of the month is counted on.
    """
    most = rule.monthly_days or _MOST_MONTH_DAYS
    return most if span is None else min(most, _working_days(span))


def _bound(rule: MinimumBaseRule, position: MonthPosition) -> Decimal:
    """Return the highest minimum the month of the run can have.

    Full time: the daily minimum times the most days of the month.  Part
    time: the hourly minimum (as published, or the daily minimum over the
    full-time hours times the days of the normal week when none is) times
    the contracted hours of those days.

    Returns:
        The bound, rounded to the cent.
    """
    days = _bound_days(rule, position.span)
    part_time = position.part_time
    if part_time is None:
        return money(rule.daily * days)
    hours, full = part_time
    hourly = rule.hourly_for(full) or rule.daily * rule.week_days / full
    return money(hourly * hours * days / rule.week_days)


def _exclusion(
    rule: MinimumBaseRule, position: MonthPosition
) -> MinimumBaseReason | None:
    """Return why art. 7 c. 5 excludes the worker from the minimum, if it does.

    Returns:
        :attr:`MinimumBaseReason.APPRENTICE` or
        :attr:`MinimumBaseReason.EXEMPT_CATEGORY`, ``None`` otherwise.
    """
    if position.apprentice:
        return MinimumBaseReason.APPRENTICE
    if position.category in rule.exempt_categories:
        return MinimumBaseReason.EXEMPT_CATEGORY
    return None


def _undetermined_reason(
    rule: MinimumBaseRule, position: MonthPosition
) -> MinimumBaseReason | None:
    """Return why the minimum of the run's month cannot be fixed, if so.

    Returns:
        The first reason, in the order of the checks; ``None`` when the run
        posts the pay of a fully employed month without absences, of a
        worker whose exclusion is known, in a sector with a sourced day
        count.
    """
    reasons = (
        (
            bool(rule.exempt_categories) and position.category is None,
            MinimumBaseReason.CATEGORY_UNKNOWN,
        ),
        (position.adds_to_month, MinimumBaseReason.PAY_ADDED_TO_MONTH),
        (position.span is not None, MinimumBaseReason.PARTIAL_MONTH),
        (position.absence, MinimumBaseReason.ABSENCE_IN_MONTH),
        (rule.monthly_days is None, MinimumBaseReason.MONTHLY_DAYS_UNSOURCED),
    )
    return next((reason for applies, reason in reasons if applies), None)


def _month_minimum(
    rule: MinimumBaseRule, position: MonthPosition
) -> Decimal | MinimumBaseReason:
    """Return the minimum of a fully employed month without absences.

    Returns:
        The daily minimum times the days of the month for full time, the
        hourly minimum times the hours of the month for part time (the
        weekly hours over the days of a month of normal weeks), or the
        reason the bundle cannot fix it.
    """
    reason = _undetermined_reason(rule, position)
    days = rule.monthly_days
    if reason is not None or days is None:
        return reason or MinimumBaseReason.MONTHLY_DAYS_UNSOURCED
    part_time = position.part_time
    if part_time is None:
        return money(rule.daily * days)
    hours, full = part_time
    hourly = rule.hourly_for(full)
    if hourly is None:
        return MinimumBaseReason.HOURLY_MINIMUM_UNSOURCED
    return money(hourly * hours * days / rule.week_days)


def _resolve(
    rule: MinimumBaseRule, actual: Decimal, position: MonthPosition
) -> MinimumBase:
    """Return the minimum of the INPS base of a run, without its source.

    Returns:
        The minimum of :func:`resolve_minimum_base`, ``source`` left unset.
    """
    excluded = _exclusion(rule, position)
    if excluded is not None:
        return MinimumBase(actual, actual, excluded)
    bound = _bound(rule, position)
    compared = position.month_pay if position.adds_to_month else actual
    if compared >= bound:
        return MinimumBase(actual, bound, MinimumBaseReason.ABOVE_MINIMUM)
    minimum = _month_minimum(rule, position)
    if isinstance(minimum, MinimumBaseReason):
        return MinimumBase(actual, bound, minimum)
    reason = (
        MinimumBaseReason.RAISED_TO_MINIMUM
        if actual < minimum
        else MinimumBaseReason.ABOVE_MINIMUM
    )
    return MinimumBase(actual, bound, reason, minimum)


def resolve_minimum_base(
    rule: MinimumBaseRule, actual: Decimal, position: MonthPosition
) -> MinimumBase:
    """Return the minimum of the INPS base of a run.

    The highest minimum the month can have is the daily minimum times the
    days of a fully paid month (27, the most days of a six-day week a month
    holds, when the count is not sourced; the days of a six-day week in the
    employed span when fewer), scaled to the part-time ratio: fewer paid days only
    lower it.  A base at or above it needs no day count.  A run that adds
    pay to a month is compared on the monthly pay of the worker instead.

    Args:
        rule: Minimum base rule of the year and sector.
        actual: INPS base of the run, pay chain and events.
        position: What the run pays of its month.

    Returns:
        The minimum, the reason, and the base it gives.
    """
    source = None if rule.provenance is None else rule.provenance.location
    return replace(_resolve(rule, actual, position), source=source)
