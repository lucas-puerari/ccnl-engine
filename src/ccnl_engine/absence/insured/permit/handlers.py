"""Handler of the permits to assist a disabled person: deduction and indemnity.

The run deducts the days of permit of its month at the CCNL daily quota and
pays them back in full as the INPS indemnity the employer advances (art. 43
D.Lgs. 151/2001), posted as ``maternity_item``: out of the INPS base, the
days covered by figurative contributions (art. 44 c. 2).  The deduction
keeps the TFR base, as payroll practice holds for these permits: the days
are paid and counted in the seniority (L. 104/1992 art. 33 c. 4, D.Lgs.
151/2001 artt. 43 and 34 c. 5), by the maintainer's decision of
2026-11-15 (the resolved engine limitation ``disability_permit_tfr``).

An hour of permit is paid as :mod:`~ccnl_engine.absence.insured.hours.rules`
says.  Where the engine cannot derive its base the hours post nothing: the
run records the ``incomplete`` issue
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
from ccnl_engine.absence.insured.hours.rules import hours_pay
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = [
    "HOURS_UNDERIVED",
    "PERMITS",
    "_handle_disability_permit",
]

#: Capability of the permits to assist a disabled person.
PERMITS = "disability_permits"
#: Hours of permit whose CCNL hourly base the engine cannot derive.
HOURS_UNDERIVED = "disability_permit_hours_underived"
_ZERO = Decimal(0)


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
    hour_pay = hours_pay(event.hours, span, ctx.hourly, PERMITS, HOURS_UNDERIVED)
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
    return effect
