"""Handler of the permits to assist a disabled person: deduction and indemnity.

The run deducts the days of permit of its month at the CCNL daily quota and
pays them back in full as the INPS indemnity the employer advances (art. 43
D.Lgs. 151/2001), posted as ``maternity_item``: out of the INPS base, the
days covered by figurative contributions (art. 44 c. 2).  The deduction
keeps the TFR base, as payroll practice holds for these permits; art. 2120
c. 3 c.c. does not list them, so the run records the open engine
limitation ``disability_permit_tfr``.
"""

from __future__ import annotations

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
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = ["PERMITS", "PERMIT_TFR_LIMITATION", "_handle_disability_permit"]

#: Capability of the permits to assist a disabled person.
PERMITS = "disability_permits"
#: The TFR base keeps the permit days on payroll practice, not on a source.
PERMIT_TFR_LIMITATION = "disability_permit_tfr"


def _handle_disability_permit(
    event: DisabilityPermitEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days of permit in the month of the run.

    Returns:
        The items, entries, base deltas, decision and limitation of the
        permits.
    """
    terms = ctx.insured
    span = _span(event, terms, PERMITS)
    if terms is None or terms.pay is None:
        return _no_quota(PERMITS)
    days = event.days_within(*span)
    units, deduction = deducted_days(terms.pay, days)
    indemnity = money(terms.rates.disability_permit.indemnity_rate * deduction)
    pay = InsuredPay(units, deduction, indemnity, len(days))
    effect = post_lines(
        (
            ("abs", -pay.deduction, _INTEGRATION, pay.units),
            ("inps", pay.indemnity, "maternity_item", Decimal(pay.days)),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(PERMITS, terms, span, pay, modelled=True, advanced=True)
    ]
    effect.limitations = (PERMIT_TFR_LIMITATION,)
    return effect
