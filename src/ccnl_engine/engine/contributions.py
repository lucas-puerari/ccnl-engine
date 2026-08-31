"""Social security and TFR contribution calculations.

SIMPLIFICATION: uniform rate over gross annual pay; IVS ceiling split
(Art. 1 L. 335/1995) not modelled.
"""

from decimal import Decimal

from ccnl_engine.engine.rounding import money
from ccnl_engine.tax.models import YearRules


def inps_employee(gross_annual: Decimal, rules: YearRules) -> Decimal:
    """Compute the employee-side INPS contribution."""
    base = (
        min(gross_annual, rules.inps.ceiling)
        if rules.inps.ceiling is not None
        else gross_annual
    )
    return money(base * rules.inps.employee_rate)


def inps_employer(
    gross_annual: Decimal, rules: YearRules, *, fixed_term: bool = False
) -> Decimal:
    """Compute the employer-side INPS contribution, including NASpI addizionale."""
    # SIMPLIFICATION: +0.50% increment per renewal not modelled; only base rate applies.
    base = (
        min(gross_annual, rules.inps.ceiling)
        if rules.inps.ceiling is not None
        else gross_annual
    )
    rate = rules.inps.employer_rate
    if fixed_term:
        rate = rate + rules.fixed_term_additional_rate
    return money(base * rate)


def tfr(gross_annual: Decimal, rules: YearRules) -> Decimal:
    """Compute the annual TFR accrual (Art. 2120 c.c.)."""
    return money(gross_annual / rules.tfr.accrual_divisor)
