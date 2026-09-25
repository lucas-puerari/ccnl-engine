"""Handlers for welfare and fringe benefit events."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application._event_items import _fringe_bases
from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.events import FringeEvent, WelfareEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import FringeBenefitItem, WelfareItem


def _handle_welfare(event: WelfareEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle welfare benefit events.

    Returns:
        Handler result with WelfareItem posted to NON_CASH_BENEFITS.
    """
    gross = event.amount
    welfare_resolution = _require_resolution(ctx.resolver, "welfare_item", ctx.context)
    item = WelfareItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        intents=[
            PostingIntent(
                entry_id=f"ncb_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="welfare_item",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=gross,
                policy_decision_id=welfare_resolution.policy_id,
            )
        ],
    )


def _handle_fringe(event: FringeEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle fringe benefit events (with running accumulator update).

    Returns:
        Handler result with fringe item, ledger entry, contribution-base deltas,
        and updated ``new_cumulative_fringe`` / ``new_cumulative_taxed`` values.
    """
    gross = event.amount
    fringe_inps, fringe_irpef, new_cumulative_fringe = _fringe_bases(
        gross, ctx.cumulative_fringe, ctx.fringe_threshold, ctx.cumulative_taxed
    )
    new_cumulative_taxed = ctx.cumulative_taxed + fringe_inps
    fringe_resolution = _require_resolution(
        ctx.resolver, "fringe_benefit_item", ctx.context
    )
    item = FringeBenefitItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        intents=[
            PostingIntent(
                entry_id=f"ncb_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="fringe_benefit_item",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=gross,
                policy_decision_id=fringe_resolution.policy_id,
            )
        ],
        inps_delta=fringe_inps,
        irpef_delta=fringe_irpef,
        fringe_value=gross,
        fringe_inps=fringe_inps,
        fringe_irpef=fringe_irpef,
        new_cumulative_fringe=new_cumulative_fringe,
        new_cumulative_taxed=new_cumulative_taxed,
    )
