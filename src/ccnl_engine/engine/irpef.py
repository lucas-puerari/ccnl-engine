"""IRPEF (personal income tax) calculation.

Implements Art. 11 TUIR brackets and the Art. 13 co. 1 TUIR work-income
deduction (piecewise-linear schedule as modified by D.Lgs. 216/2023 and
confirmed by L. 207/2024), the trattamento integrativo (Art. 1 D.L.
3/2020 as updated by L. 207/2024), and the addizionale regionale e comunale
IRPEF (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998).

Not in scope for this engine (handled by a separate fiscal library):
detrazioni per carichi di famiglia (Art. 12 TUIR); sterilization of detrazioni
for redditi > EUR 200k (Art. 1 c. 3-4 L. 199/2025).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.surtax.models import SurtaxBracket
    from ccnl_engine.tax.models import TrattamentoIntegrativoRules, YearRules

_ZERO = Decimal(0)


def irpef_gross(taxable_income: Decimal, rules: YearRules) -> Decimal:
    """Compute gross IRPEF on taxable_income using marginal brackets.

    Returns:
        The gross IRPEF amount, rounded to two decimal places.
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
        elif taxable_income > prev_limit:
            tax += (taxable_income - prev_limit) * bracket.rate
    return money(tax)


def work_income_deduction(gross_income: Decimal, rules: YearRules) -> Decimal:
    """Compute the Art. 13 TUIR work-income deduction via piecewise interpolation.

    Returns:
        The applicable deduction amount, rounded to two decimal places.
    """
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


def trattamento_integrativo(
    gross_annual: Decimal,
    irpef_lorda: Decimal,
    detrazioni_lavoro: Decimal,
    rules: TrattamentoIntegrativoRules,
) -> Decimal:
    """Compute the trattamento integrativo bonus (Art. 1 D.L. 3/2020).

    Args:
        gross_annual: Annual gross pay (RAL) used to determine the bonus tier.
        irpef_lorda: Gross IRPEF before work-income deduction (Art. 11 TUIR).
        detrazioni_lavoro: Work-income deduction (Art. 13 TUIR).
        rules: Threshold and amount parameters from the tax data file.

    Returns:
        The trattamento integrativo amount, rounded to two decimal places.
        Zero when RAL exceeds ``rules.threshold_upper`` or when the bonus
        condition is not met.
    """
    if gross_annual > rules.threshold_upper:
        return _ZERO
    if gross_annual <= rules.threshold_mid:
        return money(rules.max_amount) if irpef_lorda > detrazioni_lavoro else _ZERO
    span = rules.threshold_upper - rules.threshold_mid
    scaled = rules.max_amount * (rules.threshold_upper - gross_annual) / span
    return money(max(_ZERO, scaled))


def surtax_from_brackets(
    taxable_income: Decimal,
    brackets: list[SurtaxBracket],
    soglia: Decimal = _ZERO,
) -> Decimal:
    """Compute addizionale IRPEF (regionale or comunale) via marginal brackets.

    The bracket structure mirrors IRPEF (Art. 11 TUIR): each bracket's rate
    applies only to income within that slice.  Regions and municipalities that
    set a single flat rate are represented as a single bracket with
    ``up_to=None``.

    Args:
        taxable_income: IRPEF taxable base (gross annual minus employee INPS).
        brackets: Ascending list of :class:`~ccnl_engine.surtax.models.SurtaxBracket`
            entries; the last entry must have ``up_to=None``.
        soglia: Full-exemption threshold (soglia di esenzione): if
            ``taxable_income <= soglia`` the surtax is zero.  Defaults to zero
            (no exemption).

    Returns:
        Annual surtax amount, rounded to two decimal places.
    """
    if taxable_income <= soglia or taxable_income <= _ZERO:
        return _ZERO
    tax = _ZERO
    prev_limit = _ZERO
    for bracket in brackets:
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


def _interpolate_deduction(
    gross_income: Decimal,
    lo_income: Decimal,
    hi_income: Decimal,
    lo_ded: Decimal,
    hi_ded: Decimal,
) -> Decimal:
    fraction = (gross_income - lo_income) / (hi_income - lo_income)
    return money(lo_ded + fraction * (hi_ded - lo_ded))
