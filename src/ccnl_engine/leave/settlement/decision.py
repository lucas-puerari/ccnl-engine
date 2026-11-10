"""Decision for the leave settlement of a run."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.leave.settlement.models import (
    PERMIT_DEADLINE,
    TERMINATION_RESIDUAL_LEAVE,
    SettlementTerms,
)

if TYPE_CHECKING:
    from decimal import Decimal


def settlement_decision(
    terms: SettlementTerms,
    status: CalculationStatus,
    reason: str,
    inputs: dict[str, Decimal | str],
    amount: Decimal | None,
) -> CalculationDecision:
    """Describe a deadline or termination settlement using its rule provenance.

    Returns:
        The decision with the source and amount of the settlement.
    """
    leave = terms.leave
    rules = leave.rules
    basis = None if rules is None else rules.termination
    deadline = terms.deadline
    provenance = (
        deadline.provenance
        if deadline is not None
        else None
        if basis is None
        else basis.provenance
    )
    field = "termination" if deadline is None else "permit_deadline"
    return CalculationDecision(
        capability=TERMINATION_RESIDUAL_LEAVE if deadline is None else PERMIT_DEADLINE,
        status=status,
        reason_code=reason,
        rule=f"{leave.ruleset}:work_rules.leave_rules.{field}",
        rule_version=leave.version,
        inputs=inputs,
        source=None if provenance is None else provenance.location,
        amount=amount,
    )
