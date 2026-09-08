"""Art. 15 TUIR oneri detraibili computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
    from ccnl_engine.engine.tax.domain.art15 import Art15DeductionRules


def compute_art15_deductions(
    deductions: Art15Deductions,
    rules: Art15DeductionRules,
) -> Decimal:
    """Compute Art. 15 TUIR detrazioni dall'imposta lorda (tax credits).

    Applies a flat rate on eligible expenditure up to the statutory ceiling
    for each modelled category.  Returns the total annual tax credit, not
    the deductible base.

    Art. 1 c. 3-4 L. 199/2025 sterilizzazione does NOT apply: the EUR 440
    clawback is specific to Art. 12 + Art. 13 TUIR (bracket rate change
    compensation) and does not extend to Art. 15 oneri.

    Args:
        deductions: Caller-supplied Art. 15 expenditure amounts.
        rules: Statutory parameters for the fiscal year.

    Returns:
        Total annual tax credit (EUR, rounded to 2 decimal places).
    """
    eligible = money(min(deductions.mortgage_interest, rules.mortgage_interest.ceiling))
    return money(eligible * rules.mortgage_interest.rate)
