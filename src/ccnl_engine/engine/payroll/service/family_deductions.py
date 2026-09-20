"""Art. 12 TUIR family deduction computation.

Computes annual deductions for:
- Spouse / civil partner (lett. a)
- Eligible children aged >= 21 (lett. c; post-AUU boundary)
- Ascendenti conviventi (lett. d; post L. 207/2024)

The engine uses ``gross_annual`` as a proxy for *reddito complessivo*;
other income sources are not modelled.

Deductions are annual figures.  Monthly conguaglio (year-end reconciliation)
is out of scope.

Eligibility is caller-declared.  The engine enforces the age-based AUU cutoff
and the 30+/non-disabled exclusion when ``birth_date`` is supplied, but
residency, disability certification, and own-income thresholds are taken as
declared by the caller.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.family import DependentRelationship
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.family import Dependent, FamilyComposition
    from ccnl_engine.engine.tax.domain.family import (
        ChildrenDeductionRules,
        FamilyDeductionRules,
        OtherDependentRules,
        SpouseDeductionRules,
    )
    from ccnl_engine.engine.tax.domain.rules import DeductionBreakpoint

_ZERO = Decimal(0)
_HUNDRED = Decimal(100)
_TWELVE = Decimal(12)

_REL_SPOUSE = DependentRelationship.SPOUSE
_REL_CHILD = DependentRelationship.CHILD
_REL_ASCENDANT = DependentRelationship.ASCENDANT


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


def _child_is_eligible(
    dep: Dependent,
    auu_age_cutoff: int,
    ref_year: int,
    income_threshold: Decimal,
    young_income_threshold: Decimal | None,
    young_age_cutoff: int,
) -> bool:
    """Return whether a child dependent is eligible for Art. 12 lett. c.

    Checks age-based AUU cutoff, own-income threshold, and residency.
    When ``birth_date`` is absent the child is treated as age-eligible
    (status stays ``"caller_declared"``), but income and residency checks
    still apply.

    The income threshold for children under ``young_age_cutoff`` is
    ``young_income_threshold`` when set; otherwise ``income_threshold``.

    Returns:
        ``True`` when the child qualifies for the deduction.
    """
    if not dep.residency_eligibility:
        return False
    age: int | None = None
    if dep.birth_date is not None:
        age = ref_year - dep.birth_date.year
        if age < auu_age_cutoff:
            return False
        if age >= 30 and not dep.disabled:
            return False
    use_young = (
        young_income_threshold is not None
        and age is not None
        and age < young_age_cutoff
    )
    effective_threshold: Decimal
    if use_young and young_income_threshold is not None:
        effective_threshold = young_income_threshold
    else:
        effective_threshold = income_threshold
    return dep.own_income <= effective_threshold


def _spouse_deduction(
    gross_annual: Decimal,
    rules: SpouseDeductionRules,
    spouse: Dependent | None,
) -> Decimal:
    """Return the Art. 12 c. 1 lett. a spouse deduction.

    Returns zero when ``spouse`` is ``None``, when residency eligibility is
    not declared, or when the spouse's own income exceeds the threshold.
    Pro-rated by ``months_dependent`` and ``allocation_pct``.

    Returns:
        Annual deduction amount, rounded to two decimal places.
    """
    if spouse is None:
        return _ZERO
    if not spouse.residency_eligibility:
        return _ZERO
    if spouse.own_income > rules.dependent_income_threshold:
        return _ZERO
    base = _deduction_from_breakpoints(gross_annual, rules.breakpoints)
    months_ratio = Decimal(spouse.months_dependent) / _TWELVE
    return money(base * months_ratio * spouse.allocation_pct / _HUNDRED)


def _children_deduction(
    gross_annual: Decimal,
    rules: ChildrenDeductionRules,
    children: list[Dependent],
    ref_year: int,
) -> Decimal:
    """Return the Art. 12 c. 1 lett. c children deduction.

    Eligible children are those aged 21-29 and disabled children aged 30+,
    with own income within the applicable threshold and residency eligibility.

    Each child's deduction is pro-rated by ``months_dependent`` and
    ``allocation_pct``.

    Returns:
        Total annual deduction for all eligible children, rounded.
    """
    eligible = [
        c
        for c in children
        if _child_is_eligible(
            c,
            rules.auu_age_cutoff,
            ref_year,
            rules.dependent_income_threshold,
            rules.young_child_income_threshold,
            rules.young_age_cutoff,
        )
    ]
    total = len(eligible)
    if total == 0:
        return _ZERO

    extra = max(0, total - 1)
    ceiling = (
        rules.income_ceiling + Decimal(extra) * rules.income_ceiling_increment_per_child
    )
    taper = max(_ZERO, (ceiling - gross_annual) / ceiling)

    result = _ZERO
    for child in eligible:
        per_child = money(rules.base_amount * taper)
        pro_rata = (
            per_child
            * Decimal(child.months_dependent)
            / _TWELVE
            * child.allocation_pct
            / _HUNDRED
        )
        result += money(pro_rata)
    return money(result)


def _other_deduction(
    gross_annual: Decimal,
    rules: OtherDependentRules,
    ascendants: list[Dependent],
) -> Decimal:
    """Return the Art. 12 c. 1 lett. d other-dependents deduction.

    Only cohabiting ascendants with residency eligibility and own income
    within the threshold qualify (post L. 207/2024).

    Returns:
        Total annual deduction for all qualifying ascendants, rounded.
    """
    eligible = [
        a
        for a in ascendants
        if a.cohabiting
        and a.residency_eligibility
        and a.own_income <= rules.dependent_income_threshold
    ]
    if not eligible:
        return _ZERO
    taper = max(_ZERO, (rules.income_ceiling - gross_annual) / rules.income_ceiling)
    result = _ZERO
    for asc in eligible:
        per_asc = money(rules.amount * taper)
        pro_rata = (
            per_asc
            * Decimal(asc.months_dependent)
            / _TWELVE
            * asc.allocation_pct
            / _HUNDRED
        )
        result += money(pro_rata)
    return money(result)


def compute_family_deductions(
    family: FamilyComposition,
    gross_annual: Decimal,
    rules: FamilyDeductionRules,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Compute Art. 12 TUIR family deductions.

    All returned amounts are annual.  The caller must subtract
    ``total_deduction`` from ``irpef_gross - work_income_deduction``
    (floored at zero) to obtain the effective ``irpef_net``.

    Age-based eligibility for children uses ``rules.year`` as the reference
    year.  Eligibility conditions the engine cannot verify (disability
    certification, residency) are taken as declared.

    Args:
        family: Caller-supplied family composition.
        gross_annual: Annual gross pay — used as proxy for reddito complessivo.
        rules: Art. 12 TUIR parameters for the fiscal year.

    Returns:
        A 4-tuple of (spouse_deduction, children_deduction,
        other_deduction, total_deduction).  All amounts are positive and
        rounded to two decimal places.
    """
    spouse = next((d for d in family.dependents if d.relationship == _REL_SPOUSE), None)
    children = [d for d in family.dependents if d.relationship == _REL_CHILD]
    ascendants = [d for d in family.dependents if d.relationship == _REL_ASCENDANT]

    sp = _spouse_deduction(gross_annual, rules.spouse, spouse)
    ch = _children_deduction(gross_annual, rules.children, children, rules.year)
    ot = _other_deduction(gross_annual, rules.other_dependents, ascendants)
    total = money(sp + ch + ot)
    return sp, ch, ot, total
