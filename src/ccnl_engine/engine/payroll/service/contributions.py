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

from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.contract.domain.ccnl import EmployerFund, LevelCategory
    from ccnl_engine.engine.payroll.domain.employment import Employment
    from ccnl_engine.engine.tax.domain.rules import (
        ApprenticeRates,
        DomesticInpsRates,
        InpsRates,
        YearRules,
    )

_APPRENTICE_STEP_1: int = 12
_APPRENTICE_STEP_2: int = 24


@dataclass(frozen=True)
class ContributionRates:
    """Employee and employer INPS rates resolved for one scenario."""

    employee_rate: Decimal
    employee_ivs_rate: Decimal
    employer_rate: Decimal
    employer_ivs_rate: Decimal


def resolve_rates(
    rules: YearRules, employment: Employment, category: LevelCategory | None
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

    Raises:
        TypeError: If ``rules.inps`` or ``rules.apprentice`` is None (domestic
            model sectors must take the flat-hour path in compute() instead).
    """
    if rules.inps is None or rules.apprentice is None:
        msg = (
            "resolve_rates requires standard INPS rates; "
            "domestic sectors must use the flat-hour path in compute()"
        )
        raise TypeError(msg)
    if isinstance(employment, Apprentice):
        emp_rate = rules.apprentice.employee_rate
        er_rate = apprentice_employer_rate(rules.apprentice, employment.months_elapsed)
        return ContributionRates(
            employee_rate=emp_rate,
            employee_ivs_rate=rules.apprentice.employee_ivs_rate,
            employer_rate=er_rate,
            employer_ivs_rate=apprentice_employer_ivs_rate(
                rules.apprentice, employment.months_elapsed
            ),
        )
    employer_rate = inps_employer_rate(rules.inps, category)
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
    ceiling = rules.inps.ceiling if rules.inps is not None else None
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


def inps_employer_rate(rates: InpsRates, category: str | None) -> Decimal:
    """Return the employer rate applicable to a worker category.

    Returns:
        The employer contribution rate for the given worker category.
    """
    if category is None:
        return rates.employer_rate
    return rates.employer_rate_by_category.get(category, rates.employer_rate)


def apprentice_employer_rate(rates: ApprenticeRates, months_elapsed: int) -> Decimal:
    """Return the employer rate in force at ``months_elapsed``.

    Returns:
        The employer contribution rate applicable at the given month.
    """
    if months_elapsed < _APPRENTICE_STEP_1:
        return rates.employer_rate_months_0_11
    if months_elapsed < _APPRENTICE_STEP_2:
        return rates.employer_rate_months_12_23
    return rates.employer_rate_after


def apprentice_employer_ivs_rate(
    rates: ApprenticeRates, months_elapsed: int
) -> Decimal:
    """Return the IVS-only employer rate in force at ``months_elapsed``.

    Returns:
        The IVS portion of the employer rate applicable at the given month.
    """
    if months_elapsed < _APPRENTICE_STEP_1:
        return rates.employer_ivs_rate_months_0_11
    if months_elapsed < _APPRENTICE_STEP_2:
        return rates.employer_ivs_rate_months_12_23
    return rates.employer_ivs_rate_after


def resolve_domestic_inps_rate(
    rates: DomesticInpsRates,
    hourly_rate: Decimal,
    weekly_hours: Decimal,
    *,
    is_fixed_term: bool,
) -> tuple[Decimal, Decimal]:
    """Return ``(employee_per_hour, employer_per_hour)`` for the scenario.

    Returns:
        A tuple of (employee contribution per hour, employer contribution
        per hour) based on weekly_hours and hourly_rate.

    Raises:
        ValueError: If no wage bracket covers the given hourly_rate.
    """
    if weekly_hours > rates.weekly_hours_threshold:
        b = rates.hours_bracket
        er = b.employer_per_hour_fixed_term if is_fixed_term else b.employer_per_hour
        return b.employee_per_hour, er
    for bracket in rates.wage_brackets:
        if (
            bracket.hourly_rate_up_to is None
            or hourly_rate <= bracket.hourly_rate_up_to
        ):
            er = (
                bracket.employer_per_hour_fixed_term
                if is_fixed_term
                else bracket.employer_per_hour
            )
            return bracket.employee_per_hour, er
    msg = f"no wage bracket covers hourly_rate={hourly_rate!r}"
    raise ValueError(msg)


def fund_applies_to(fund: EmployerFund, category: LevelCategory | None) -> bool:
    """Return whether the fund applies to a level of the given category.

    Returns:
        True if the fund applies to the given category, False otherwise.
    """
    if fund.applies_to_categories is None:
        return True
    return category is not None and category in fund.applies_to_categories
