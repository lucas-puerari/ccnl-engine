"""IRPEF (personal income tax) calculation.

.. note::
    **SIMPLIFICATION**: These functions compute IRPEF on annual taxable income
    using only the statutory brackets (Art. 11 TUIR) and the Art. 13 TUIR
    work-income deduction. The following are *not* modelled:

    * Addizionali regionali and addizionali comunali.
    * Detrazioni per carichi di famiglia (Art. 12 TUIR).
    * The EUR 65 additional deduction for redditi 25,000-35,000
      (Art. 13 co. 1-bis TUIR, added by D.Lgs. 216/2023).
    * The sterilization mechanism for redditi > 200,000 EUR
      (Art. 1 co. 3-4 L. 199/2025).
    * Bonus / trattamento integrativo (Art. 1 D.L. 3/2020).

All returned values are rounded to the nearest cent via
:func:`~ccnl_engine.engine.rounding.money`.
"""

from decimal import Decimal

from ccnl_engine.engine.rounding import money
from ccnl_engine.tax.models import YearRules

_ZERO = Decimal(0)


def irpef_gross(taxable_income: Decimal, rules: YearRules) -> Decimal:
    """Compute gross IRPEF on *taxable_income* using marginal brackets.

    Iterates :attr:`~ccnl_engine.tax.models.YearRules.irpef_brackets` in
    order, applying each marginal rate to the portion of income that falls
    within that bracket.

    Args:
        taxable_income: Annual taxable income (reddito imponibile) in euros.
            Negative values are treated as zero.
        rules: Tax year rules providing the IRPEF brackets.

    Returns:
        Gross IRPEF before deductions, rounded to the nearest cent.
    """
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
        # Last (unbounded) bracket
        elif taxable_income > prev_limit:
            tax += (taxable_income - prev_limit) * bracket.rate
    return money(tax)


def work_income_deduction(gross_income: Decimal, rules: YearRules) -> Decimal:
    """Compute the Art. 13 TUIR work-income deduction via piecewise interpolation.

    The deduction schedule stored in
    :attr:`~ccnl_engine.tax.models.YearRules.work_deduction_breakpoints`
    represents the deduction at the *upper bound* of each income segment.
    The engine interpolates linearly between consecutive breakpoints.

    Rules:
    * For income at or below the first breakpoint's ``income_up_to``, the
      first breakpoint's ``deduction`` is returned (flat segment).
    * Between two consecutive breakpoints the deduction is interpolated
      linearly.
    * Above the last finite breakpoint the deduction is zero.

    Args:
        gross_income: Gross annual income (reddito complessivo) in euros.
            Non-positive values yield a deduction of zero.
        rules: Tax year rules providing the deduction breakpoints.

    Returns:
        Art. 13 TUIR deduction, rounded to the nearest cent.
    """
    if gross_income <= _ZERO:
        return _ZERO
    points = rules.work_deduction_breakpoints
    # Income below or at the first breakpoint: return the flat deduction
    first = points[0]
    if first.income_up_to is not None and gross_income <= first.income_up_to:
        return money(first.deduction)
    # Walk through consecutive pairs to find the enclosing segment
    for i in range(len(points) - 1):
        lo = points[i]
        hi = points[i + 1]
        lo_income = lo.income_up_to
        hi_income = hi.income_up_to
        if lo_income is None:
            # lo is the last (open) breakpoint — should not happen in a valid series
            break  # pragma: no cover
        if hi_income is None:
            # hi is the open-ended sentinel: income > last finite breakpoint
            return money(hi.deduction)
        if lo_income < gross_income <= hi_income:
            # Linear interpolation
            fraction = (gross_income - lo_income) / (hi_income - lo_income)
            deduction = lo.deduction + fraction * (hi.deduction - lo.deduction)
            return money(deduction)
    # Income above all finite breakpoints: last entry's deduction (typically 0)
    return money(points[-1].deduction)
