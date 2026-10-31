"""Handler of the daily rests of the first year of a child.

The run deducts the hours of rest of its month at the CCNL hourly base
(:mod:`~ccnl_engine.absence.insured.hours.rules`) and pays them back in
full as the INPS indemnity the employer advances (D.Lgs. 151/2001 art. 43
c. 1), posted as ``maternity_item``: out of the INPS base, the rests
covered by figurative contributions (art. 44 c. 1).  The TFR base keeps
them: art. 39 c. 2 counts them as hours worked for the pay.  Where the
engine cannot derive the hourly base the hours post nothing, with the
``incomplete`` issue ``nursing_rest_hours_underived`` and an ``incomplete``
decision of the same reason.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

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
    from ccnl_engine.absence.insured.rest.inputs import NursingRestEvent
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = ["RESTS", "RESTS_UNDERIVED", "_handle_nursing_rest"]

#: Capability of the daily rests of the first year of a child.
RESTS = "nursing_rests"
#: Hours of rest whose CCNL hourly base the engine cannot derive.
RESTS_UNDERIVED = "nursing_rest_hours_underived"
_ZERO = Decimal(0)


def _handle_nursing_rest(event: NursingRestEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Pay the hours of rest in the month of the run.

    Returns:
        The items, entries, base deltas, decision and issues of the rests.
    """
    terms = ctx.insured
    span = _span(event, terms, RESTS)
    if terms is None or terms.pay is None:
        return _no_quota(RESTS)
    hours = event.hours_within(*span)
    pay = hours_pay(event.hours, span, ctx.hourly, RESTS, RESTS_UNDERIVED)
    issues = []
    if isinstance(pay, CalculationIssue):
        issues, hours, pay = [pay], _ZERO, _ZERO
    indemnity = money(terms.rates.nursing_rest.indemnity_rate * pay)
    days = len([i for i in event.hours if span[0] <= i.day <= span[1]])
    insured = InsuredPay(hours, pay, indemnity, days)
    effect = post_lines(
        (
            ("abs", -pay, _INTEGRATION, hours),
            ("inps", indemnity, "maternity_item", hours),
        ),
        ctx,
    )
    decision = _decision(RESTS, terms, span, insured, modelled=True, advanced=True)
    if issues:
        incomplete = CalculationStatus.INCOMPLETE
        decision = replace(decision, status=incomplete, reason_code=RESTS_UNDERIVED)
    effect.decisions = [decision]
    effect.issues = issues
    return effect
