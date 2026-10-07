"""Trattamento integrativo of a run: its share, conguaglio and recovery.

The credit of Art. 1 D.L. 3/2020 (as updated by L. 207/2024) is paid run by
run on the projected income; an excess over the annual entitlement is
recovered as soon as a run finds it, in eight installments above 60 EUR
(art. 1 c. 3).  On the last run of the employment the excess, or the
residual of a running recovery, is recovered in full (AdE circ. 29/E/2020
par. 6: "in un'unica soluzione, indipendentemente dall'importo, in mancanza
di ulteriori retribuzioni sulle quali operare il recupero in maniera
dilazionata").
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.obligations import (
    RECOVERY_RULES,
    TRATTAMENTO_RECOVERY,
)
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun, RecoveryPlan
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.tax import TaxLineItem
from ccnl_engine.payroll.service import irpef_credits
from ccnl_engine.payroll.service.credit_decisions import credit_decision
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR

if TYPE_CHECKING:
    from ccnl_engine.payroll.service.irpef_net import NetIrpef
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["resolve_trattamento"]

_ZERO = Decimal(0)
# D.L. 3/2020 art. 1 co. 3: recovery exceeding 60 EUR uses 8 equal installments.
_RECOVERY_INSTALLMENT_THRESHOLD = Decimal(60)
_RECOVERY_INSTALLMENTS = RECOVERY_RULES[TRATTAMENTO_RECOVERY].installments
_TRATTAMENTO_RULE = "dl3-2020-art1"


_RECOVERY_CAPABILITY = f"{TRATTAMENTO_RECOVERY}_recovery"


@dataclass(frozen=True)
class _Period:
    """Signed amount of the run, the plan after it and why it recovers.

    ``reason`` is ``None`` when the run pays rather than recovers.
    """

    amount: Decimal
    plan: RecoveryPlan | None = None
    reason: str | None = None


def _new_recovery(recovery: Decimal, run: InstallmentRun) -> _Period:
    """Open a fresh recovery of ``recovery``.

    Amounts <= 60 EUR, and any amount on the final run of the employment,
    are taken in full on the run.  Larger amounts are split into eight
    equal installments per D.L. 3/2020 art. 1 co. 3.

    Returns:
        The negative amount of the run and the plan still running, if any.
    """
    if recovery <= _RECOVERY_INSTALLMENT_THRESHOLD:
        return _Period(-money(recovery), reason="overpayment_recovered")
    if run.final:
        return _Period(-money(recovery), reason="overpayment_recovered_at_termination")
    plan = RecoveryPlan.create(TRATTAMENTO_RECOVERY, recovery, _RECOVERY_INSTALLMENTS)
    posted = plan.post(run)
    return _Period(-posted.amount, posted.remaining, "overpayment_recovery_opened")


def _period_amount(
    annual_tratt: Decimal,
    opening_tratt_ytd: Decimal,
    remaining: int,
    existing_plan: RecoveryPlan | None,
    run: InstallmentRun,
) -> _Period:
    """Return the signed amount of the run and the plan to carry forward.

    A plan in force takes its next installment, or its residual on the
    final run.  Otherwise the balance still due is spread over the
    remaining slots, or an excess already paid opens a recovery.

    Returns:
        The amount, negative for a recovery, with the plan and reason.
    """
    if existing_plan is not None:
        posted = existing_plan.post(run)
        return _Period(-posted.amount, posted.remaining, posted.reason)
    tratt_due = annual_tratt - opening_tratt_ytd
    if tratt_due >= _ZERO:
        period = money(tratt_due) if remaining == 1 else money(tratt_due / remaining)
        return _Period(period)
    return _new_recovery(-tratt_due, run)


def _recovery_decision(
    period: _Period, rules: YearRules, opening_tratt_ytd: Decimal
) -> tuple[CalculationDecision, ...]:
    """Return the decision recording a recovery of the run, if any.

    Returns:
        One final decision, capability ``trattamento_integrativo_recovery``,
        whose amount is the (negative) amount recovered; empty when the run
        recovers nothing.
    """
    if period.reason is None:
        return ()
    return (
        CalculationDecision(
            capability=_RECOVERY_CAPABILITY,
            status=CalculationStatus.FINAL,
            reason_code=period.reason,
            rule=RECOVERY_RULES[TRATTAMENTO_RECOVERY].rule,
            rule_version=(
                str(rules.year) if rules.ruleset is None else rules.ruleset.version
            ),
            inputs={
                "net_paid_before": opening_tratt_ytd,
                "residual_after": (
                    _ZERO if period.plan is None else period.plan.residual
                ),
            },
            amount=period.amount,
        ),
    )


def resolve_trattamento(
    taxable: Decimal,
    annual: NetIrpef,
    rules: YearRules,
    opening_tratt_ytd: Decimal,
    remaining: int,
    existing_plan: RecoveryPlan | None = None,
    eligible_work_days: int = DAYS_IN_YEAR,
    *,
    run: InstallmentRun,
) -> tuple[
    Decimal, TaxLineItem | None, RecoveryPlan | None, tuple[CalculationDecision, ...]
]:
    """Compute the per-period trattamento integrativo via conguaglio.

    An excess (tratt_due < 0) is recovered in eight equal installments
    above 60 EUR, in one period otherwise (D.L. 3/2020 art. 1 co. 3); a
    plan in force (``existing_plan``) keeps its installment amount.  On the
    final run of the employment (``run.final``) the excess or the residual
    is recovered in full.

    Above 15,000 EUR the gross tax of ``annual`` is compared with the sum of
    its art. 12 and art. 13 c. 1 TUIR deductions (D.L. 3/2020 art. 1 c. 1,
    second period); the ulteriore detrazione of L. 207/2024 art. 1 c. 6 is
    not in that list.  The art. 15 TUIR items of the same period (loans up
    to 2021, instalments of expenses up to 2021) are not known to the
    payroll and are left to the worker's tax return: the credit of the run
    can only be lower than the one of the return, never higher.

    Returns:
        ``(period_tratt, component, next_plan, decisions)`` where:
        - ``period_tratt`` is the signed per-period amount (negative = recovery);
        - ``component`` is a :class:`TaxLineItem` for the audit trace when the
          annual entitlement is positive, or ``None`` otherwise;
        - ``next_plan`` is the updated :class:`RecoveryPlan` to carry into the
          next period's opening state, or ``None`` when no plan is active;
        - ``decisions`` records the annual entitlement, why it is due or
          not, and the signed ``period_amount``, then the recovery of the
          run, if any; empty when the credit is not in force for the year.
    """
    if rules.trattamento_integrativo is None:
        return _ZERO, None, None, ()
    relevant_deductions = annual.work_deduction + annual.family_deductions
    outcome = irpef_credits.trattamento_integrativo_outcome(
        taxable,
        annual.gross,
        annual.work_deduction,
        relevant_deductions,
        rules.trattamento_integrativo,
        eligible_work_days=eligible_work_days,
    )
    annual_tratt = outcome.amount
    period = _period_amount(
        annual_tratt, opening_tratt_ytd, remaining, existing_plan, run
    )
    period_tratt = period.amount
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
            "irpef_gross": annual.gross,
            "work_deduction": annual.work_deduction,
            "family_deductions": annual.family_deductions,
            "relevant_deductions": relevant_deductions,
            "eligible_work_days": str(eligible_work_days),
            "recovery_in_progress": str(existing_plan is not None).lower(),
            "period_amount": period_tratt,
        },
    )
    recovery = _recovery_decision(period, rules, opening_tratt_ytd)
    return period_tratt, component, period.plan, (decision, *recovery)
