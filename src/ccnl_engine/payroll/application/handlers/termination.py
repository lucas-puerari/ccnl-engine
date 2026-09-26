"""Handlers for bilateral fund contributions and TFR settlement at cessazione."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.events import BilateralFundEvent, TerminationTFREvent
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import (
    EmployeeWithholdingItem,
    EmployerContributionItem,
    TfrSettlementItem,
)
from ccnl_engine.payroll.domain.rounding import money


def _handle_bilateral_fund(
    event: BilateralFundEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle bilateral or health fund contribution events.

    Returns:
        Handler result with employee and employer items posted to
        BILATERAL_FUND_EMPLOYEE and BILATERAL_FUND_EMPLOYER accounts.
    """
    emp_id = f"{ctx.evt_id}_emp"
    er_id = f"{ctx.evt_id}_er"
    emp_resolution = _require_resolution(
        ctx.resolver, "employee_withholding_item", ctx.context
    )
    er_resolution = _require_resolution(
        ctx.resolver, "employer_contribution_item", ctx.context
    )
    emp_item = EmployeeWithholdingItem(
        item_id=emp_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=event.employee_amount,
    )
    er_item = EmployerContributionItem(
        item_id=er_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=event.employer_amount,
    )
    return EventEffect(
        items=[emp_item, er_item],
        intents=[
            PostingIntent(
                entry_id=f"bilat_emp_{ctx.evt_id}",
                source_item_id=emp_id,
                pay_item_kind="employee_withholding_item",
                account=AccountKind.BILATERAL_FUND_EMPLOYEE,
                amount=event.employee_amount,
                policy_decision_id=emp_resolution.policy_id,
            ),
            PostingIntent(
                entry_id=f"bilat_er_{ctx.evt_id}",
                source_item_id=er_id,
                pay_item_kind="employer_contribution_item",
                account=AccountKind.BILATERAL_FUND_EMPLOYER,
                amount=event.employer_amount,
                policy_decision_id=er_resolution.policy_id,
            ),
        ],
    )


def _handle_termination_tfr(
    event: TerminationTFREvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle TFR settlement at cessazione.

    Returns:
        Handler result with TFR item posted to TFR_SETTLEMENT and SEPARATE_TAX.
    """
    gross = event.amount
    sep_tax = money(gross * event.separate_tax_rate)
    tfr_settle_resolution = _require_resolution(
        ctx.resolver, "tfr_settlement_item", ctx.context
    )
    item = TfrSettlementItem(
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
                entry_id=f"tfr_settle_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="tfr_settlement_item",
                account=AccountKind.TFR_SETTLEMENT,
                amount=gross,
                policy_decision_id=tfr_settle_resolution.policy_id,
            ),
            PostingIntent(
                entry_id=f"sep_tax_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="tfr_settlement_item",
                account=AccountKind.SEPARATE_TAX,
                amount=sep_tax,
                policy_decision_id=tfr_settle_resolution.policy_id,
            ),
        ],
    )
