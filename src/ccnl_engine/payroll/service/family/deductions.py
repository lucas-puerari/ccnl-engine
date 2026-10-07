"""Art. 12 TUIR family deductions of a tax year: every dependent and the sum.

The deductions are annual: each dependent's full-year amount at the reddito
complessivo, times the months it is due over twelve (c. 3), times the share
allocated to the worker, rounded to the cent.  Eligibility conditions the
engine cannot verify (residency, disability certification, cohabitation,
the dependents' own income) are taken as declared; one left unknown grants
no deduction and is named in :attr:`FamilyDeductions.missing_facts`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.family import DependentRelationship
from ccnl_engine.payroll.service.family.ascendants import ascendant_deductions
from ccnl_engine.payroll.service.family.children import children_deductions
from ccnl_engine.payroll.service.family.spouse import spouse_deduction

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.service.family.common import DependentDeduction
    from ccnl_engine.tax.domain.family import FamilyDeductionRules

__all__ = ["FamilyDeductions", "compute_family_deductions"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class FamilyDeductions:
    """Art. 12 TUIR deductions of the year, one per declared dependent.

    Attributes:
        dependents: The deduction of each dependent: spouse, children,
            ascendants, each in declaration order.
    """

    dependents: tuple[DependentDeduction, ...]

    def of(self, relationship: DependentRelationship) -> Decimal:
        """Return the total deduction for the dependents of ``relationship``.

        Returns:
            The sum of their rounded deductions.
        """
        return sum(
            (
                d.amount
                for d in self.dependents
                if d.dependent.relationship is relationship
            ),
            _ZERO,
        )

    @property
    def total(self) -> Decimal:
        """Total annual family deductions."""
        return sum((d.amount for d in self.dependents), _ZERO)

    def of_month(self, month: int) -> Decimal:
        """Return the deductions of one month of the year (art. 12 c. 3).

        Returns:
            The sum of :meth:`DependentDeduction.of_month` of every
            dependent.
        """
        return sum((d.of_month(month) for d in self.dependents), _ZERO)

    @property
    def entitled(self) -> bool:
        """Whether a dependent gives right to a deduction in some month.

        When none does, the deductions are zero whatever the income.
        """
        return any(d.months for d in self.dependents)

    @property
    def missing_facts(self) -> tuple[str, ...]:
        """Conditions left unknown by a dependant that may qualify.

        Returns:
            The field names, each once, in the order first met.
        """
        return tuple(dict.fromkeys(f for d in self.dependents for f in d.missing_facts))

    @property
    def exhausted(self) -> bool:
        """Whether no dependant can take a deduction at more income.

        A dependant that may qualify takes none when its annual amount is
        past the phase-out, where it stays zero with more income, or its
        stated share is zero.  A dependant with a missing fact counts
        with its annual amount.
        """
        return not any(
            d.months and d.annual and d.dependent.share for d in self.dependents
        )


def compute_family_deductions(
    family: FamilyComposition, income: Decimal, rules: FamilyDeductionRules
) -> FamilyDeductions:
    """Compute the Art. 12 TUIR family deductions of the tax year of ``rules``.

    Args:
        family: Caller-supplied family composition.
        income: Reddito complessivo of the year (art. 12 c. 4-bis: net of
            the main dwelling); a negative value counts as zero.
        rules: Art. 12 TUIR parameters of the tax year.

    Returns:
        The deduction of every dependent.
    """
    income = max(income, _ZERO)
    by_kind = {
        kind: [d for d in family.dependents if d.relationship is kind]
        for kind in DependentRelationship
    }
    spouses = by_kind[DependentRelationship.SPOUSE]
    return FamilyDeductions(
        tuple(spouse_deduction(s, income, rules) for s in spouses)
        + children_deductions(
            by_kind[DependentRelationship.CHILD],
            income,
            rules,
            sole_parent=family.sole_parent,
        )
        + ascendant_deductions(by_kind[DependentRelationship.ASCENDANT], income, rules)
    )
