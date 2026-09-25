"""Handler for contract-renewal arrears (tassazione separata)."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.events import ArrearsEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import ContractRenewalArrears
from ccnl_engine.payroll.service.rounding import money


def _handle_arrears(event: ArrearsEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle contract-renewal arrears (tassazione separata).

    Returns:
        Handler result with arrears item posted to CASH_EARNINGS and SEPARATE_TAX.
    """
    gross = event.amount
    sep_tax = money(gross * event.separate_tax_rate)
    arrears_resolution = _require_resolution(
        ctx.resolver, "contract_renewal_arrears", ctx.context
    )
    item = ContractRenewalArrears(
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
                entry_id=f"cash_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="contract_renewal_arrears",
                account=AccountKind.CASH_EARNINGS,
                amount=gross,
                policy_decision_id=arrears_resolution.policy_id,
            ),
            PostingIntent(
                entry_id=f"sep_tax_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="contract_renewal_arrears",
                account=AccountKind.SEPARATE_TAX,
                amount=sep_tax,
                policy_decision_id=arrears_resolution.policy_id,
            ),
        ],
        inps_delta=gross,
    )
