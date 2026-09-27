"""Payslip lines and decisions of the IRPEF deferred on written request.

See :mod:`~ccnl_engine.payroll.application.withholding._deferral`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import EmployeeWithholdingItem
from ccnl_engine.payroll.domain.remittance import POST_CONGUAGLIO_WITHHOLDING
from ccnl_engine.payroll.domain.shortfall_deferral import DEFERRAL_MONTHLY_RATE

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.shortfall_deferral import (
        DeferredInstallment,
        DeferredShortfall,
    )

__all__ = [
    "CAPABILITY",
    "deferral_decision",
    "deferred_lines",
    "unrecovered_deferral",
    "withheld_decision",
]

CAPABILITY = "shortfall_deferral"
_WITHHOLDING = "employee_withholding_item"
_RULE = "dpr600-1973-art23-c3"
_ZERO = Decimal(0)


def deferral_decision(
    ctx: RunContext,
    reason: str,
    amount: Decimal,
    inputs: dict[str, Decimal | str],
    status: CalculationStatus = CalculationStatus.FINAL,
) -> CalculationDecision:
    rules = ctx.contract.year_rules
    return CalculationDecision(
        capability=CAPABILITY,
        status=status,
        reason_code=reason,
        rule=_RULE,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs=inputs,
        amount=amount,
    )


def deferred_lines(
    ctx: RunContext, deferred: DeferredShortfall, posted: DeferredInstallment
) -> tuple[list[PayItem], list[LedgerEntry]]:
    policy_id = _require_resolution(
        ctx.resolver, _WITHHOLDING, ctx.policy_context
    ).policy_id
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []
    payment_date = ctx.request.payment_date
    stem = f"deferred_irpef_{deferred.tax_year}"
    for item_id, amount in (
        (f"{stem}_{ctx.run_id}", posted.principal),
        (f"{stem}_interest_{ctx.run_id}", posted.interest),
    ):
        if amount == _ZERO:
            continue
        items.append(
            EmployeeWithholdingItem(
                item_id=item_id,
                competence_period=ctx.cp,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=amount,
            )
        )
        entries.append(
            _make_entry(
                item_id,
                item_id,
                _WITHHOLDING,
                ctx.cp,
                payment_date,
                AccountKind.ORDINARY_TAX,
                amount,
                policy_id=policy_id,
                remittance_code=POST_CONGUAGLIO_WITHHOLDING,
            )
        )
    return items, entries


def unrecovered_deferral(
    ctx: RunContext, deferred: DeferredShortfall
) -> tuple[CalculationDecision, CalculationIssue]:
    decision = deferral_decision(
        ctx,
        "deferred_shortfall_unrecovered",
        deferred.irpef,
        {"origin_tax_year": str(deferred.tax_year)},
        CalculationStatus.PROVISIONAL,
    )
    issue = CalculationIssue(
        code="deferred_shortfall_unrecovered",
        message=(
            f"shortfall_deferral: {deferred.irpef} IRPEF of the conguaglio "
            f"{deferred.tax_year} deferred on written request was not withheld "
            f"by the end of {deferred.withheld_in} or of the employment; art. "
            "23 c. 3 DPR 600/1973 requires the amount to be communicated to "
            "the worker, who pays it by 15 January of the next year"
        ),
        status=CalculationStatus.PROVISIONAL,
    )
    return decision, issue


def withheld_decision(
    ctx: RunContext, deferred: DeferredShortfall, posted: DeferredInstallment
) -> CalculationDecision:
    return deferral_decision(
        ctx,
        "deferred_shortfall_withheld",
        posted.total,
        {
            "origin_tax_year": str(deferred.tax_year),
            "residual_before": deferred.irpef,
            "principal": posted.principal,
            "interest": posted.interest,
            "months": Decimal(posted.months),
            "monthly_rate": DEFERRAL_MONTHLY_RATE,
        },
    )
