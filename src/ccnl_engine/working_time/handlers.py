"""Handlers for standard work-time and bonus events."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
)
from ccnl_engine.event.facade import (
    AbsenceEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
)
from ccnl_engine.event.handlers import (
    EventEffect,
    _EventHandlerCtx,
    _treatment_deltas,
)
from ccnl_engine.event.standard.handlers import (
    _make_standard_event_intent,
    _standard_event_gross,
    _standard_event_item,
)
from ccnl_engine.ledger.models import PostingIntent
from ccnl_engine.pay_item.services import (
    _ZERO,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.pay_item.treatment.models import EventTreatment
from ccnl_engine.regime.handlers import (
    apply_preferential_regime,
)
from ccnl_engine.working_time.services import resolve_work_event
from ccnl_engine.working_time.tourism.services import special_supplement_lines


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
    # Turning an "and" of the guard into "or" also sends a contract renewal
    # through the PdR ceiling; its own regime, with a lower ceiling (33,000
    # EUR in 2026) and the same fail-closed rule, already taxes it as
    # ordinary income there: those two mutants are equivalent.
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


def _hours_apart(
    event: object, apart: Decimal, ctx: _EventHandlerCtx, treatment: EventTreatment
) -> EventEffect:
    """Return the pay of the hours a supplement band is due on top of.

    The hours themselves (worked on a public holiday, or paid apart by the
    CCNL) are pay of the period at ordinary tax: the work-time regime
    covers only the supplement.

    Returns:
        Nothing without such hours; the item, posting and base deltas of
        the hours, of the event's kind.
    """
    if not apart or not isinstance(
        event, (HolidayWorkEvent, NightShiftEvent, ShiftWorkEvent)
    ):
        return EventEffect()
    paid = replace(event, supplement_amount=apart)
    evt_id = f"{ctx.evt_id}_hours"
    item, kind = _standard_event_item(paid, apart, evt_id, ctx.cp, ctx.payment_date)
    resolution = _require_resolution(ctx.resolver, kind, ctx.context)
    di, dt, dirpef = _treatment_deltas(treatment, apart)
    return EventEffect(
        items=[item],
        intents=[_make_standard_event_intent(paid, apart, evt_id, kind, resolution)],
        inps_delta=di,
        tfr_delta=dt,
        irpef_delta=dirpef,
    )


def _premium(event: object) -> bool:
    """Return whether the event is a premium withheld apart from the period.

    Art. 23 c. 2 lett. b) DPR 600/1973 withholds on the "compensi della
    stessa natura" of the mensilità aggiuntive, among which AdE circ.
    15/E/2007 par. 2.4 lists "le gratifiche annuali di bilancio, i cosiddetti
    premi trimestrali, semestrali e annuali".  A bonus or a productivity
    bonus is one; a contract renewal increment and a sales commission are
    pay of the period.

    Returns:
        ``True`` for a :class:`BonusEvent` that is not a contract renewal.
    """
    return isinstance(event, BonusEvent) and event.kind not in {
        "contract_renewal",
        "commission",
    }


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

    A work-time event is paid with the caller's values or, without them,
    with those the CCNL sets (see :mod:`~ccnl_engine.working_time.services`).

    Returns:
        Handler result with pay item, ledger entry, and INPS/TFR/IRPEF deltas.
    """
    decisions: list[CalculationDecision] = []
    issues: list[CalculationIssue] = []
    limitations: tuple[str, ...] = ()
    apart = _ZERO
    if not isinstance(event, (SickLeaveEvent, BonusEvent)):
        resolved = resolve_work_event(event, ctx.overtime_bands, ctx.hourly)
        event = resolved.event
        decisions.extend(resolved.decisions)
        issues.extend(resolved.issues)
        limitations = resolved.limitations
        apart = resolved.apart
    gross = _standard_event_gross(event)
    item, kind = _standard_event_item(
        event, gross, ctx.evt_id, ctx.cp, ctx.payment_date
    )
    resolution = _require_resolution(ctx.resolver, kind, ctx.context)
    treatment = _treatment_from_resolution(resolution)
    if _pdr_ceiling_exceeded(event, treatment, ctx):
        # Only the tax changes: the INPS and TFR bases of the bonus stay.
        # ``substitute=None`` would be as falsy as False: not generated.
        treatment = replace(
            treatment, irpef=True, substitute=False
        )  # pragma: no mutate
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
    special = special_supplement_lines(event, gross, decisions, ctx)
    decisions.extend(special.decisions)
    issues.extend(special.issues)
    hours = _hours_apart(event, apart, ctx, treatment)

    return EventEffect(
        items=[item, *special.items, *hours.items],
        intents=[*intents, *special.intents, *hours.intents],
        inps_delta=di + hours.inps_delta,
        tfr_delta=dt + hours.tfr_delta,
        irpef_delta=dirpef + hours.irpef_delta,
        separate_irpef_delta=dirpef if _premium(event) else _ZERO,
        substitute_delta=substitute_delta,
        regime_cap_used=cap_used,
        decisions=decisions,
        issues=issues,
        limitations=limitations,
    )
