"""Art. 12 c. 1 lett. a and b TUIR: deduction for a dependent spouse."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.family.common import (
    DependentDeduction,
    phase_out,
    prorate,
    truncated,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.family import Dependent
    from ccnl_engine.tax.domain.family import FamilyDeductionRules

__all__ = ["spouse_annual", "spouse_deduction"]

_ZERO = Decimal(0)


def spouse_annual(income: Decimal, rules: FamilyDeductionRules) -> Decimal:
    """Return the full-year spouse deduction at the reddito complessivo.

    Lett. a, numbers 1) to 3), plus the increase of lett. b for the band
    ``income`` falls in.  With no income the ratio of number 1) is zero and
    the deduction is not due (c. 4).

    Args:
        income: Reddito complessivo of the year, ``>= 0``.
        rules: Art. 12 rules of the year.

    Returns:
        The annual deduction, not rounded.
    """
    spouse = rules.spouse
    decimals = rules.ratio_decimals
    if income <= _ZERO:
        return _ZERO
    if income <= spouse.low_income_limit:
        ratio = truncated(income / spouse.low_income_limit, decimals)
        base = spouse.full_amount - spouse.low_income_reduction * ratio
    elif income <= spouse.flat_income_limit:
        base = spouse.flat_amount
    else:
        base = phase_out(
            spouse.flat_amount,
            spouse.phase_out_limit,
            spouse.phase_out_limit - spouse.flat_income_limit,
            income,
            decimals,
        )
    return base + rules.spouse_increases.increase(income)


def spouse_deduction(
    spouse: Dependent, income: Decimal, rules: FamilyDeductionRules
) -> DependentDeduction:
    """Return the deduction for ``spouse`` in the tax year of ``rules``.

    The spouse qualifies when resident under c. 2-bis and with own income
    within the limit of c. 2, for the months of the dependency interval.

    Returns:
        The deduction, zero months when the spouse does not qualify.
    """
    qualifies = (
        spouse.residency_eligibility
        and spouse.own_income <= rules.spouse.dependent_income_threshold
    )
    months = len(spouse.dependency_months(rules.year)) if qualifies else 0
    return prorate(spouse, months, spouse_annual(income, rules))
