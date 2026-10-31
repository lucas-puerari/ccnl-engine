"""Monthly accrual of ferie and permits under the leave rules of a CCNL.

A regular run credits its competence month: a twelfth of the yearly days
of ferie and of the yearly hours of each permit bucket, when the month is
credited under the month rule of the bucket
(:class:`~ccnl_engine.leave.models.MonthCredit`).  The days of the month
served are the days of the employment within it, less the days of the
absences that suspend the accrual.  The credit is kept in twelfths (the
yearly entitlement itself), so the accrual of a year is exact.

What the accrual cannot tell from the request is not guessed silently: a
month fraction under a bucket whose month rule the text leaves open
accrues nothing, an unknown seniority gives the days of the default tier,
an unknown hire date the first step of a new-hire ramp, an absence whose
effect on the accrual is not stated counts as served; each of them marks
the balance inexact (:attr:`~ccnl_engine.leave.balance.models.LeaveBalance.exact`).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.leave.types import LeaveBucket

if TYPE_CHECKING:
    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.leave.balance.models import LeaveAccount
    from ccnl_engine.leave.models import LeaveRules
    from ccnl_engine.leave.permit.models import PermitRules
    from ccnl_engine.leave.types import MonthCredit

__all__ = ["AccrualFacts", "MonthService", "accrue_month", "month_service"]

_ZERO = Decimal(0)
_ONE = Decimal(1)


@dataclass(frozen=True)
class MonthService:
    """Days of a month the worker served toward the leave accrual.

    Attributes:
        served: Days of the employment in the month, less the days of the
            absences that suspend the accrual.
        days: Calendar days of the month.
        known: Whether every absence of the month states its effect on the
            accrual.
    """

    served: int
    days: int
    known: bool = True

    @property
    def whole(self) -> bool:
        """Whether the worker served every day of the month."""
        return self.served >= self.days


@dataclass(frozen=True)
class AccrualFacts:
    """Facts of a run the accrual of its month reads.

    Attributes:
        year: Competence year of the run.
        month: Competence month of the run.
        service: Days of the month served.
        headcount: Employees of the employer.
        hired_on: First day of the employment, ``None`` when not stated.
        seniority_months: Months of recognised service, ``None`` when not
            known.
        part_time_ratio: Weekly hours over the full-time hours of a part
            time worker, ``None`` for a full-time worker.
    """

    year: int
    month: int
    service: MonthService
    headcount: int
    hired_on: date | None = None
    seniority_months: int | None = None
    part_time_ratio: Decimal | None = None

    @property
    def last_day(self) -> date:
        """Last day of the competence month."""
        return date(self.year, self.month, self.service.days)

    def months_since_hire(self) -> int | None:
        """Return the whole months from the hire to the end of the month.

        Returns:
            The months completed on the last day of the competence month,
            ``None`` without a hire date.
        """
        hired = self.hired_on
        if hired is None:
            return None
        end = self.last_day
        months = (end.year - hired.year) * 12 + end.month - hired.month
        return months if end.day >= hired.day else months - 1


def month_service(
    year: int,
    month: int,
    period: EmploymentPeriod | None,
    suspended: frozenset[date],
    *,
    known: bool,
) -> MonthService:
    """Return the days of a month served toward the leave accrual.

    Args:
        year: Year of the month.
        month: The month.
        period: The employment, ``None`` when not stated: every day counts.
        suspended: Days of absences that suspend the accrual.
        known: Whether every absence states its effect on the accrual.

    Returns:
        The days served and the days of the month.
    """
    days = calendar.monthrange(year, month)[1]
    first, last = date(year, month, 1), date(year, month, days)
    if period is not None:
        first = max(first, period.started_on)
        last = last if period.ended_on is None else min(last, period.ended_on)
    employed = max(0, (last - first).days + 1)
    off = sum(1 for day in suspended if first <= day <= last)
    return MonthService(served=max(0, employed - off), days=days, known=known)


def _credit(rule: MonthCredit | None, service: MonthService) -> tuple[bool, bool]:
    """Return whether the month accrues, and whether that is exact.

    Returns:
        ``(credited, exact)``: a whole month always accrues; a month
        fraction follows ``rule``, and accrues nothing, inexactly, without
        one.
    """
    if service.whole:
        return True, service.known
    if rule is None:
        return False, False
    return rule.credits(service.served, service.days), service.known


def _ferie(rules: LeaveRules, facts: AccrualFacts) -> tuple[Decimal, bool] | None:
    """Return the twelfths of ferie the month accrues, and whether exact.

    Returns:
        ``None`` when the CCNL states no accrual of the ferie.
    """
    accrual = rules.ferie_accrual
    if accrual is None:
        return None
    credited, exact = _credit(accrual.month_credit, facts.service)
    day = facts.last_day
    days = rules.annual_days(facts.seniority_months, day)
    known = facts.seniority_months is not None or not rules.days_depend_on_seniority(
        day
    )
    return (days if credited else _ZERO), exact and known


def _permit(permit: PermitRules, facts: AccrualFacts) -> tuple[Decimal, bool]:
    """Return the twelfths of a permit bucket the month accrues, and whether exact.

    Returns:
        The yearly hours of the employer size, times the share of a new
        hire and the part-time ratio, when the month is credited.
    """
    credited, exact = _credit(permit.month_credit, facts.service)
    hours = permit.hours_for(facts.headcount)
    ramp = permit.ramp
    if ramp is not None and ramp.covers(facts.headcount):
        months = facts.months_since_hire()
        if facts.hired_on is None or months is None:
            hours *= ramp.steps[0].share
            exact = False
        else:
            hours *= ramp.share(facts.hired_on, months)
    if facts.part_time_ratio is not None:
        hours *= facts.part_time_ratio
    return (hours if credited else _ZERO), exact


def accrue_month(
    account: LeaveAccount, rules: LeaveRules, facts: AccrualFacts
) -> LeaveAccount:
    """Return ``account`` with the leave the month of ``facts`` accrues.

    Returns:
        The account with every bucket of ``rules`` credited for the month,
        a bucket left at zero when the month does not accrue.
    """
    credited: list[tuple[LeaveBucket, tuple[Decimal, bool]]] = []
    ferie = _ferie(rules, facts)
    if ferie is not None:
        credited.append((LeaveBucket.FERIE, ferie))
    credited.extend((p.bucket, _permit(p, facts)) for p in rules.permits)
    for bucket, (twelfths, exact) in credited:
        account = account.credited(bucket, facts.year, twelfths, exact=exact)
    return account
