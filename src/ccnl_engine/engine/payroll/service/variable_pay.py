"""Variable-pay computation service (fringe benefits, welfare, PdR bonus).

All outputs are *informational*: ``gross_annual``, ``taxable_income``,
``net_annual``, and ``irpef_net`` are never mutated.

Fringe benefits (Art. 51 c. 3 TUIR):
    Amounts up to the statutory threshold are fully exempt.  The excess
    is reported as ``fringe_benefit_taxable_annual``; its IRPEF impact is
    not computed here (would require extending the L2 fiscal chain).

Welfare (Art. 51 c. 2 TUIR):
    Welfare contributions are unconditionally exempt from IRPEF and
    social contributions when structured under Art. 51 c. 2.  The engine
    echoes the amount without verifying platform eligibility.

Premio di risultato / Bonus (L. 208/2015 art. 1 cc. 182-190):
    If the bonus is PdR-eligible and the worker's gross employment income
    does not exceed the statutory ceiling, a flat substitutive tax applies
    up to the statutory maximum.  The remaining amount is reported as
    ordinarily taxable; its IRPEF impact is not recomputed.
    When the income ceiling is exceeded a warning is appended and the
    full bonus is reported as ordinarily taxable.
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
    taxable = money(max(_ZERO, fb_input.annual_amount - threshold))
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
    gross_annual: Decimal,
    l3_warnings: list[str],
) -> tuple[Decimal, Decimal, Decimal]:
    """Compute PdR flat tax and ordinarily taxable bonus amount.

    When the bonus is not PdR-eligible, the entire amount is reported as
    ordinarily taxable.  When PdR-eligible but the worker's gross annual
    income exceeds the statutory ceiling, the PdR regime does not apply
    and a warning is appended.

    Args:
        bonus_input: Caller-declared annual bonus and PdR eligibility flag.
        pdr_rules: Statutory PdR parameters for the fiscal year.
        gross_annual: Worker's gross annual employment income, used to
            check the income ceiling for PdR eligibility.
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

    if gross_annual > pdr_rules.income_ceiling:
        l3_warnings.append(
            "bonus_input: PdR regime not applicable — gross_annual "
            f"{gross_annual} exceeds income ceiling {pdr_rules.income_ceiling}"
        )
        return amount, _ZERO, amount

    pdr_base = min(amount, pdr_rules.max_amount)
    flat_tax = money(pdr_base * pdr_rules.flat_tax_rate)
    ordinary = money(max(_ZERO, amount - pdr_rules.max_amount))
    return amount, flat_tax, ordinary
