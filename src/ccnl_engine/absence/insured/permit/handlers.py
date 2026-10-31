"""Handler of the permits to assist a disabled person: deduction and indemnity.

The run deducts the days of permit of its month at the CCNL daily quota and
pays them back in full as the INPS indemnity the employer advances (art. 43
D.Lgs. 151/2001), posted as ``maternity_item``: out of the INPS base, the
days covered by figurative contributions (art. 44 c. 2).  The deduction
keeps the TFR base, as payroll practice holds for these permits; art. 2120
c. 3 c.c. does not list them, so the run records the open engine
limitation ``disability_permit_tfr``.

An hour of permit is the hourly base of the CCNL on its day
(:class:`~ccnl_engine.working_time.hourly.policies.HourlyTerms`), deducted
and paid back alike.  Where the engine cannot derive that base the hours
post nothing: the run records the ``incomplete`` issue
``disability_permit_hours_underived`` naming the reason, and the decision
of the permits is ``incomplete`` with the same reason.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.days.rules import deducted_days
from ccnl_engine.absence.insured.handlers import (
    _INTEGRATION,
    _decision,
    _no_quota,
    _span,
)
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx
    from ccnl_engine.working_time.hourly.policies import HourlyTerms

__all__ = [
    "HOURS_UNDERIVED",
    "PERMITS",
    "PERMIT_TFR_LIMITATION",
    "_handle_disability_permit",
]

#: Capability of the permits to assist a disabled person.
PERMITS = "disability_permits"
#: The TFR base keeps the permit days on payroll practice, not on a source.
PERMIT_TFR_LIMITATION = "disability_permit_tfr"
#: Hours of permit whose CCNL hourly base the engine cannot derive.
HOURS_UNDERIVED = "disability_permit_hours_underived"
_ZERO = Decimal(0)
_BASE_FIELD = "the hourly base of PermitHours.hours"


def _hour_pay(
    event: DisabilityPermitEvent, span: tuple[date, date], hourly: HourlyTerms
) -> Decimal | CalculationIssue:
    """Return the pay of the hours of permit in ``span``, or why not.

    Returns:
        Each hour at the CCNL hourly base of its day, rounded once; the
        ``incomplete`` issue when a base cannot be derived.
    """
    total = _ZERO
    for item in event.hours:
        if not span[0] <= item.day <= span[1]:
            continue
        try:
            base = hourly.base(item.day, _BASE_FIELD, PERMITS)
        except InvalidInputError as error:
            return CalculationIssue(
                code=HOURS_UNDERIVED,
                message=f"the hours of permit post nothing: {error}",
                status=CalculationStatus.INCOMPLETE,
                capability=PERMITS,
                cause=IssueCause.RULE,
            )
        total += base.rate * item.hours
    return money(total)


def _handle_disability_permit(
    event: DisabilityPermitEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days and hours of permit in the month of the run.

    Returns:
        The items, entries, base deltas, decision, issues and limitation
        of the permits.
    """
    terms = ctx.insured
    span = _span(event, terms, PERMITS)
    if terms is None or terms.pay is None:
        return _no_quota(PERMITS)
    days = event.days_within(*span)
    units, deduction = deducted_days(terms.pay, days)
    rate = terms.rates.disability_permit.indemnity_rate
    indemnity = money(rate * deduction)
    hours = event.hours_within(*span)
    hour_pay = _hour_pay(event, span, ctx.hourly)
    issues = []
    if isinstance(hour_pay, CalculationIssue):
        issues, hours, hour_pay = [hour_pay], _ZERO, _ZERO
    hour_indemnity = money(rate * hour_pay)
    pay = InsuredPay(units, deduction + hour_pay, indemnity + hour_indemnity, len(days))
    effect = post_lines(
        (
            ("abs", -deduction, _INTEGRATION, units),
            ("inps", indemnity, "maternity_item", Decimal(len(days))),
            ("abshours", -hour_pay, _INTEGRATION, hours),
            ("inpshours", hour_indemnity, "maternity_item", hours),
        ),
        ctx,
    )
    decision = _decision(PERMITS, terms, span, pay, modelled=True, advanced=True)
    if issues:
        incomplete = CalculationStatus.INCOMPLETE
        decision = replace(decision, status=incomplete, reason_code=HOURS_UNDERIVED)
    effect.decisions = [decision]
    effect.issues = issues
    effect.limitations = (PERMIT_TFR_LIMITATION,)
    return effect
