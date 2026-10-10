"""Account transition of the somma esente: what a run pays or recovers.

Before the conguaglio a run pays the percentage applied to the income it
pays (AdE circ. 4/E/2025 par. 1.2), capped at what is still due, and never
recovers.  At the conguaglio the balance
between the annual due and the net paid is settled: an amount not due is
recovered in full up to 60 EUR and otherwise in ten equal installments
(L. 207/2024 art. 1 c. 7), in full on the last run of the employment (AdE
circ. 4/E/2025 par. 1.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.state.models_obligation import (
    RECOVERY_RULES,
    SOMMA_ESENTE_RECOVERY,
)
from ccnl_engine.payroll.withholding.models_recovery_plan import (
    InstallmentRun,
    RecoveryPlan,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.state.models_credit_account import SommaEsenteAccount
    from ccnl_engine.payroll.withholding.models_schedule import WithholdingPosition

__all__ = ["Settlement", "settle"]

_ZERO = Decimal(0)
#: L. 207/2024 art. 1 c. 7: up to 60 EUR the excess is recovered in full.
_SINGLE_RECOVERY_LIMIT = Decimal(60)


@dataclass(frozen=True)
class Settlement:
    """Amount of a run, its reason and the recovery still running after it."""

    amount: Decimal
    reason: str
    plan: RecoveryPlan | None = None


def _installment(
    plan: RecoveryPlan, run: InstallmentRun, reason: str | None = None
) -> Settlement:
    """Post what ``run`` recovers of ``plan``.

    Returns:
        The negative amount recovered and the plan still running after it;
        ``reason``, when given, replaces the reason of the installment.
    """
    posted = plan.post(run)
    return Settlement(
        amount=-posted.amount,
        reason=reason or posted.reason,
        plan=posted.remaining,
    )


def _recover(excess: Decimal, run: InstallmentRun) -> Settlement:
    """Recover an ``excess`` found at the conguaglio (L. 207/2024 art. 1 c. 7).

    Returns:
        The full excess up to 60 EUR or on the final run of the employment,
        otherwise the first of ten equal installments with the plan of the
        others.
    """
    if excess <= _SINGLE_RECOVERY_LIMIT:
        return Settlement(amount=-excess, reason="overpayment_recovered")
    if run.final:
        return Settlement(amount=-excess, reason="overpayment_recovered_at_termination")
    plan = RecoveryPlan.create(
        SOMMA_ESENTE_RECOVERY,
        excess,
        RECOVERY_RULES[SOMMA_ESENTE_RECOVERY].installments,
    )
    return _installment(plan, run, "overpayment_recovery_opened")


def settle(
    annual: Decimal,
    period: Decimal,
    withholding: WithholdingPosition,
    account: SommaEsenteAccount,
    plan: RecoveryPlan | None,
    run: InstallmentRun,
) -> Settlement:
    """Decide the amount of the run.

    Returns:
        The installment of a running recovery, its residual on the final
        run; at the conguaglio the balance between the annual due and the
        net paid, recovered when negative; before it ``period``, the
        percentage applied to the income of the run, capped at what is
        still due.
    """
    if plan is not None:
        return _installment(plan, run)
    balance = money(annual) - account.net
    if withholding.remaining == 1:
        if balance < _ZERO:
            return _recover(-balance, run)
        return Settlement(amount=balance, reason="settled_at_conguaglio")
    if balance < _ZERO:
        return Settlement(amount=_ZERO, reason="overpayment_pending_conguaglio")
    share = min(period, balance)
    return Settlement(amount=share, reason="share_paid" if share else "not_due")
