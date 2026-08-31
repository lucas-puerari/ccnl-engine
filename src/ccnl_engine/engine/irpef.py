"""IRPEF (personal income tax) calculation.

SIMPLIFICATION: only Art. 11 TUIR brackets and Art. 13 TUIR work-income
deduction. Not modelled: addizionali regionali/comunali; detrazioni per
carichi di famiglia (Art. 12); EUR 65 additional deduction (Art. 13
co. 1-bis, D.Lgs. 216/2023); sterilization for redditi > 200 k (Art. 1
co. 3-4 L. 199/2025); bonus/trattamento integrativo (Art. 1 D.L. 3/2020).
"""

from decimal import Decimal

from ccnl_engine.engine.rounding import money
from ccnl_engine.tax.models import YearRules

_ZERO = Decimal(0)


def irpef_gross(taxable_income: Decimal, rules: YearRules) -> Decimal:
    """Compute gross IRPEF on taxable_income using marginal brackets."""
    if taxable_income <= _ZERO:
        return _ZERO
    tax = _ZERO
    prev_limit = _ZERO
    for bracket in rules.irpef_brackets:
        if bracket.up_to is not None:
            bracket_top = bracket.up_to
            if taxable_income <= prev_limit:
                break
            taxable_in_bracket = min(taxable_income, bracket_top) - prev_limit
            tax += taxable_in_bracket * bracket.rate
            prev_limit = bracket_top
        elif taxable_income > prev_limit:
            tax += (taxable_income - prev_limit) * bracket.rate
    return money(tax)


def work_income_deduction(gross_income: Decimal, rules: YearRules) -> Decimal:
    """Compute the Art. 13 TUIR work-income deduction via piecewise interpolation."""
    if gross_income <= _ZERO:
        return _ZERO
    points = rules.work_deduction_breakpoints
    first = points[0]
    if first.income_up_to is not None and gross_income <= first.income_up_to:
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
        if lo_income < gross_income <= hi_income:
            return _interpolate_deduction(
                gross_income, lo_income, hi_income, lo.deduction, hi.deduction
            )
    return money(points[-1].deduction)


def _interpolate_deduction(
    gross_income: Decimal,
    lo_income: Decimal,
    hi_income: Decimal,
    lo_ded: Decimal,
    hi_ded: Decimal,
) -> Decimal:
    fraction = (gross_income - lo_income) / (hi_income - lo_income)
    return money(lo_ded + fraction * (hi_ded - lo_ded))
