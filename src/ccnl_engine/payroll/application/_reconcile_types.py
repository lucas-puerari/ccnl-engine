"""Shared types for reconciliation invariant sub-modules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult

_ZERO = Decimal(0)


@dataclass(frozen=True)
class ReconciliationViolation:
    """One failed invariant check.

    Attributes:
        invariant_id: Short label identifying which invariant failed (e.g. ``"I9"``).
        message: Human-readable description of the failure.
        expected: The value the invariant expected, when applicable.
        actual: The value that was observed, when applicable.
    """

    invariant_id: str
    message: str
    expected: Decimal | None = None
    actual: Decimal | None = None


def _sum_account(
    result: PeriodCalculationResult,
    account: AccountKind,
) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total amount for ``account`` in ``result.ledger_entries``, or zero
        when no entries for that account are present.
    """
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        _ZERO,
    )
