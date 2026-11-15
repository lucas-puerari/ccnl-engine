"""Handler of a parental leave taken by the hour: deduction and indemnity.

As the leave by the day (:mod:`~ccnl_engine.absence.insured.parental.\
handlers`), the run deducts the hours of its month as an unpaid absence,
out of the INPS and TFR bases, at the CCNL hourly base of their day
(:mod:`~ccnl_engine.absence.insured.hours.rules`), and pays back the INPS
indemnity, half the daily base at the rate of each day (art. 34 c. 1 D.Lgs.
151/2001; INPS circ. 152/2015 par. 2.2).  A collective rule on the hours
that make a day of leave prevails over the general criterion of art. 32 c.
1-ter: the CCNL hours in force on the first day of leave make the days of
leave (``work_rules.parental_hourly``), and the run records the open engine
limitation ``parental_hourly_ccnl_rule`` while the bundle does not record
the rule of the CCNL.
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
from ccnl_engine.absence.insured.parental.hourly.agreement import agreement_issue
from ccnl_engine.absence.insured.parental.hourly.rules import (
    allocate_hours,
    hourly_top_up,
    hours_indemnity,
)
from ccnl_engine.absence.insured.parental.income import income_check
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.parental.hourly.inputs import (
        HourlyParentalLeaveEvent,
    )
    from ccnl_engine.absence.insured.parental.hourly.models import (
        ParentalHourlyClause,
    )
    from ccnl_engine.absence.insured.services import InsuredTerms
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = ["HOURLY_CCNL_LIMITATION", "HOURS_UNDERIVED", "_handle_hourly_parental"]

#: The collective rule on the hours of a day of leave is not in the bundle.
HOURLY_CCNL_LIMITATION = "parental_hourly_ccnl_rule"
#: Hours of leave whose CCNL hourly base the engine cannot derive.
HOURS_UNDERIVED = "parental_hours_underived"
_DEDUCTION = "absence_deduction"
_ZERO = Decimal(0)


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
    days, unknown = allocate_hours(event, rates, _day_hours(event, terms))
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
    in_span = [day for day in days.pieces if span[0] <= day <= span[1]]
    deduction = hours_pay(event.hours, span, ctx.hourly, PARENTAL, HOURS_UNDERIVED)
    rule = None if terms.rules is None else terms.rules.parental
    issues: list[CalculationIssue] = [
        *([] if rule is not None else [_not_modelled(PARENTAL)]),
        *base.issues,
    ]
    if isinstance(deduction, CalculationIssue):
        issues.append(deduction)
        hours, deduction = _ZERO, _ZERO
    indemnity = hours_indemnity(days, *span, daily)
    missing_counter = rule is not None and event.topped_up_days_before is None
    integration, topped_up = hourly_top_up(
        event, days, span, daily, rule, rates.indemnity_rate
    )
    effect = post_lines(
        (
            ("abs", -deduction, _DEDUCTION, hours),
            ("inps", indemnity, "maternity_item", days.leave_days(*span)),
            ("intg", integration, "absence_integration_item", topped_up),
        ),
        ctx,
    )
    pay = InsuredPay(hours, deduction, indemnity, len(in_span), integration)
    decision = _decision(
        PARENTAL,
        terms,
        span,
        pay,
        modelled=rule is not None and not missing_counter,
        advanced=True,
    )
    if any(i.code == HOURS_UNDERIVED for i in issues):
        incomplete = CalculationStatus.INCOMPLETE
        decision = replace(decision, status=incomplete, reason_code=HOURS_UNDERIVED)
    effect.decisions = [decision]
    if missing_counter:
        issues.append(
            CalculationIssue(
                code="parental_top_up_history_unknown",
                message=(
                    "HourlyParentalLeaveEvent.topped_up_days_before is required "
                    "to cap the CCNL supplement across runs; no top-up is posted"
                ),
                status=CalculationStatus.INCOMPLETE,
                capability=PARENTAL,
                fact="topped_up_days_before",
                cause=IssueCause.FACT,
            )
        )
    if unknown:
        issues.append(_cohort_issue())
    issue, unpublished = income_check(
        days.rates(), in_span, event.individual_income, PARENTAL
    )
    local = agreement_issue(event.local_hourly_agreement, PARENTAL)
    effect.issues = [*issues, *(i for i in (issue, local) if i is not None)]
    effect.limitations = _limitations(
        base.limitations,
        terms.hourly_clause,
        unpublished=unpublished,
    )
    return effect


def _limitations(
    base: tuple[str, ...],
    clause: ParentalHourlyClause | None,
    *,
    unpublished: bool,
) -> tuple[str, ...]:
    """Return the limitations of the leave by the hour of the run.

    Returns:
        Those of the daily base and of the indemnified months; the income
        threshold when it is not published; the CCNL rule while the bundle
        does not record it.
    """
    limitations = [*base, PARENTAL_EXTRA_MONTH_LIMITATION]
    if unpublished:
        limitations.append(PARENTAL_INCOME_LIMITATION)
    if clause is None:
        limitations.append(HOURLY_CCNL_LIMITATION)
    return tuple(limitations)


def _day_hours(event: HourlyParentalLeaveEvent, terms: InsuredTerms) -> Decimal | None:
    """Return the hours of a day of leave the CCNL sets for ``event``.

    Returns:
        The CCNL hours in force on the first day of leave, scaled by the
        part-time ratio when the CCNL scales them; the average daily hours
        of a CCNL that regulates the leave without them; ``None`` for the
        general criterion.
    """
    clause = terms.hourly_clause
    if clause is None or clause.criterion_on(event.hours[0].day):
        return None
    if clause.day_hours is None:
        return event.average_daily_hours
    ratio = terms.part_time
    if not clause.part_time_scaled or ratio is None:
        return clause.day_hours
    return clause.day_hours * ratio
