"""Handlers for standard work-time and bonus events."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application._event_items import (
    _make_standard_event_intent,
    _standard_event_gross,
    _standard_event_item,
    _treatment_deltas,
)
from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
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
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.treatment import EventTreatment
from ccnl_engine.payroll.service.rounding import money


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


def _rinnovo_tax(
    event: object, treatment: EventTreatment, ctx: _EventHandlerCtx, gross: Decimal
) -> Decimal | None:
    """Return the 5% substitute tax for a contract_renewal BonusEvent, or None.

    Returns:
        Tax amount, or ``None`` when not a contract_renewal or rate is not set.
    """
    if not (
        isinstance(event, BonusEvent)
        and event.kind == "contract_renewal"
        and treatment.substitute
        and ctx.rinnovo_flat_rate is not None
    ):
        return None
    return money(gross * ctx.rinnovo_flat_rate)


def _notte_turno_tax(
    event: object, ctx: _EventHandlerCtx, gross: Decimal
) -> Decimal | None:
    """Return the 15% substitute tax for an eligible NightShiftEvent, or None.

    Fail-closed: ``None`` prior_income → ordinary IRPEF (not substitute rate).

    Returns:
        Tax amount, or ``None`` when not eligible or rate is not configured.
    """
    if not (
        isinstance(event, NightShiftEvent)
        and event.prior_income is not None
        and ctx.notte_flat_rate is not None
        and ctx.notte_income_ceiling is not None
    ):
        return None
    if event.prior_income > ctx.notte_income_ceiling:
        return None
    return money(gross * ctx.notte_flat_rate)


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
    intents: list[PostingIntent] = [
        _make_standard_event_intent(event, gross, ctx.evt_id, kind, resolution)
    ]
    substitute_delta = _ZERO

    rinnovo = _rinnovo_tax(event, treatment, ctx, gross)
    if rinnovo is not None:
        intents.append(
            PostingIntent(
                entry_id=f"rinnovo_tax_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind=kind,
                account=AccountKind.SUBSTITUTE_TAX,
                amount=rinnovo,
                policy_decision_id=resolution.policy_id,
            )
        )
        dirpef = _ZERO
    elif treatment.substitute:
        substitute_delta = gross

    notte = _notte_turno_tax(event, ctx, gross)
    if notte is not None:
        intents.append(
            PostingIntent(
                entry_id=f"notte_tax_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind=kind,
                account=AccountKind.SUBSTITUTE_TAX,
                amount=notte,
                policy_decision_id=resolution.policy_id,
            )
        )
        dirpef = _ZERO

    return EventEffect(
        items=[item],
        intents=intents,
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
        substitute_delta=substitute_delta,
    )
