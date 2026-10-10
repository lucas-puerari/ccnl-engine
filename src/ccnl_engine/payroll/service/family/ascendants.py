"""Art. 12 c. 1 lett. d TUIR: deduction for cohabiting ascendants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.family.common import (
    DependentDeduction,
    phase_out,
    prorate,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal

    from ccnl_engine.payroll.domain.family import Dependent
    from ccnl_engine.tax.family.models import FamilyDeductionRules

__all__ = ["ascendant_deductions"]


def ascendant_deductions(
    ascendants: Sequence[Dependent], income: Decimal, rules: FamilyDeductionRules
) -> tuple[DependentDeduction, ...]:
    """Return the deduction of every ascendant, in the order given.

    Only ascendants living with the worker qualify (post L. 207/2024), when
    resident under c. 2-bis and with own income within the limit of c. 2.
    The share among those entitled is the declared ``allocation_pct``
    ("da ripartire pro quota tra coloro che hanno diritto alla detrazione").

    Returns:
        One deduction per ascendant, zero months when a stated condition
        excludes it.
    """
    other = rules.other_dependents
    annual = phase_out(
        other.amount,
        other.income_ceiling,
        other.income_ceiling,
        income,
        rules.ratio_decimals,
    )
    return tuple(
        prorate(
            ascendant,
            ascendant.dependency_months(rules.year)
            if ascendant.may_qualify(other.dependent_income_threshold)
            else frozenset(),
            annual,
        )
        for ascendant in ascendants
    )
