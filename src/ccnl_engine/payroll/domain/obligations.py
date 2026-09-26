"""Obligations of the employment that survive the change of tax year.

Unlike :class:`~ccnl_engine.payroll.domain.tax_year_state.TaxYearState`,
nothing here restarts on 1 January: an installment recovery opened by the
conguaglio of year N keeps running on the payslips of year N+1 until its
last installment (D.L. 3/2020 art. 1 c. 3 for the trattamento integrativo,
L. 207/2024 art. 1 c. 7 for the somma esente).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan

__all__ = [
    "RECOVERY_RULES",
    "SOMMA_ESENTE_RECOVERY",
    "TRATTAMENTO_RECOVERY",
    "EmploymentObligations",
    "RecoveryObligation",
    "RecoveryRule",
]

#: ``RecoveryPlan.kind`` of the trattamento integrativo recovery.
TRATTAMENTO_RECOVERY = "trattamento_integrativo"
#: ``RecoveryPlan.kind`` of the somma esente recovery.
SOMMA_ESENTE_RECOVERY = "somma_esente"
_MIN_TAX_YEAR = 2020


@final
@dataclass(frozen=True)
class RecoveryRule:
    """How the over-payment of one credit is recovered.

    Attributes:
        rule: Identifier of the norm, recorded on each installment decision.
        installments: Number of equal installments above the threshold.
    """

    rule: str
    installments: int


#: Recovery rule per recovered credit.  Both credits recover up to 60 EUR on
#: one payslip; above it the installments differ.
RECOVERY_RULES: dict[str, RecoveryRule] = {
    TRATTAMENTO_RECOVERY: RecoveryRule(rule="dl3-2020-art1-c3", installments=8),
    SOMMA_ESENTE_RECOVERY: RecoveryRule(rule="l207-2024-art1-c7", installments=10),
}


@final
@dataclass(frozen=True)
class RecoveryObligation:
    """An installment recovery and the tax year of the credit it recovers.

    Attributes:
        tax_year: Tax year whose conguaglio found the credit not due.  The
            installments posted in that year enter the ``recovered`` total
            of its :class:`~ccnl_engine.payroll.domain.ytd_accounts\
.CreditAccount`; those posted in a later year are carried: they are
            deducted on the payslip but belong to no account of the later
            year.
        plan: The installment plan, with the installments still to post.
    """

    tax_year: int
    plan: RecoveryPlan

    def __post_init__(self) -> None:
        """Validate the origin tax year and the recovered credit.

        Only the recoveries of :data:`RECOVERY_RULES` are modelled; a plan of
        another kind is rejected rather than carried without effect.

        Raises:
            ValueError: When ``tax_year`` is before 2020 or ``plan.kind`` is
                not a key of :data:`RECOVERY_RULES`.
        """
        if self.plan.kind not in RECOVERY_RULES:
            msg = (
                f"RecoveryObligation.plan.kind must be one of "
                f"{sorted(RECOVERY_RULES)}; got {self.plan.kind!r}"
            )
            raise ValueError(msg)
        if self.tax_year < _MIN_TAX_YEAR:
            msg = f"RecoveryObligation.tax_year must be >= 2020; got {self.tax_year}"
            raise ValueError(msg)

    def advanced(self) -> RecoveryObligation | None:
        """Return the obligation after posting one installment.

        Returns:
            The obligation one installment further along, or ``None`` when
            the installment just posted was the last one.
        """
        plan = self.plan
        if plan.installments_posted == plan.installments_total - 1:
            return None
        return RecoveryObligation(tax_year=self.tax_year, plan=plan.advance())


@final
@dataclass(frozen=True)
class EmploymentObligations:
    """Obligations carried from run to run across tax years.

    Attributes:
        recoveries: Active installment recoveries, at most one per credit
            kind and origin tax year, in the order they were opened.
    """

    recoveries: tuple[RecoveryObligation, ...] = ()

    def __post_init__(self) -> None:
        """Reject two recoveries of the same credit opened in the same year.

        Raises:
            ValueError: When two recoveries share ``tax_year`` and kind.
        """
        keys = [(r.tax_year, r.plan.kind) for r in self.recoveries]
        if len(set(keys)) != len(keys):
            msg = (
                "EmploymentObligations.recoveries holds two recoveries of the "
                f"same credit opened in the same tax year: {keys}"
            )
            raise ValueError(msg)

    @property
    def latest_tax_year(self) -> int | None:
        """Latest origin tax year of any recovery, ``None`` when there is none."""
        return max((r.tax_year for r in self.recoveries), default=None)

    def recovery_of(self, tax_year: int, kind: str) -> RecoveryPlan | None:
        """Return the plan of credit ``kind`` opened in ``tax_year``, if any.

        Returns:
            The matching plan, or ``None``.
        """
        return next(
            (
                r.plan
                for r in self.recoveries
                if r.tax_year == tax_year and r.plan.kind == kind
            ),
            None,
        )

    def carried_into(self, tax_year: int) -> tuple[RecoveryObligation, ...]:
        """Return the recoveries opened before ``tax_year``.

        Returns:
            The recoveries whose origin year is earlier than ``tax_year``,
            in their stored order.
        """
        return tuple(r for r in self.recoveries if r.tax_year < tax_year)
