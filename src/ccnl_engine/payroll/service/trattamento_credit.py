"""Trattamento integrativo of a run: its share, conguaglio and recovery.

The credit of Art. 1 D.L. 3/2020 (as updated by L. 207/2024) is paid run by
run on the projected income; an excess over the annual entitlement is
recovered as soon as a run finds it, in eight installments above 60 EUR
(art. 1 c. 3).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.obligations import (
    RECOVERY_RULES,
    TRATTAMENTO_RECOVERY,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.tax import TaxLineItem
from ccnl_engine.payroll.service import irpef as irpef_svc
from ccnl_engine.payroll.service import irpef_credits
from ccnl_engine.payroll.service.credit_decisions import credit_decision

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["resolve_trattamento"]

_ZERO = Decimal(0)
# D.L. 3/2020 art. 1 co. 3: recovery exceeding 60 EUR uses 8 equal installments.
_RECOVERY_INSTALLMENT_THRESHOLD = Decimal(60)
_RECOVERY_INSTALLMENTS = RECOVERY_RULES[TRATTAMENTO_RECOVERY].installments
_TRATTAMENTO_RULE = "dl3-2020-art1"


def _advance_plan(plan: RecoveryPlan) -> RecoveryPlan | None:
    """Return the plan advanced by one installment, or None when fully recovered.

    Returns:
        The advanced plan, or ``None`` if this was the last installment.
    """
    is_last = plan.installments_posted == plan.installments_total - 1
    return None if is_last else plan.advance()


def _new_recovery(recovery: Decimal) -> tuple[Decimal, RecoveryPlan | None]:
    """Open a fresh recovery: return (installment_amount, next_plan).

    Amounts <= 60 EUR are taken in full immediately (single period).
    Larger amounts are split into eight equal installments per
    D.L. 3/2020 art. 1 co. 3.

    Returns:
        ``(installment, next_plan)`` where ``next_plan`` is ``None`` when
        the recovery is settled in a single period.
    """
    if recovery <= _RECOVERY_INSTALLMENT_THRESHOLD:
        return money(recovery), None
    plan = RecoveryPlan.create(TRATTAMENTO_RECOVERY, recovery, _RECOVERY_INSTALLMENTS)
    return plan.next_installment, _advance_plan(plan)


def resolve_trattamento(
    taxable: Decimal,
    irpef_gross: Decimal,
    work_deduction: Decimal,
    rules: YearRules,
    opening_tratt_ytd: Decimal,
    remaining: int,
    existing_plan: RecoveryPlan | None = None,
    eligible_work_days: int = irpef_svc.DAYS_IN_YEAR,
) -> tuple[
    Decimal, TaxLineItem | None, RecoveryPlan | None, CalculationDecision | None
]:
    """Compute the per-period trattamento integrativo via conguaglio.

    When the worker owes back a credit (tratt_due < 0) the recovery is split
    into eight equal installments if the amount exceeds 60 EUR, or taken in
    one period otherwise (D.L. 3/2020 art. 1 co. 3).  Once a
    :class:`~ccnl_engine.payroll.domain.recovery_plan.RecoveryPlan` is in
    force (``existing_plan`` is not ``None``) the installment amount is frozen
    for all remaining periods and the last installment absorbs the rounding
    residual.

    Returns:
        ``(period_tratt, component, next_plan, decision)`` where:
        - ``period_tratt`` is the signed per-period amount (negative = recovery);
        - ``component`` is a :class:`TaxLineItem` for the audit trace when the
          annual entitlement is positive, or ``None`` otherwise;
        - ``next_plan`` is the updated :class:`RecoveryPlan` to carry into the
          next period's opening state, or ``None`` when no plan is active;
        - ``decision`` records the annual entitlement, why it is due or not,
          and the signed ``period_amount``; ``None`` when the credit is not
          in force for the year.
    """
    if rules.trattamento_integrativo is None:
        return _ZERO, None, None, None
    outcome = irpef_credits.trattamento_integrativo_outcome(
        taxable,
        irpef_gross,
        work_deduction,
        work_deduction,
        rules.trattamento_integrativo,
        eligible_work_days=eligible_work_days,
    )
    annual_tratt = outcome.amount
    if existing_plan is not None:
        period_tratt = -existing_plan.next_installment
        next_plan: RecoveryPlan | None = _advance_plan(existing_plan)
    else:
        tratt_due = annual_tratt - opening_tratt_ytd
        if tratt_due >= _ZERO:
            period_tratt = (
                money(tratt_due) if remaining == 1 else money(tratt_due / remaining)
            )
            next_plan = None
        else:
            installment, next_plan = _new_recovery(-tratt_due)
            period_tratt = -installment
    component = (
        TaxLineItem(
            name="trattamento_integrativo",
            amount=annual_tratt,
            rule_id=_TRATTAMENTO_RULE,
            fonte="Art. 1 D.L. 3/2020 (L. 207/2024)",
        )
        if annual_tratt > _ZERO
        else None
    )
    decision = credit_decision(
        "trattamento_integrativo",
        _TRATTAMENTO_RULE,
        rules,
        outcome,
        {
            "taxable_income": taxable,
            "irpef_gross": irpef_gross,
            "work_deduction": work_deduction,
            "eligible_work_days": str(eligible_work_days),
            "recovery_in_progress": str(existing_plan is not None).lower(),
            "period_amount": period_tratt,
        },
    )
    return period_tratt, component, next_plan, decision
