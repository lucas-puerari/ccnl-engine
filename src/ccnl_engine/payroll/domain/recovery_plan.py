"""RecoveryPlan: tracks the structured recovery of an over-paid tax credit."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.payroll.service.rounding import money

_ZERO = Decimal(0)

__all__ = ["RecoveryPlan"]


@dataclass(frozen=True)
class RecoveryPlan:
    """Structured installment plan for recovering an over-paid tax credit.

    Created when the amount to recover exceeds 60 EUR (D.L. 3/2020 art. 1 co. 3)
    to spread the recovery over eight equal installments.  The last installment
    absorbs any rounding residual so the sum is always exactly ``original_amount``.

    Attributes:
        kind: Identifier for the credit being recovered, e.g.
            ``"trattamento_integrativo"``.
        original_amount: Total amount to recover (positive).
        installment_amount: Uniform per-period deduction (positive, rounded).
        installments_total: Number of periods over which the recovery runs.
        installments_posted: Number of installments already deducted.
    """

    kind: str
    original_amount: Decimal
    installment_amount: Decimal
    installments_total: int
    installments_posted: int

    def __post_init__(self) -> None:
        """Validate field constraints on construction.

        Raises:
            ValueError: When any field violates its invariant.
        """
        if self.original_amount <= _ZERO:
            msg = (
                f"RecoveryPlan.original_amount must be > 0; got {self.original_amount}"
            )
            raise ValueError(msg)
        if self.installment_amount <= _ZERO:
            msg = (
                f"RecoveryPlan.installment_amount must be > 0; "
                f"got {self.installment_amount}"
            )
            raise ValueError(msg)
        if self.installments_total < 1:
            msg = (
                f"RecoveryPlan.installments_total must be >= 1; "
                f"got {self.installments_total}"
            )
            raise ValueError(msg)
        if not 0 <= self.installments_posted < self.installments_total:
            msg = (
                f"RecoveryPlan.installments_posted must be in "
                f"[0, {self.installments_total}); got {self.installments_posted}"
            )
            raise ValueError(msg)

    @property
    def residual(self) -> Decimal:
        """Amount not yet recovered."""
        return self.original_amount - money(
            self.installment_amount * self.installments_posted
        )

    @property
    def next_installment(self) -> Decimal:
        """Amount to deduct this period.

        The last installment uses the residual to absorb rounding.
        """
        if self.installments_posted == self.installments_total - 1:
            return self.residual
        return self.installment_amount

    def advance(self) -> RecoveryPlan:
        """Return a plan with ``installments_posted`` incremented by one.

        Returns:
            A new :class:`RecoveryPlan` one period further along.
        """
        return RecoveryPlan(
            kind=self.kind,
            original_amount=self.original_amount,
            installment_amount=self.installment_amount,
            installments_total=self.installments_total,
            installments_posted=self.installments_posted + 1,
        )

    @classmethod
    def create(
        cls,
        kind: str,
        original_amount: Decimal,
        installments_total: int,
    ) -> RecoveryPlan:
        """Create a fresh plan from the original recovery amount.

        Args:
            kind: Credit identifier.
            original_amount: Total amount to recover (positive).
            installments_total: Number of periods to spread across.

        Returns:
            A :class:`RecoveryPlan` with ``installments_posted=0`` and
            ``installment_amount`` set to ``original_amount / installments_total``
            rounded to two decimal places.
        """
        installment = money(original_amount / Decimal(installments_total))
        return cls(
            kind=kind,
            original_amount=original_amount,
            installment_amount=installment,
            installments_total=installments_total,
            installments_posted=0,
        )
