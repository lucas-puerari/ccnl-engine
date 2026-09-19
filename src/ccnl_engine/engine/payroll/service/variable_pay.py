"""Variable-pay computation service (fringe benefits, welfare, PdR bonus).

Fringe benefits (Art. 51 c. 3 TUIR):
    Amounts up to the statutory threshold are fully exempt.  The excess
    (``fringe_benefit_taxable_annual``) is added to the IRPEF taxable base
    by the fiscal service.

Welfare (Art. 51 c. 2 TUIR):
    Welfare contributions are unconditionally exempt from IRPEF and
    social contributions when structured under Art. 51 c. 2.  The engine
    echoes the amount without verifying platform eligibility.

Premio di risultato / Bonus (L. 208/2015 art. 1 cc. 182-190):
    If the bonus is PdR-eligible, ``prior_year_gross_annual`` must be
    supplied; without it the PdR regime cannot be verified and the full
    amount is treated as ordinarily taxable (``not_computed`` scope item).
    When eligibility is confirmed, a flat substitutive tax applies up to
    the statutory maximum; the excess is ordinarily taxable and enters the
    IRPEF base.  When the prior-year income ceiling is exceeded a warning
    is appended and the full bonus is ordinarily taxable.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.supplements import (
        BonusInput,
        FringeBenefitInput,
        WelfareInput,
    )
    from ccnl_engine.engine.tax.domain.variable_pay import (
        FringeBenefitRules,
        PdRRules,
    )

_ZERO = Decimal(0)


def compute_fringe_benefit(
    fb_input: FringeBenefitInput,
    fb_rules: FringeBenefitRules,
) -> tuple[Decimal, Decimal, Decimal]:
    """Compute fringe-benefit exemption and taxable excess.

    Args:
        fb_input: Caller-declared annual fringe benefit amount and
            dependent-children flag.
        fb_rules: Statutory exemption thresholds for the fiscal year.

    Returns:
        A 3-tuple of:
        - ``annual_amount``: echo of input.
        - ``threshold``: applicable statutory threshold.
        - ``taxable_annual``: amount above the threshold (floored at zero).
    """
    threshold = (
        fb_rules.threshold_with_children
        if fb_input.has_dependent_children
        else fb_rules.threshold_standard
    )
    # R15: once the threshold is breached the *entire* amount is taxable,
    # not just the excess (Art. 51 c. 3 TUIR — all-or-nothing rule).
    taxable = fb_input.annual_amount if fb_input.annual_amount > threshold else _ZERO
    return fb_input.annual_amount, threshold, taxable


def compute_welfare(welfare_input: WelfareInput) -> Decimal:
    """Return the welfare annual amount (always tax-exempt under Art. 51 c. 2).

    Args:
        welfare_input: Caller-declared annual welfare amount.

    Returns:
        The welfare amount (echo of input).
    """
    return welfare_input.annual_amount


def compute_bonus(
    bonus_input: BonusInput,
    pdr_rules: PdRRules,
    l3_warnings: list[str],
) -> tuple[Decimal, Decimal, Decimal]:
    """Compute PdR flat tax and ordinarily taxable bonus amount.

    When the bonus is not PdR-eligible, the entire amount is ordinarily
    taxable.  When PdR-eligible, ``prior_year_gross_annual`` must be
    supplied; without it the PdR regime cannot be verified and the full
    amount is treated as ordinarily taxable (caller should set
    ``bonus_pdr_missing_prior_year`` and emit a ``not_computed`` scope
    item).  When the prior-year income ceiling is exceeded a warning is
    appended and the full bonus is ordinarily taxable.

    Args:
        bonus_input: Caller-declared annual bonus and PdR eligibility flag.
        pdr_rules: Statutory PdR parameters for the fiscal year.
        l3_warnings: Mutable list; a warning is appended when the income
            ceiling disqualifies PdR treatment.

    Returns:
        A 3-tuple of:
        - ``bonus_annual``: echo of input.
        - ``pdr_flat_tax_annual``: imposta sostitutiva (0 if not eligible).
        - ``ordinary_taxable_annual``: portion taxed at ordinary IRPEF rate.
    """
    amount = bonus_input.annual_amount
    if amount <= _ZERO:
        return _ZERO, _ZERO, _ZERO

    if not bonus_input.eligible_for_pdr:
        return amount, _ZERO, amount

    # R16: prior_year_gross_annual is required for PdR ceiling check.
    # When absent the caller treats the bonus as not_computed and passes
    # all-ordinary; this branch handles the "prior year provided" path only.
    if bonus_input.prior_year_gross_annual is None:
        return amount, _ZERO, amount

    ceiling_income = bonus_input.prior_year_gross_annual
    if ceiling_income > pdr_rules.income_ceiling:
        l3_warnings.append(
            "bonus_input: PdR regime not applicable — income "
            f"{ceiling_income} exceeds ceiling {pdr_rules.income_ceiling}"
        )
        return amount, _ZERO, amount

    pdr_base = min(amount, pdr_rules.max_amount)
    flat_tax = money(pdr_base * pdr_rules.flat_tax_rate)
    ordinary = money(max(_ZERO, amount - pdr_rules.max_amount))
    return amount, flat_tax, ordinary
