"""Handler of a compulsory paternity leave: deduction and INPS indemnity.

The run deducts the days of leave of its month at the CCNL daily quota and
pays back the INPS indemnity, 100% of the pay of the month before the leave
(art. 29 D.Lgs. 151/2001), advanced by the employer like the maternity
indemnity and posted as ``maternity_item``: outside the INPS and TFR bases.
No CCNL top-up: the indemnity is already the whole pay.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.base.rules import leave_base
from ccnl_engine.absence.insured.handlers import (
    _INTEGRATION,
    _decision,
    _no_quota,
    _span,
)
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import paternity_pay

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.inputs import PaternityLeaveEvent
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = [
    "PATERNITY",
    "PATERNITY_BASE_LIMITATION",
    "PATERNITY_BASE_UNKNOWN",
    "_handle_paternity_leave",
]

#: Capability of a compulsory paternity leave.
PATERNITY = "paternity_leave"
#: INPS pays a paternity indemnity and the leave states no base.
PATERNITY_BASE_UNKNOWN = "paternity_base_pay_unknown"
#: Paternity paid on the pay of the run: the base of art. 23 is not computed.
PATERNITY_BASE_LIMITATION = "paternity_daily_base"


def _handle_paternity_leave(
    event: PaternityLeaveEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days of the paternity leave in the month of the run.

    Returns:
        The items, entries, base deltas, decision and issues of the leave.
    """
    terms = ctx.insured
    span = _span(event, terms, PATERNITY)
    if terms is None or terms.pay is None:
        return _no_quota(PATERNITY)
    base = leave_base(
        event.paternity_base_pay,
        terms,
        event.started_on,
        capability=PATERNITY,
        field="PaternityLeaveEvent.paternity_base_pay",
        code=PATERNITY_BASE_UNKNOWN,
        limitation=PATERNITY_BASE_LIMITATION,
    )
    days = event.days_within(*span)
    pay = paternity_pay(days, terms.pay, terms.rates.paternity, base.rmgg)
    effect = post_lines(
        (
            ("abs", -pay.deduction, _INTEGRATION, pay.units),
            ("inps", pay.indemnity, "maternity_item", Decimal(pay.days)),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(PATERNITY, terms, span, pay, modelled=True, advanced=True)
    ]
    effect.issues = list(base.issues)
    effect.limitations = base.limitations
    return effect
