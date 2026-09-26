"""Handler for structured sick-leave episodes (SicknessCaseEvent)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

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
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    CompetencePeriod,
    PayItem,
    SicknessItem,
)
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.events import SicknessCaseEvent
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.domain.sickness import SicknessCase


def _case_components(
    case: SicknessCase, evt_id: str
) -> tuple[Decimal, tuple[tuple[str, Decimal, Decimal], ...]]:
    """Return the absence and the paid components of a sickness case.

    Returns:
        ``(absence, components)`` where each component is
        ``(item_id, amount, sick_days)``: the INPS indemnity, the employer
        integration and the carenza, in this order.
    """
    absence = money(case.gross_daily * case.working_days)
    inps_indemnity = money(
        case.gross_daily * case.inps_daily_rate * case.indemnifiable_days
    )
    top_up_factor = (
        case.integration_rate - case.inps_daily_rate
    ) * case.indemnifiable_days
    employer_integration = (
        money(case.gross_daily * top_up_factor) if top_up_factor > _ZERO else _ZERO
    )
    carenza = money(
        case.gross_daily * case.carenza_integration_rate * case.waiting_period_days
    )
    components = tuple(
        (
            component_id,
            amount,
            Decimal(case.indemnifiable_days)
            if "inps" in component_id or "intg" in component_id
            else Decimal(case.waiting_period_days),
        )
        for component_id, amount in (
            (f"{evt_id}_inps", inps_indemnity),
            (f"{evt_id}_intg", employer_integration),
            (f"{evt_id}_crnz", carenza),
        )
    )
    return absence, components


def _absence_posting(
    abs_id: str,
    absence: Decimal,
    working_days: int,
    cp: CompetencePeriod,
    payment_date: date,
    policy_id: str,
) -> tuple[PayItem, PostingIntent]:
    """Return the absence deduction of a sickness case and its intent.

    Returns:
        ``(item, intent)`` posting ``absence`` to ``EMPLOYEE_DEDUCTIONS``.
    """
    item = AbsenceDeduction(
        item_id=abs_id,
        competence_period=cp,
        payment_date=payment_date,
        quantity=Decimal(working_days),
        amount=absence,
        absence_days=Decimal(working_days),
    )
    intent = PostingIntent(
        entry_id=f"deduction_{abs_id}",
        source_item_id=abs_id,
        pay_item_kind="absence_deduction",
        account=AccountKind.EMPLOYEE_DEDUCTIONS,
        amount=absence,
        policy_decision_id=policy_id,
    )
    return item, intent


def _sickness_posting(
    component_id: str,
    amount: Decimal,
    sick_days: Decimal,
    cp: CompetencePeriod,
    payment_date: date,
    policy_id: str,
) -> tuple[PayItem, PostingIntent]:
    """Return one paid component of a sickness case and its intent.

    Returns:
        ``(item, intent)`` posting ``amount`` to ``CASH_EARNINGS``.
    """
    item = SicknessItem(
        item_id=component_id,
        competence_period=cp,
        payment_date=payment_date,
        quantity=Decimal(1),
        amount=amount,
        sick_days=sick_days,
    )
    intent = PostingIntent(
        entry_id=f"cash_{component_id}",
        source_item_id=component_id,
        pay_item_kind="sickness_item",
        account=AccountKind.CASH_EARNINGS,
        amount=amount,
        policy_decision_id=policy_id,
    )
    return item, intent


def _process_sickness_case_event(
    event: SicknessCaseEvent,
    evt_id: str,
    cp: CompetencePeriod,
    payment_date: date,
    resolver: PolicyResolver,
    context: PolicyContext,
) -> tuple[list[PayItem], list[PostingIntent], Decimal, Decimal, Decimal]:
    """Decompose a SicknessCaseEvent into absence + sickness integration components.

    Returns:
        ``(items, intents, delta_inps, delta_tfr, delta_irpef)`` where the deltas
        are the net contribution to the INPS/TFR/IRPEF bases for the period.
    """
    case = event.case
    resolution = _require_resolution(resolver, "sickness_item", context)
    treatment = _treatment_from_resolution(resolution)
    absence, components = _case_components(case, evt_id)

    item, intent = _absence_posting(
        f"{evt_id}_abs",
        absence,
        case.working_days,
        cp,
        payment_date,
        resolution.policy_id,
    )
    items: list[PayItem] = [item]
    intents: list[PostingIntent] = [intent]
    di_total = dt_total = dirpef_total = _ZERO
    di, dt, dirpef = _treatment_deltas(treatment, -absence)
    di_total += di
    dt_total += dt
    dirpef_total += dirpef

    for component_id, amount, sick_days in components:
        if amount <= _ZERO:
            continue
        item, intent = _sickness_posting(
            component_id, amount, sick_days, cp, payment_date, resolution.policy_id
        )
        items.append(item)
        intents.append(intent)
        di, dt, dirpef = _treatment_deltas(treatment, amount)
        di_total += di
        dt_total += dt
        dirpef_total += dirpef

    return items, intents, di_total, dt_total, dirpef_total


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
