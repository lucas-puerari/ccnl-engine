"""Handler for structured sick-leave episodes (SicknessCaseEvent)."""

from __future__ import annotations

from ccnl_engine.payroll.application._event_items import _process_sickness_case_event
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.events import SicknessCaseEvent


def _handle_sickness_case(
    event: SicknessCaseEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle structured sick-leave episodes.

    Returns:
        Handler result with sickness items, ledger entries, and INPS/TFR/IRPEF deltas.
    """
    sc_items, sc_intents, di, dt, dirpef = _process_sickness_case_event(
        event, ctx.evt_id, ctx.cp, ctx.payment_date, ctx.resolver, ctx.context
    )
    return EventEffect(
        items=list(sc_items),
        intents=list(sc_intents),
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
    )
