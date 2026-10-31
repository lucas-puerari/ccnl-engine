"""Handler of a parental leave taken by the hour: deduction and indemnity.

As the leave by the day (:mod:`~ccnl_engine.absence.insured.parental.\
handlers`), the run deducts the hours of its month as an unpaid absence,
out of the INPS and TFR bases, at the CCNL hourly base of their day
(:mod:`~ccnl_engine.absence.insured.hours.rules`), and pays back the INPS
indemnity, half the daily base at the rate of each day (art. 34 c. 1 D.Lgs.
151/2001; INPS circ. 152/2015 par. 2.2).  A collective rule on the hours
that make a day of leave prevails over the general criterion of art. 32 c.
1-ter; the bundle holds none, so the run records the open engine
limitation ``parental_hourly_ccnl_rule``.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.base.rules import leave_base, run_daily_base
from ccnl_engine.absence.insured.handlers import (
    _decision,
    _no_quota,
    _not_modelled,
    _span,
)
from ccnl_engine.absence.insured.hours.rules import hours_pay
from ccnl_engine.absence.insured.parental.handlers import (
    PARENTAL,
    PARENTAL_BASE_LIMITATION,
    PARENTAL_BASE_UNKNOWN,
    PARENTAL_EXTRA_MONTH_LIMITATION,
    PARENTAL_INCOME_LIMITATION,
    _cohort_issue,
)
from ccnl_engine.absence.insured.parental.hourly.rules import (
    allocate_hours,
    hours_indemnity,
)
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.parental.hourly.inputs import (
        HourlyParentalLeaveEvent,
    )
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = ["HOURLY_CCNL_LIMITATION", "HOURS_UNDERIVED", "_handle_hourly_parental"]

#: The collective rule on the hours of a day of leave is not in the bundle.
HOURLY_CCNL_LIMITATION = "parental_hourly_ccnl_rule"
#: Hours of leave whose CCNL hourly base the engine cannot derive.
HOURS_UNDERIVED = "parental_hours_underived"
_DEDUCTION = "absence_deduction"
_ZERO = Decimal(0)
_HALF = Decimal(2)


def _handle_hourly_parental(
    event: HourlyParentalLeaveEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days of leave by the hour in the month of the run.

    Returns:
        The items, entries, base deltas, decision, issues and limitations.
    """
    terms = ctx.insured
    span = _span(event, terms, PARENTAL)
    if terms is None or terms.pay is None:
        return _no_quota(PARENTAL)
    rates = terms.rates.parental
    days, unknown = allocate_hours(event, rates)
    base = leave_base(
        event.parental_base_pay,
        terms,
        event.event_date,
        capability=PARENTAL,
        field="HourlyParentalLeaveEvent.parental_base_pay",
        code=PARENTAL_BASE_UNKNOWN,
        limitation=PARENTAL_BASE_LIMITATION,
    )
    daily = base.rmgg
    if daily is None:
        daily = run_daily_base(terms.pay, rates.daily_divisor)
    hours = event.hours_within(*span)
    in_span = [day for day in days if span[0] <= day <= span[1]]
    deduction = hours_pay(event.hours, span, ctx.hourly, PARENTAL, HOURS_UNDERIVED)
    issues: list[CalculationIssue] = [_not_modelled(PARENTAL), *base.issues]
    if isinstance(deduction, CalculationIssue):
        issues.append(deduction)
        hours, deduction = _ZERO, _ZERO
    indemnity = hours_indemnity(days, *span, daily)
    effect = post_lines(
        (
            ("abs", -deduction, _DEDUCTION, hours),
            ("inps", indemnity, "maternity_item", Decimal(len(in_span)) / _HALF),
        ),
        ctx,
    )
    pay = InsuredPay(hours, deduction, indemnity, len(in_span))
    decision = _decision(PARENTAL, terms, span, pay, modelled=False, advanced=True)
    if any(i.code == HOURS_UNDERIVED for i in issues):
        incomplete = CalculationStatus.INCOMPLETE
        decision = replace(decision, status=incomplete, reason_code=HOURS_UNDERIVED)
    effect.decisions = [decision]
    if unknown:
        issues.append(_cohort_issue())
    effect.issues = issues
    limitations = [*base.limitations, PARENTAL_EXTRA_MONTH_LIMITATION]
    if any(days[day] is None for day in in_span):
        limitations.append(PARENTAL_INCOME_LIMITATION)
    effect.limitations = (*limitations, HOURLY_CCNL_LIMITATION)
    return effect
