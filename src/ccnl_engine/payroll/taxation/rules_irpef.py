"""Gross IRPEF and IRPEF surtaxes on marginal brackets.

Implements the Art. 11 TUIR brackets and the addizionale regionale e
comunale IRPEF (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998), which share the
marginal bracket structure.

The deductions from gross IRPEF live in
:mod:`~ccnl_engine.payroll.taxation.rules_irpef_deduction` (Art. 13 TUIR and the
sterilizzazione of L. 199/2025) and
:mod:`~ccnl_engine.payroll.family.services` (Art. 12 TUIR); the
credits (trattamento integrativo, ulteriore detrazione, somma esente) in
:mod:`~ccnl_engine.payroll.taxation.rules_irpef_credit`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ccnl_engine.primitives import Bracket
    from ccnl_engine.tax.annual.models import YearRules

_ZERO = Decimal(0)
DAYS_IN_YEAR = 365  # "365 per l'intero anno": 730/2026 istruzioni, quadro C
#: Monthly pay periods in a year, the divisor of the annual brackets.
MONTHS_IN_YEAR = 12


def _marginal_tax(taxable_income: Decimal, brackets: Sequence[Bracket]) -> Decimal:
    """Apply each bracket's rate to the slice of income inside it.

    Returns:
        The tax on ``taxable_income``, rounded to two decimal places.
    """
    return money(_exact_marginal_tax(taxable_income, brackets))


def _exact_marginal_tax(
    taxable_income: Decimal, brackets: Sequence[Bracket]
) -> Decimal:
    """Apply each bracket's rate to the slice of income inside it.

    Returns:
        The tax on ``taxable_income``, not rounded.
    """
    tax = _ZERO
    prev_limit = _ZERO
    for bracket in brackets:
        if bracket.up_to is not None:
            bracket_top = bracket.up_to
            # Equivalent as `<`: at equality the bracket adds 0 and the next breaks.
            if taxable_income <= prev_limit:  # pragma: no mutate
                break
            taxable_in_bracket = min(taxable_income, bracket_top) - prev_limit
            tax += taxable_in_bracket * bracket.rate
            prev_limit = bracket_top
        # Equivalent as `>=`: at equality the open bracket adds 0 * rate.
        elif taxable_income > prev_limit:  # pragma: no mutate
            tax += (taxable_income - prev_limit) * bracket.rate
    return tax


def irpef_gross(taxable_income: Decimal, rules: YearRules) -> Decimal:
    """Compute gross IRPEF on taxable_income using marginal brackets.

    Returns:
        The gross IRPEF amount, rounded to two decimal places.
    """
    # Equivalent as `<`: at zero income _marginal_tax also returns zero.
    if taxable_income <= _ZERO:  # pragma: no mutate
        return _ZERO
    return _marginal_tax(taxable_income, rules.irpef_brackets)


def period_irpef_gross(
    taxable: Decimal, rules: YearRules, periods: int = MONTHS_IN_YEAR
) -> Decimal:
    """Return the IRPEF on the taxable of a pay period, before any deduction.

    Art. 23 c. 2 DPR 600/1973 withholds on the pay of a period "con le
    aliquote dell'imposta sul reddito delle persone fisiche, ragguagliando
    al periodo di paga i corrispondenti scaglioni annui di reddito" (lett.
    a), and on the mensilità aggiuntive "ragguagliando a mese" the same
    brackets (lett. b).  Dividing every bracket limit by ``periods`` taxes
    ``taxable`` as the annual brackets tax ``taxable * periods``, divided
    by ``periods``: the limits are not rounded.

    Args:
        taxable: Taxable income of the pay period.
        rules: Year rules with the annual brackets.
        periods: Pay periods in a year, twelve for a monthly pay.

    Returns:
        The tax, rounded to two decimal places; zero at or below zero.
    """
    if taxable <= _ZERO:
        return _ZERO
    return money(_exact_marginal_tax(taxable * periods, rules.irpef_brackets) / periods)


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
            :class:`~ccnl_engine.tax.surtax.models_table.SurtaxBracket`
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
