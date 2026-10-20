"""Handler of the paid leave taken in a period.

The leave is paid at the normal rate: the monthly pay of the period already
holds the time off, so the handler posts nothing.  It decides the ``leave``
capability: final when the CCNL accrues the bucket the leave is taken from,
incomplete otherwise, since its balance (and the indemnity of the residual
at the end of the employment) cannot be kept.  The balance itself is
consumed by :func:`~ccnl_engine.leave.services.run_leave`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

if TYPE_CHECKING:
    from ccnl_engine.leave.inputs import LeaveTakenEvent
    from ccnl_engine.leave.models import LeaveRules

__all__ = ["LEAVE", "LeaveTerms", "_handle_leave_taken"]

#: Capability of the leave taken.
LEAVE = "leave"
#: Reason of leave taken from a bucket the CCNL accrues.
PAID_IN_MONTHLY_PAY = "paid_in_monthly_pay"
#: Reason of leave taken from a bucket the CCNL does not accrue.
BUCKET_NOT_MODELLED = "leave_bucket_not_modelled"


@dataclass(frozen=True)
class LeaveTerms:
    """The leave rules of the CCNL of a run.

    Attributes:
        rules: Leave rules of the CCNL, ``None`` when it has none.
        ruleset: Ruleset identifier of the CCNL.
        version: Ruleset version.
    """

    rules: LeaveRules | None
    ruleset: str
    version: str


def _handle_leave_taken(event: LeaveTakenEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Decide the leave taken: no pay of its own, a balance consumed.

    Returns:
        Handler result with the ``leave`` decision only.
    """
    terms = ctx.leave
    rules = None if terms is None else terms.rules
    modelled = rules is not None and event.bucket in rules.buckets
    provenance = None if rules is None else rules.provenance
    decision = CalculationDecision(
        capability=LEAVE,
        status=CalculationStatus.FINAL if modelled else CalculationStatus.INCOMPLETE,
        reason_code=PAID_IN_MONTHLY_PAY if modelled else BUCKET_NOT_MODELLED,
        rule=(
            "work_rules.leave_rules"
            if terms is None
            else f"{terms.ruleset}:work_rules.leave_rules"
        ),
        rule_version="unknown" if terms is None else terms.version,
        inputs={
            "bucket": str(event.bucket),
            "quantity": event.quantity,
            "unit": event.bucket.unit,
        },
        source=None if provenance is None else provenance.location,
        amount=Decimal(0),
    )
    return EventEffect(decisions=[decision])
