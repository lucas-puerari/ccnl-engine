"""Payslip lines and decisions of the IRPEF deferred on written request.

See :mod:`~ccnl_engine.payroll.withholding.services_deferral`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.facade import EmployeeWithholdingItem
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.ledger.models_remittance import POST_CONGUAGLIO_WITHHOLDING
from ccnl_engine.payroll.period.services_shared import (
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.withholding.inputs_shortfall_deferral import (
    DEFERRAL_MONTHLY_RATE,
)
from ccnl_engine.payroll.withholding.rules_law import (
    WithholdingTopic,
    withholding_rule,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.amount.facade import PayItem
    from ccnl_engine.payroll.ledger.models import LedgerEntry
    from ccnl_engine.payroll.period.services_run_context import RunContext
    from ccnl_engine.payroll.withholding.inputs_shortfall_deferral import (
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
_ZERO = Decimal(0)


def deferral_decision(
    ctx: RunContext,
    reason: str,
    amount: Decimal,
    inputs: dict[str, Decimal | str],
    status: CalculationStatus = CalculationStatus.FINAL,
) -> CalculationDecision:
    """Build the decision of one step of the deferred IRPEF.

    Returns:
        The decision with the conguaglio rule of the contract year.
    """
    rules = ctx.contract.year_rules
    law = withholding_rule(WithholdingTopic.CONGUAGLIO, rules.year)
    return CalculationDecision(
        capability=CAPABILITY,
        status=status,
        reason_code=reason,
        rule=law.rule,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs=inputs,
        source=law.source,
        amount=amount,
    )


def deferred_lines(
    ctx: RunContext, deferred: DeferredShortfall, posted: DeferredInstallment
) -> tuple[list[PayItem], list[LedgerEntry]]:
    """Build the withholding lines of one deferred installment.

    Returns:
        The pay items and ledger entries of the principal and the interest.
    """
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
    """Report deferred IRPEF still unrecovered when the window closes.

    Returns:
        The provisional decision and the issue that tells the worker to pay.
    """
    decision = deferral_decision(
        ctx,
        "deferred_shortfall_unrecovered",
        deferred.irpef,
        {"origin_tax_year": str(deferred.tax_year)},
        CalculationStatus.PROVISIONAL,
    )
    law = withholding_rule(WithholdingTopic.CONGUAGLIO, ctx.contract.year_rules.year)
    issue = CalculationIssue(
        code="deferred_shortfall_unrecovered",
        message=(
            f"shortfall_deferral: {deferred.irpef} IRPEF of the conguaglio "
            f"{deferred.tax_year} deferred on written request was not withheld "
            f"by the end of {deferred.withheld_in} or of the employment; "
            f"{law.citation} requires the amount to be communicated to "
            "the worker, who pays it by 15 January of the next year"
        ),
        status=CalculationStatus.PROVISIONAL,
    )
    return decision, issue


def withheld_decision(
    ctx: RunContext, deferred: DeferredShortfall, posted: DeferredInstallment
) -> CalculationDecision:
    """Build the decision of a deferred installment withheld in the run.

    Returns:
        The final decision with principal, interest and monthly rate.
    """
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
