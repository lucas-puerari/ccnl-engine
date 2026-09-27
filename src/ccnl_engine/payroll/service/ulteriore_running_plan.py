"""Installments of an ulteriore detrazione plan within its own tax year.

A plan opened by the conguaglio of year N (L. 207/2024 art. 1 c. 7) lives
inside the IRPEF of N: the conguaglio withholds the first installment and
defers the rest.  An adjustment run of N settles the cumulative balance
again, so it would take back the whole deferred residual; it withholds the
balance less what is still deferred after its own installment instead.  On
the last run of the employment nothing stays deferred (AdE circ. 4/E/2025
par. 1.2).
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.recovery_plan import PostedInstallment

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.recovery_plan import (
        InstallmentRun,
        RecoveryPlan,
    )
    from ccnl_engine.payroll.service.ulteriore_recovery import UlterioreSettlement

__all__ = ["AT_TERMINATION", "post_running_plan"]

_ZERO = Decimal(0)
#: Reason of an excess recovered in full because no payslip follows.
AT_TERMINATION = "overpayment_recovered_at_termination"


def post_running_plan(
    balance: Decimal,
    settlement: UlterioreSettlement,
    plan: RecoveryPlan,
    run: InstallmentRun,
) -> UlterioreSettlement:
    """Post an installment of a plan opened by a conguaglio of the tax year.

    The run settles the cumulative balance again, and ``balance`` holds the
    residual of ``plan`` still deferred.  The run keeps deferring what is
    left after the installment it posts; on the final run of the
    employment nothing is left.  When ``balance`` is below what would stay
    deferred, e.g. an adjustment that restores the deduction, the plan is
    closed and the cumulative balance settles the year on the run
    (``recovery_absorbed_by_conguaglio``).  A further excess the run finds
    while the plan runs is recovered in full on the run, not merged into
    the plan (``overpayment_recovered``).

    Args:
        balance: IRPEF of the run on the cumulative balance, the residual
            of ``plan`` included.
        settlement: What the run recognizes of the deduction, with nothing
            deferred.
        plan: The running plan.
        run: The run: final or adjustment.

    Returns:
        The settlement with the installment posted, the part still deferred
        and the plan after the run.
    """
    posted = plan.post(run)
    deferred = _ZERO if posted.remaining is None else posted.remaining.residual
    if balance < deferred:
        posted = PostedInstallment(
            max(balance, _ZERO), "recovery_absorbed_by_conguaglio", None
        )
        deferred = _ZERO
    in_full = settlement.reason == AT_TERMINATION and not run.final
    return replace(
        settlement,
        reason="overpayment_recovered" if in_full else settlement.reason,
        deferred=deferred,
        plan=posted.remaining,
        installment=posted,
        residual_before=plan.residual,
    )
