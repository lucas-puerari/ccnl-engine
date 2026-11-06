"""What the indemnity of the residual leave is paid from, and what it pays."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.decision.models import CalculationDecision, CalculationIssue
    from ccnl_engine.leave.balance.models import LeaveAccount
    from ccnl_engine.leave.handlers import LeaveTerms
    from ccnl_engine.leave.models import PermitDeadline
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import CompetencePeriod, PayItem
    from ccnl_engine.pay_item.policies import PolicyContext, PolicyResolver

__all__ = [
    "PERMIT_DEADLINE",
    "TERMINATION_RESIDUAL_LEAVE",
    "LeaveSettlement",
    "SettlementTerms",
]

#: Capability of the indemnity for the residual leave.
TERMINATION_RESIDUAL_LEAVE = "termination_residual_leave"
#: Capability of the permits paid at the deadline of their year.
PERMIT_DEADLINE = "leave"
_ZERO = Decimal(0)


@dataclass(frozen=True)
class SettlementTerms:
    """What the indemnity of a run that closes the employment is paid from.

    Attributes:
        leave: Leave rules of the CCNL, with its ruleset.
        monthly_pay: Monthly pay of a fully employed month (the retribuzione
            di fatto the CCNL divides).
        hourly_divisor: Hourly divisor of the CCNL on the run date, ``None``
            when not in force.
        part_time_ratio: Weekly over full-time hours of a part-time worker,
            ``None`` for a full-time worker: the hourly quota of a permit is
            that of the full-time pay.
        competence_period: Competence period of the run.
        payment_date: Payment date of the run.
        tag: Run identifier, the tag of the item ids.
        resolver: Policy resolver of the pay-item kinds.
        context: Context the policy is resolved in.
        deadline: The deadline the permits are paid at
            (``LeaveRules.permit_deadline``), ``None`` at the end of the
            employment.
    """

    leave: LeaveTerms
    monthly_pay: Decimal
    hourly_divisor: Decimal | None
    part_time_ratio: Decimal | None
    competence_period: CompetencePeriod
    payment_date: date
    tag: str
    resolver: PolicyResolver
    context: PolicyContext
    deadline: PermitDeadline | None = None


@dataclass(frozen=True)
class LeaveSettlement:
    """Indemnity of the residual leave, the bases it enters and its decision.

    Attributes:
        account: The leave account after the settlement.
        decision: The ``termination_residual_leave`` decision.
        items: One leave settlement item per bucket paid.
        entries: Cash-earning ledger entries of the items.
        inps_base: Amount entering the INPS contribution base.
        tfr_base: Amount entering the TFR base.
        irpef_base: Amount entering the ordinary IRPEF base.
        issues: Facts missing to pay the indemnity.
    """

    account: LeaveAccount
    decision: CalculationDecision
    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    inps_base: Decimal = _ZERO
    tfr_base: Decimal = _ZERO
    irpef_base: Decimal = _ZERO
    issues: tuple[CalculationIssue, ...] = field(default=())
