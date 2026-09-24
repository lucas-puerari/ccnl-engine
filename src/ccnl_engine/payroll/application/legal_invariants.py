"""Legal and normative reconciliation invariants (stub).

Future home for invariants that verify Italian labour and tax law compliance
(e.g. minimum net salary rules, maximum withholding rates, deduction caps).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import ReconciliationViolation

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState

__all__: list[str] = []


def check_legal(
    result: PeriodCalculationResult,  # noqa: ARG001
    opening: PeriodState,  # noqa: ARG001
) -> list[ReconciliationViolation]:
    """Run all legal invariants. Currently a no-op stub.

    Returns:
        Empty list (no legal invariants implemented yet).
    """
    return []
