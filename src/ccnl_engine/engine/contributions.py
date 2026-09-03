"""Social security and TFR contribution calculations.

SIMPLIFICATION: uniform rate over the contribution base; IVS ceiling split
(Art. 1 L. 335/1995) not modelled.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.engine.rounding import money
from ccnl_engine.models.employment import Apprentice, FixedTerm

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.models.employment import Employment
    from ccnl_engine.tax.models import YearRules


@dataclass(frozen=True)
class ContributionRates:
    """Employee and employer INPS rates resolved for one scenario."""

    employee_rate: Decimal
    employer_rate: Decimal


def resolve_rates(
    rules: YearRules, employment: Employment, category: str | None
) -> ContributionRates:
    """Resolve INPS rates for an employment type and worker category.

    Apprentices use the statutory reduced rates (L. 296/2006 art. 1 c. 773,
    headcount already resolved in ``rules.apprentice``). Fixed-term contracts
    add the NASpI *addizionale* to the employer rate (Art. 2 c. 28 L. 92/2012).

    Returns:
        ContributionRates with employee and employer rates for the scenario.
    """
    if isinstance(employment, Apprentice):
        return ContributionRates(
            employee_rate=rules.apprentice.employee_rate,
            employer_rate=rules.apprentice.employer_rate_at(employment.months_elapsed),
        )
    employer_rate = rules.inps.employer_rate_for(category)
    if isinstance(employment, FixedTerm):
        employer_rate += rules.fixed_term_additional_rate
    return ContributionRates(
        employee_rate=rules.inps.employee_rate, employer_rate=employer_rate
    )


def inps_contribution(base_annual: Decimal, rate: Decimal, rules: YearRules) -> Decimal:
    """Compute an INPS contribution on the (ceiling-capped) annual base.

    Returns:
        The annual INPS contribution amount, rounded to two decimal places.
    """
    capped = (
        min(base_annual, rules.inps.ceiling)
        if rules.inps.ceiling is not None
        else base_annual
    )
    return money(capped * rate)


def tfr(base_annual: Decimal, rules: YearRules) -> Decimal:
    """Compute the annual TFR accrual (Art. 2120 c.c.).

    Returns:
        The annual TFR accrual amount, rounded to two decimal places.
    """
    return money(base_annual / rules.tfr.accrual_divisor)
