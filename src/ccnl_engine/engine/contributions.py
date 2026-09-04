"""Social security and TFR contribution calculations.

IVS ceiling split: when ``ivs_ceiling_applies`` is True and the tax file
carries a non-null ``ceiling``, only the IVS portion of each INPS rate is
capped at the massimale retributivo (Art. 1 c. 18 L. 335/1995); the
remainder (NASpI, CUAF, CIG, etc.) is applied to the full base.
``ivs_ceiling_applies`` must be set explicitly by the caller: it is True only
for workers whose first INPS enrollment falls on or after 1 Jan 1996
(Art. 1 c. 18 L. 335/1995).  Defaulting it to False preserves the previous
behaviour (no capping) for all existing callers.
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
    employee_ivs_rate: Decimal
    employer_rate: Decimal
    employer_ivs_rate: Decimal


def resolve_rates(
    rules: YearRules, employment: Employment, category: str | None
) -> ContributionRates:
    """Resolve INPS rates for an employment type and worker category.

    Apprentices use the statutory reduced rates (L. 296/2006 art. 1 c. 773,
    headcount already resolved in ``rules.apprentice``).  The NASpI
    *addizionale* (Art. 2 c. 28 L. 92/2012) is **not** applied to apprentices:
    apprendistato is explicitly exempt under Art. 2 c. 29 of the same law, so
    the ``Apprentice`` branch returns before the ``FixedTerm`` check — this is
    intentional, not an oversight.  Fixed-term non-apprentice contracts add the
    addizionale to the employer rate only; the IVS rate is unchanged because
    the addizionale is a non-IVS component (NASpI fund).

    Returns:
        ContributionRates with employee and employer rates for the scenario.
    """
    if isinstance(employment, Apprentice):
        emp_rate = rules.apprentice.employee_rate
        er_rate = rules.apprentice.employer_rate_at(employment.months_elapsed)
        return ContributionRates(
            employee_rate=emp_rate,
            employee_ivs_rate=rules.apprentice.employee_ivs_rate,
            employer_rate=er_rate,
            employer_ivs_rate=rules.apprentice.employer_ivs_rate_at(
                employment.months_elapsed
            ),
        )
    employer_rate = rules.inps.employer_rate_for(category)
    # NASpI addizionale is not IVS; keep ivs_rate unchanged.
    employer_ivs_rate = rules.inps.employer_ivs_rate
    if isinstance(employment, FixedTerm):
        employer_rate += rules.fixed_term_additional_rate
    return ContributionRates(
        employee_rate=rules.inps.employee_rate,
        employee_ivs_rate=rules.inps.employee_ivs_rate,
        employer_rate=employer_rate,
        employer_ivs_rate=employer_ivs_rate,
    )


def inps_contribution(
    base_annual: Decimal,
    total_rate: Decimal,
    ivs_rate: Decimal,
    rules: YearRules,
    *,
    ivs_ceiling_applies: bool,
) -> Decimal:
    """Compute an INPS contribution, applying the IVS ceiling only to the IVS portion.

    When ``ivs_ceiling_applies`` is True and ``rules.inps.ceiling`` is set,
    the IVS portion (``ivs_rate``) is capped at the massimale retributivo
    while the non-IVS remainder (NASpI, CUAF, CIG, etc.) is applied to the
    full ``base_annual``.  When False, or when no ceiling is configured, a
    flat rate is applied to the full base (preserving the previous behaviour).

    Returns:
        The annual INPS contribution amount, rounded to two decimal places.
    """
    ceiling = rules.inps.ceiling
    if ivs_ceiling_applies and ceiling is not None:
        ivs_base = min(base_annual, ceiling)
        non_ivs_rate = total_rate - ivs_rate
        return money(ivs_base * ivs_rate + base_annual * non_ivs_rate)
    return money(base_annual * total_rate)


def tfr(base_annual: Decimal, rules: YearRules) -> Decimal:
    """Compute the annual TFR accrual (Art. 2120 c.c.).

    Returns:
        The annual TFR accrual amount, rounded to two decimal places.
    """
    return money(base_annual / rules.tfr.accrual_divisor)
