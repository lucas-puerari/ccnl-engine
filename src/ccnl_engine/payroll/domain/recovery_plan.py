"""RecoveryPlan: tracks the structured recovery of an over-paid tax credit.

A plan posts one installment per payslip, except on the last run of the
employment: there no later pay can carry the installments, so the whole
residual is recovered on that run.  AdE circ. 29/E/2020 par. 6 (trattamento
integrativo) and circ. 4/E/2025 par. 1.2 (somma esente and ulteriore
detrazione): "in caso di cessazione del rapporto di lavoro, il sostituto
d'imposta, in sede di conguaglio di fine rapporto, è tenuto a recuperare i
benefici fiscali non spettanti in un'unica soluzione, indipendentemente
dall'importo, in mancanza di ulteriori retribuzioni sulle quali operare il
recupero in maniera dilazionata".
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.payroll.domain.rounding import money

_ZERO = Decimal(0)
#: Reason of a recovery settled in full on the last run of the employment.
SETTLED_AT_TERMINATION = "settled_at_termination"
#: Reason of an installment posted on an adjustment run.
ADJUSTMENT_RUN_INSTALLMENT = "installment_posted_adjustment_run"

__all__ = [
    "ADJUSTMENT_RUN_INSTALLMENT",
    "SETTLED_AT_TERMINATION",
    "InstallmentRun",
    "PostedInstallment",
    "RecoveryPlan",
]


@dataclass(frozen=True)
class InstallmentRun:
    """The run an installment is posted on, as far as the plan is concerned.

    Attributes:
        final: Whether the run is the last one of the employment: the
            employment ends in the tax year and the run closes its last
            withholding slot, or the run is a termination run.
        adjustment: Whether the run is an adjustment run.
    """

    final: bool = False
    adjustment: bool = False


@dataclass(frozen=True)
class PostedInstallment:
    """What a run recovers of a plan.

    Attributes:
        amount: Amount recovered on the run (positive).
        reason: Reason code: ``installment_posted``,
            ``last_installment_posted``,
            ``installment_posted_adjustment_run`` or
            ``settled_at_termination``.
        remaining: The plan after the run, ``None`` once it is settled.
    """

    amount: Decimal
    reason: str
    remaining: RecoveryPlan | None


@dataclass(frozen=True)
class RecoveryPlan:
    """Structured installment plan for recovering an over-paid tax credit.

    Created when the amount to recover exceeds 60 EUR, to spread the recovery
    over equal installments: eight for the trattamento integrativo (D.L.
    3/2020 art. 1 co. 3), ten for the somma esente (L. 207/2024 art. 1 c. 7).
    The last installment absorbs any rounding residual so the sum is always
    exactly ``original_amount``.

    Attributes:
        kind: Identifier for the credit being recovered, e.g.
            ``"trattamento_integrativo"`` or ``"somma_esente"``.
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

    def post(self, run: InstallmentRun) -> PostedInstallment:
        """Return what ``run`` recovers of the plan.

        The single rule shared by every recovered credit: the next
        installment on an ordinary or adjustment run, the whole residual on
        the final run of the employment.

        Args:
            run: The run the installment is posted on.

        Returns:
            The amount recovered, its reason and the plan still running.
        """
        if run.final:
            return PostedInstallment(self.residual, SETTLED_AT_TERMINATION, None)
        last = self.installments_posted == self.installments_total - 1
        reason = "last_installment_posted" if last else "installment_posted"
        return PostedInstallment(
            self.next_installment,
            ADJUSTMENT_RUN_INSTALLMENT if run.adjustment else reason,
            None if last else self.advance(),
        )

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
