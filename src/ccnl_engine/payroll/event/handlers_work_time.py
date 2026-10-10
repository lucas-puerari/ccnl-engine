"""Handlers for standard work-time and bonus events."""

from __future__ import annotations

from ccnl_engine.payroll.amount.models_treatment import EventTreatment
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationIssue,
)
from ccnl_engine.payroll.event.facade import (
    AbsenceEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
)
from ccnl_engine.payroll.event.handlers_context import (
    EventEffect,
    _EventHandlerCtx,
    _treatment_deltas,
)
from ccnl_engine.payroll.event.handlers_preferential_regime import (
    apply_preferential_regime,
)
from ccnl_engine.payroll.event.handlers_standard import (
    _make_standard_event_intent,
    _standard_event_gross,
    _standard_event_item,
)
from ccnl_engine.payroll.event.policies_overtime_rate import (
    band_decision,
    overtime_issues,
    resolve_overtime_rate,
)
from ccnl_engine.payroll.ledger.models import PostingIntent
from ccnl_engine.payroll.period.services_shared import (
    _ZERO,
    _require_resolution,
    _treatment_from_resolution,
)


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


def _premium(event: object) -> bool:
    """Return whether the event is a premium withheld apart from the period.

    Art. 23 c. 2 lett. b) DPR 600/1973 withholds on the "compensi della
    stessa natura" of the mensilità aggiuntive, among which AdE circ.
    15/E/2007 par. 2.4 lists "le gratifiche annuali di bilancio, i cosiddetti
    premi trimestrali, semestrali e annuali".  A bonus or a productivity
    bonus is one; a contract renewal increment is pay of the period.

    Returns:
        ``True`` for a :class:`BonusEvent` that is not a contract renewal.
    """
    return isinstance(event, BonusEvent) and event.kind != "contract_renewal"


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

    An overtime event is paid with its multiplier or, without one, with the
    CCNL band of its kind (see
    :mod:`~ccnl_engine.payroll.event.policies_overtime_rate`).

    Returns:
        Handler result with pay item, ledger entry, and INPS/TFR/IRPEF deltas.
    """
    decisions: list[CalculationDecision] = []
    issues: list[CalculationIssue] = []
    if isinstance(event, OvertimeEvent):
        rate = resolve_overtime_rate(event, ctx.overtime_bands)
        event = rate.paid(event)
        issues.extend(overtime_issues(event, rate))
        decision = band_decision(
            event, rate, ctx.overtime_bands, _standard_event_gross(event)
        )
        decisions.extend(() if decision is None else (decision,))
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
        separate_irpef_delta=dirpef if _premium(event) else _ZERO,
        substitute_delta=substitute_delta,
        regime_cap_used=cap_used,
        decisions=decisions,
        issues=issues,
    )
