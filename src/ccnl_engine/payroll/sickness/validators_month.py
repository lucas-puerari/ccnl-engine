"""Checks of the sick days of a month against its pay and its other absences.

The sick days are deducted with the CCNL daily quota of an unpaid absence
(:mod:`._sickness_pay`); the monthly pay is a fixed amount whatever the
days of the month.  The two agree only when the payable days of the month
match the divisor.  No CCNL text the bundle holds says how a month of
sickness is deducted when they do not, so the run raises a provisional
issue instead of a silent amount:

- every payable day of the employed span is a sick day, yet the deduction
  is less than the pay the run posts: the pay of days nobody worked is left
  (24 Mondays to Saturdays of a February by 26);
- a payable day is worked, yet the deduction reaches the pay the run
  posts: the worked days are left unpaid (sick 1 to 30 of a 31-day month by
  30, day 31 counting as day 30; 26 sick days of a 27-day month by 26).

An unpaid :class:`~ccnl_engine.payroll.event.facade.AbsenceEvent` on a sick
day counts the day twice and is rejected.  On other days of the month it is
deducted at the caller's hourly rate, the sick days at the CCNL daily
quota: the two do not add up to the month on any rule, so the run raises a
provisional issue.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.amount.rules_proration import payable_days
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.event.facade import AbsenceEvent
from ccnl_engine.payroll.sickness.models import SicknessEpisode

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.payroll.event.facade import WorkEvent
    from ccnl_engine.payroll.sickness.rules_terms import (
        DailyQuota,
        SicknessTerms,
    )

__all__ = [
    "QUOTA_MISMATCH",
    "WITH_UNPAID_ABSENCE",
    "check_absences_off_sick_days",
    "month_issues",
]

#: The daily quota of the sick days does not match the pay of the month.
QUOTA_MISMATCH = "sickness_month_quota_mismatch"
#: Sick days and an unpaid absence deducted with different quotas.
WITH_UNPAID_ABSENCE = "sickness_with_unpaid_absence"


def _days(first: date, last: date) -> Iterator[date]:
    for step in range((last - first).days + 1):
        yield first + timedelta(days=step)


def check_absences_off_sick_days(events: tuple[WorkEvent, ...]) -> None:
    """Reject an unpaid absence on a day of a sickness episode of the run.

    Raises:
        InvalidInputError: When an absence and an episode share a day.
    """
    episodes = [e for e in events if isinstance(e, SicknessEpisode)]
    for absence in (e for e in events if isinstance(e, AbsenceEvent)):
        last = absence.end_date or absence.event_date
        for episode in episodes:
            if episode.within(absence.event_date, last) is not None:
                msg = (
                    f"AbsenceEvent from {absence.event_date} to {last} falls on "
                    f"days of sickness episode '{episode.episode_id}': a sick "
                    "day is not an unpaid absence"
                )
                raise InvalidInputError(
                    msg, field="AbsenceEvent.event_date", feature="sickness"
                )


def _posted_units(employed: tuple[date, date], quota: DailyQuota) -> Decimal:
    """Return the units of the monthly pay the run posts.

    Returns:
        The divisor for a whole month, the payable units of a partial one
        up to the divisor.
    """
    first, last = employed
    month_end = calendar.monthrange(last.year, last.month)[1]
    if first.day == 1 and last.day == month_end:
        return quota.divisor
    units = Decimal(payable_days(quota.method, first, last))
    return min(units * (quota.daily_hours or Decimal(1)), quota.divisor)


def _quota_issue(
    employed: tuple[date, date],
    quota: DailyQuota,
    sick: frozenset[date],
    deducted: Decimal,
) -> CalculationIssue | None:
    """Return the issue of a deduction that does not match the days worked.

    Returns:
        The issue, ``None`` when the deduction matches.
    """
    worked = any(
        day not in sick and payable_days(quota.method, day, day)
        for day in _days(*employed)
    )
    posted = _posted_units(employed, quota)
    if worked == (deducted < posted):
        return None
    what = (
        "a day is worked, yet the sick days deduct the whole pay"
        if worked
        else "every payable day is a sick day, yet part of the pay is left"
    )
    return CalculationIssue(
        code=QUOTA_MISMATCH,
        message=(
            f"the sick days of {employed[0]:%B %Y} deduct {deducted} of the "
            f"{posted} units of the pay posted ({quota.method.value}): {what}; "
            "the CCNL data do not say how such a month is deducted"
        ),
        status=CalculationStatus.PROVISIONAL,
    )


def month_issues(
    events: tuple[WorkEvent, ...],
    terms: SicknessTerms,
    sick: frozenset[date],
    deducted: Decimal,
) -> tuple[CalculationIssue, ...]:
    """Return the issues of the sick days of the run as a whole.

    Args:
        events: The events of the run.
        terms: What the run pays sickness with.
        sick: The sick days within the comporto the run paid.
        deducted: Units of the monthly pay they deducted.

    Returns:
        The quota mismatch and the unpaid absence issues that hold.
    """
    employed, quota = terms.employed, terms.quota
    if not sick or employed is None or quota is None:
        return ()
    issues: list[CalculationIssue] = []
    mismatch = _quota_issue(employed, quota, sick, deducted)
    if mismatch is not None:
        issues.append(mismatch)
    if any(isinstance(e, AbsenceEvent) for e in events):
        issues.append(
            CalculationIssue(
                code=WITH_UNPAID_ABSENCE,
                message=(
                    "the run deducts sick days at the CCNL daily quota and an "
                    "unpaid absence at the hourly rate given: together they "
                    "do not count the days of the month on one rule"
                ),
                status=CalculationStatus.PROVISIONAL,
            )
        )
    return tuple(issues)
