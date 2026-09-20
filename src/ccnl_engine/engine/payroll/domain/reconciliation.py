"""Reconciliation domain types: violations and the reconciliation error."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class ReconciliationViolation:
    """A single failed accounting invariant."""

    code: str
    message: str


class ReconciliationError(Exception):
    """Raised when one or more accounting invariants are violated."""

    def __init__(self, violations: list[ReconciliationViolation]) -> None:
        """Initialise with a non-empty list of violations.

        Args:
            violations: The invariants that failed.
        """
        self.violations = violations
        codes = ", ".join(v.code for v in violations)
        super().__init__(f"Reconciliation failed: {codes}")
