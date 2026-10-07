"""Art. 12 c. 1 lett. c TUIR: deduction for dependent children.

A child gives right to the deduction in a month when the dependency holds
and the child has turned 21 by the end of the month and had not turned 30
at its start, or has a disability: the month of the 21st birthday is the
first, the month of the 30th the last (c. 3).  The number of children that
raises the income ceiling counts every child entitled in some month.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.family.common import (
    DependentDeduction,
    phase_out,
    prorate,
)
from ccnl_engine.payroll.service.family.spouse import spouse_annual

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal

    from ccnl_engine.payroll.domain.family import Dependent
    from ccnl_engine.tax.domain.family import (
        ChildrenDeductionRules,
        FamilyDeductionRules,
    )

__all__ = ["child_months", "children_deductions", "children_within_income_limit"]

_NO_BIRTH_DATE = date.min


def _birth(child: Dependent) -> date:
    # A child always has a birth date: Dependent rejects one without.
    return child.birth_date or _NO_BIRTH_DATE


def _income_limit(
    child: Dependent, rules: ChildrenDeductionRules, year: int
) -> Decimal:
    """Return the own-income limit of ``child`` in ``year`` (c. 2).

    Returns:
        The higher limit for the whole year in which the child turns at
        most ``young_child_max_age``, the general one otherwise.
    """
    if year - _birth(child).year <= rules.young_child_max_age:
        return rules.young_child_income_threshold
    return rules.dependent_income_threshold


def _in_age_band(
    child: Dependent, rules: ChildrenDeductionRules, year: int, month: int
) -> bool:
    birth = _birth(child)
    age_at_end = year - birth.year - (1 if month < birth.month else 0)
    age_at_start = age_at_end - (1 if month == birth.month else 0)
    if age_at_end < rules.auu_age_cutoff:
        return False
    return child.disabled or age_at_start < rules.age_limit


def child_months(child: Dependent, rules: ChildrenDeductionRules, year: int) -> int:
    """Return the months of ``year`` in which ``child`` gives right to lett. c.

    Returns:
        Zero when the child is stated not resident under c. 2-bis or its
        stated own income exceeds its limit; an unknown condition does not
        exclude a month.
    """
    if not child.may_qualify(_income_limit(child, rules, year)):
        return 0
    return sum(
        1
        for month in child.dependency_months(year)
        if _in_age_band(child, rules, year, month)
    )


def children_within_income_limit(
    children: Sequence[Dependent], rules: ChildrenDeductionRules, year: int
) -> bool | None:
    """Return whether a child is in the condition of art. 12 c. 2 in ``year``.

    The condition is the own-income limit alone: neither the age band of
    lett. c nor c. 2-bis applies.  It selects the higher fringe-benefit
    threshold (L. 207/2024 art. 1 c. 390: "figli [...] che si trovano nelle
    condizioni previste dall'articolo 12, comma 2").  Only a child whose
    dependency interval touches ``year`` counts.

    Returns:
        ``True`` when a child's stated own income is within its limit,
        ``None`` when none is and a child's own income is unknown,
        ``False`` otherwise.
    """
    found: bool | None = False
    for child in children:
        if not child.dependency_months(year):
            continue
        if child.own_income is None:
            found = None
        elif child.own_income <= _income_limit(child, rules, year):
            return True
    return found


def children_deductions(
    children: Sequence[Dependent],
    income: Decimal,
    rules: FamilyDeductionRules,
    *,
    sole_parent: bool,
) -> tuple[DependentDeduction, ...]:
    """Return the deduction of every child, in the order given.

    For a sole parent the eldest entitled child takes the spouse deduction
    of lett. a and b when more favourable (lett. c, last period).

    Returns:
        One deduction per child, zero months when it is not entitled.
    """
    child_rules = rules.children
    months = [child_months(child, child_rules, rules.year) for child in children]
    entitled = [index for index, m in enumerate(months) if m]
    ceiling = child_rules.income_ceiling + (
        max(len(entitled) - 1, 0) * child_rules.income_ceiling_increment_per_child
    )
    annual = phase_out(
        child_rules.base_amount, ceiling, ceiling, income, rules.ratio_decimals
    )
    first = (
        min(entitled, key=lambda index: _birth(children[index]))
        if sole_parent and entitled
        else None
    )
    return tuple(
        prorate(
            child,
            m,
            max(annual, spouse_annual(income, rules)) if index == first else annual,
        )
        for index, (child, m) in enumerate(zip(children, months, strict=True))
    )
