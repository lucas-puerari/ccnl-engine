"""Art. 12 TUIR family deduction computation.

Computes annual deductions for:
- Spouse / civil partner (lett. a)
- Eligible children aged >= 21 (lett. c; post-AUU boundary)
- Ascendenti conviventi (lett. d; post L. 207/2024)

The engine uses ``gross_annual`` as a proxy for *reddito complessivo*;
other income sources are not modelled.

Deductions are annual figures.  Monthly conguaglio (year-end reconciliation)
is out of scope.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.engine.tax.domain.family import (
        ChildrenDeductionRules,
        FamilyDeductionRules,
        OtherDependentRules,
        SpouseDeductionRules,
    )
    from ccnl_engine.engine.tax.domain.rules import DeductionBreakpoint

_ZERO = Decimal(0)


def _interpolate(
    income: Decimal,
    lo_income: Decimal,
    hi_income: Decimal,
    lo_ded: Decimal,
    hi_ded: Decimal,
) -> Decimal:
    """Linear interpolation between two deduction breakpoints.

    Returns:
        The interpolated deduction, rounded to two decimal places.
    """
    fraction = (income - lo_income) / (hi_income - lo_income)
    return money(lo_ded + fraction * (hi_ded - lo_ded))


def _deduction_from_breakpoints(
    income: Decimal,
    points: list[DeductionBreakpoint],
) -> Decimal:
    """Evaluate a piecewise-linear deduction schedule.

    Mirrors the logic of
    :func:`~ccnl_engine.engine.payroll.service.irpef.work_income_deduction`.

    Returns:
        The deduction amount for *income*, rounded to two decimal places.
    """
    if not points:
        return _ZERO
    first = points[0]
    if first.income_up_to is not None and income <= first.income_up_to:
        return money(first.deduction)
    for i in range(len(points) - 1):
        lo = points[i]
        hi = points[i + 1]
        lo_income = lo.income_up_to
        hi_income = hi.income_up_to
        if lo_income is None:
            break  # pragma: no cover
        if hi_income is None:
            return money(hi.deduction)
        if lo_income < income <= hi_income:
            return _interpolate(
                income, lo_income, hi_income, lo.deduction, hi.deduction
            )
    return money(points[-1].deduction)


def _spouse_deduction(
    gross_annual: Decimal,
    rules: SpouseDeductionRules,
) -> Decimal:
    """Return the Art. 12 c. 1 lett. a spouse deduction.

    Returns:
        Annual deduction amount, rounded to two decimal places.
        Zero when ``gross_annual`` exceeds the taper ceiling.
    """
    return _deduction_from_breakpoints(gross_annual, rules.breakpoints)


def _children_deduction(
    gross_annual: Decimal,
    rules: ChildrenDeductionRules,
    n_standard: int,
    n_disabled: int,
) -> Decimal:
    """Return the Art. 12 c. 1 lett. c children deduction.

    Each eligible child gives a deduction tapered by income.  The taper
    ceiling increases by ``income_ceiling_increment_per_child`` for each child
    beyond the first.

    Args:
        gross_annual: Annual gross pay (proxy for reddito complessivo).
        rules: Children deduction parameters.
        n_standard: Number of standard eligible children (age >= AUU cutoff).
        n_disabled: Number of disabled eligible children (age >= AUU cutoff).

    Returns:
        Total annual deduction for all eligible children, rounded.
    """
    total_children = n_standard + n_disabled
    if total_children == 0:
        return _ZERO

    # Adjust the income ceiling for multiple children (Art. 12 c. 1 lett. c).
    extra_children = max(0, total_children - 1)
    effective_ceiling = (
        rules.income_ceiling
        + Decimal(extra_children) * rules.income_ceiling_increment_per_child
    )

    taper = max(_ZERO, (effective_ceiling - gross_annual) / effective_ceiling)
    deduction_standard = money(rules.base_amount * taper) * n_standard
    deduction_disabled = money(rules.disabled_amount * taper) * n_disabled
    return money(deduction_standard + deduction_disabled)


def _other_deduction(
    gross_annual: Decimal,
    rules: OtherDependentRules,
    n_ascendenti: int,
) -> Decimal:
    """Return the Art. 12 c. 1 lett. d other-dependents deduction.

    Only ascendenti conviventi qualify post L. 207/2024.

    Returns:
        Total annual deduction for all qualifying ascendants, rounded.
    """
    if n_ascendenti == 0:
        return _ZERO
    taper = max(_ZERO, (rules.income_ceiling - gross_annual) / rules.income_ceiling)
    return money(money(rules.amount * taper) * n_ascendenti)


def compute_family_deductions(
    family: FamilyComposition,
    gross_annual: Decimal,
    rules: FamilyDeductionRules,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Compute Art. 12 TUIR family deductions.

    All returned amounts are annual.  The caller must subtract
    ``total_deduction`` from ``irpef_gross - work_income_deduction``
    (floored at zero) to obtain the effective ``irpef_net``.

    The engine uses ``gross_annual`` as a proxy for *reddito complessivo*.
    Other income sources (rental, financial, etc.) are not modelled.

    Args:
        family: Caller-supplied family composition.
        gross_annual: Annual gross pay — used as proxy for reddito complessivo.
        rules: Art. 12 TUIR parameters for the fiscal year.

    Returns:
        A 4-tuple of (spouse_deduction, children_deduction,
        other_deduction, total_deduction).  All amounts are positive and
        rounded to two decimal places.
    """
    spouse = (
        _spouse_deduction(gross_annual, rules.spouse)
        if family.spouse_dependent
        else _ZERO
    )
    children = _children_deduction(
        gross_annual,
        rules.children,
        family.children_21_or_older,
        family.children_21_or_older_disabled,
    )
    other = _other_deduction(
        gross_annual, rules.other_dependents, family.ascendenti_conviventi
    )
    total = money(spouse + children + other)
    return spouse, children, other, total
