"""Handlers for standard work-time and bonus events."""

from __future__ import annotations

from ccnl_engine.payroll.application._event_items import (
    _make_standard_event_intent,
    _standard_event_gross,
    _standard_event_item,
    _treatment_deltas,
)
from ccnl_engine.payroll.application._period_utils import (
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
)
from ccnl_engine.payroll.domain.treatment import EventTreatment


def _pdr_ceiling_exceeded(
    event: object, treatment: EventTreatment, ctx: _EventHandlerCtx
) -> bool:
    """Return True when a productivity_bonus is ineligible for the PdR substitute rate.

    Fail-closed: unknown prior income (``None``) is treated as exceeding the
    ceiling, so the conservative treatment (ordinary IRPEF) is applied.

    Returns:
        ``True`` when the event is ineligible — either because prior income is
        unknown or because it exceeds ``ctx.pdr_income_ceiling``.
    """
    if not (
        isinstance(event, BonusEvent)
        and event.kind == "productivity_bonus"
        and treatment.substitute
        and ctx.pdr_income_ceiling is not None
    ):
        return False
    # Fail-closed: None means income status unknown → treat as ineligible.
    if event.prior_income is None:
        return True
    return event.prior_income > ctx.pdr_income_ceiling


def _handle_standard(
    event: OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | BonusEvent,
    ctx: _EventHandlerCtx,
) -> EventEffect:
    """Handle standard work-time and bonus events.

    Returns:
        Handler result with pay item, ledger entry, and INPS/TFR/IRPEF deltas.
    """
    gross = _standard_event_gross(event)
    item, kind = _standard_event_item(
        event, gross, ctx.evt_id, ctx.cp, ctx.payment_date
    )
    resolution = _require_resolution(ctx.resolver, kind, ctx.context)
    treatment = _treatment_from_resolution(resolution)
    if _pdr_ceiling_exceeded(event, treatment, ctx):
        treatment = EventTreatment(
            inps=treatment.inps, tfr=treatment.tfr, irpef=True, substitute=False
        )
    di, dt, dirpef = _treatment_deltas(treatment, gross)
    result = EventEffect(
        items=[item],
        intents=[
            _make_standard_event_intent(event, gross, ctx.evt_id, kind, resolution)
        ],
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
    )
    if treatment.substitute:
        result.substitute_delta = gross
    return result
