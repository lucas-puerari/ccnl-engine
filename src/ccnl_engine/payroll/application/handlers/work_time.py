"""Handlers for standard work-time and bonus events."""

from __future__ import annotations

from ccnl_engine.payroll.application._period_utils import (
    _ZERO,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
    _treatment_deltas,
)
from ccnl_engine.payroll.application.handlers._preferential_regime import (
    apply_preferential_regime,
)
from ccnl_engine.payroll.application.handlers._standard_event import (
    _make_standard_event_intent,
    _standard_event_gross,
    _standard_event_item,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
)
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
)
from ccnl_engine.payroll.domain.ledger import PostingIntent
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
    prior_income = ctx.worker_facts.prior_income
    if prior_income is None:
        return True
    return prior_income > ctx.pdr_income_ceiling


def _handle_standard(
    event: OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | ShiftWorkEvent
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
    decisions: list[CalculationDecision] = []
    issues: list[CalculationIssue] = []

    cap_used = _ZERO
    regime = apply_preferential_regime(
        event, kind, treatment.substitute, ctx, gross, resolution.policy_id
    )
    if regime is not None:
        intents.extend(regime.intents)
        dirpef = regime.ordinary_amount
        cap_used = regime.cap_used
        decisions.append(regime.decision)
        if regime.issue is not None:
            issues.append(regime.issue)
    elif treatment.substitute:
        substitute_delta = gross

    return EventEffect(
        items=[item],
        intents=intents,
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
        substitute_delta=substitute_delta,
        regime_cap_used=cap_used,
        decisions=decisions,
        issues=issues,
    )
