"""Qualification of extra-month ratei at the termination of an employment.

The days of absences that suspend accrual do not count towards a month,
and an extra month whose next payment falls outside the employment is
liquidated on the regular run of the termination month.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.accrual import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    absence_days,
)
from ccnl_engine.payroll.domain.events import AbsenceEvent
from ccnl_engine.payroll.domain.run import PayrollRun

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine.payroll.domain.accrual import MonthAccrualRule
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.events import WorkEvent

__all__ = ["non_accruing_days", "termination_settlements"]


def non_accruing_days(events: Iterable[WorkEvent]) -> frozenset[date]:
    """Return the days of the year's absences that suspend accrual.

    Args:
        events: Every event of the year, of any run.

    Returns:
        Every calendar day of an :class:`AbsenceEvent` with
        ``suspends_accrual`` set.
    """
    days: set[date] = set()
    for event in events:
        if isinstance(event, AbsenceEvent) and event.suspends_accrual:
            last = event.end_date or event.event_date
            days |= absence_days(event.event_date, last)
    return frozenset(days)


def termination_settlements(
    calendar: WorkCalendar,
    employment_period: EmploymentPeriod | None,
    non_accruing_days: frozenset[date],
    rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
) -> dict[str, tuple[ExtraMonthAccrual, ...]]:
    """Return the ratei the last run of an employment ending this year pays.

    An extra month whose next payment after the termination month falls
    outside the employment is liquidated on the regular run of the
    termination month.  Its window is the one of that next payment (the
    following year when the payment month precedes the termination month),
    clipped to the hire date and counted up to the termination date with
    ``rule``.

    Returns:
        The accruals keyed by the ``run_id`` of the termination month's
        regular run, empty when the employment does not end in the year.
    """
    if employment_period is None or employment_period.ended_on is None:
        return {}
    ended_on = employment_period.ended_on
    if ended_on.year != calendar.year:
        return {}
    accruals = tuple(
        ExtraMonthAccrual.of(
            extra,
            calendar.year + (1 if extra.payment_month < ended_on.month else 0),
            employment_period,
            non_accruing_days=non_accruing_days,
            rule=rule,
        )
        for extra in calendar.extra_months
        if extra.payment_month != ended_on.month
    )
    return {PayrollRun.regular(calendar.year, ended_on.month).run_id: accruals}
