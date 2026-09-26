"""Legal and normative reconciliation invariants.

Invariants that verify Italian labour and tax law compliance — distinct from
the accounting identities in ledger_invariants.py.

Implemented invariants:
    L1 — every SUBSTITUTE_TAX ledger entry has a non-negative amount.
         Substitute tax (imposta sostitutiva) is always a withholding;
         refunds are posted to CREDITS, never as negative SUBSTITUTE_TAX.
    L2 — every ORDINARY_TAX ledger entry has a non-negative amount.
         IRPEF withholding is always positive; refunds use the CREDITS account
         (tax_refund_item policy), not a negative ORDINARY_TAX entry.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import ReconciliationViolation
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState

__all__: list[str] = []

_ZERO = Decimal(0)


def _check_account_non_negative(
    result: PeriodCalculationResult,
    account: AccountKind,
    invariant_id: str,
) -> list[ReconciliationViolation]:
    return [
        ReconciliationViolation(
            invariant_id=invariant_id,
            message=(
                f"LedgerEntry '{e.pay_item_id}' posts a negative amount "
                f"{e.amount} to {account.value}"
            ),
        )
        for e in result.ledger_entries
        if e.account == account and e.amount < _ZERO
    ]


def check_l1(result: PeriodCalculationResult) -> list[ReconciliationViolation]:
    """L1: every SUBSTITUTE_TAX entry has a non-negative amount.

    Returns:
        Violations for any entry that posts a negative amount to SUBSTITUTE_TAX.
    """
    return _check_account_non_negative(result, AccountKind.SUBSTITUTE_TAX, "L1")


def check_l2(result: PeriodCalculationResult) -> list[ReconciliationViolation]:
    """L2: every ORDINARY_TAX entry has a non-negative amount.

    Returns:
        Violations for any entry that posts a negative amount to ORDINARY_TAX.
    """
    return _check_account_non_negative(result, AccountKind.ORDINARY_TAX, "L2")


def check_legal(
    result: PeriodCalculationResult,
    opening: PeriodState,  # noqa: ARG001
) -> list[ReconciliationViolation]:
    """Run all legal invariants against *result*.

    Returns:
        List of :class:`ReconciliationViolation` instances, empty when all pass.
    """
    violations: list[ReconciliationViolation] = []
    violations.extend(check_l1(result))
    violations.extend(check_l2(result))
    return violations
