"""Gross IRPEF and IRPEF surtaxes on marginal brackets.

Implements the Art. 11 TUIR brackets and the addizionale regionale e
comunale IRPEF (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998), which share the
marginal bracket structure.

The deductions from gross IRPEF live in
:mod:`~ccnl_engine.payroll.service.irpef_deductions` (Art. 13 TUIR and the
sterilizzazione of L. 199/2025) and
:mod:`~ccnl_engine.payroll.service.family_deductions` (Art. 12 TUIR); the
credits (trattamento integrativo, ulteriore detrazione, somma esente) in
:mod:`~ccnl_engine.payroll.service.irpef_credits`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.shared.domain.primitives import Bracket
    from ccnl_engine.tax.domain.ruleset import YearRules

_ZERO = Decimal(0)
DAYS_IN_YEAR = 365  # "365 per l'intero anno": 730/2026 istruzioni, quadro C


def _marginal_tax(taxable_income: Decimal, brackets: Sequence[Bracket]) -> Decimal:
    """Apply each bracket's rate to the slice of income inside it.

    Returns:
        The tax on ``taxable_income``, rounded to two decimal places.
    """
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


def irpef_gross(taxable_income: Decimal, rules: YearRules) -> Decimal:
    """Compute gross IRPEF on taxable_income using marginal brackets.

    Returns:
        The gross IRPEF amount, rounded to two decimal places.
    """
    if taxable_income <= _ZERO:
        return _ZERO
    return _marginal_tax(taxable_income, rules.irpef_brackets)


def surtax_from_brackets(
    taxable_income: Decimal,
    brackets: Sequence[Bracket],
    exemption_threshold: Decimal = _ZERO,
) -> Decimal:
    """Compute addizionale IRPEF (regionale or comunale) via marginal brackets.

    The bracket structure mirrors IRPEF (Art. 11 TUIR): each bracket's rate
    applies only to income within that slice.  Regions and municipalities that
    set a single flat rate are represented as a single bracket with
    ``up_to=None``.

    Args:
        taxable_income: IRPEF taxable base (gross annual minus employee INPS).
        brackets: Ordered sequence of
            :class:`~ccnl_engine.tax.domain.surtax_rules.SurtaxBracket`
            entries; the last entry must have ``up_to=None``.
        exemption_threshold: Full-exemption threshold: if
            ``taxable_income <= exemption_threshold`` the surtax is zero.
            Defaults to zero (no exemption).

    Returns:
        Annual surtax amount, rounded to two decimal places.
    """
    if taxable_income <= exemption_threshold or taxable_income <= _ZERO:
        return _ZERO
    return _marginal_tax(taxable_income, brackets)
