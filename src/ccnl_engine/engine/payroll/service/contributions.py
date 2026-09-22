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
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
    ContributionComponent,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import EmployerFund, LevelCategory
    from ccnl_engine.engine.payroll.domain.employment import Contract as Employment
    from ccnl_engine.engine.payroll.domain.employment import Permanent
    from ccnl_engine.engine.tax.domain.rules import (
        ApprenticeRates,
        DomesticInpsRates,
        InpsRates,
        YearRules,
    )

_ZERO = Decimal(0)

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


def inps_employee_additional(
    base_annual: Decimal,
    rates: InpsRates | None,
    *,
    ivs_ceiling_applies: bool,
) -> Decimal:
    """Compute the 1% employee additional IVS contribution (Art. 3-ter D.L. 384/1992).

    Applies to the portion of annual earnings exceeding the first pensionable
    band threshold. The additional is IVS and is therefore subject to the
    massimale retributivo when ivs_ceiling_applies is True.

    Returns zero when ``rates`` is None, or when the additional rate or
    threshold is not configured for this sector.

    Returns:
        Additional employee INPS contribution, rounded to two decimal places.
    """
    if rates is None:
        return _ZERO
    add_rate = rates.employee_additional_rate
    add_threshold = rates.employee_additional_threshold
    if add_rate is None:
        # InpsRates._check_rates guarantees the pair is either both set or both
        # absent, so checking add_rate is sufficient.
        return _ZERO
    # Invariant: add_threshold is set whenever add_rate is set.
    assert add_threshold is not None
    capped = (
        min(base_annual, rates.ceiling)
        if ivs_ceiling_applies and rates.ceiling is not None
        else base_annual
    )
    excess = max(_ZERO, capped - add_threshold)
    return money(excess * add_rate)


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
        AssertionError: Structurally unreachable; the ``DomesticInpsRates``
            invariant guarantees an open-ended last bracket.
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
    # Unreachable: DomesticInpsRates invariant guarantees an open-ended
    # last bracket (hourly_rate_up_to=None) that covers every hourly_rate.
    raise AssertionError  # pragma: no cover


def fund_applies_to(fund: EmployerFund, category: LevelCategory | None) -> bool:
    """Return whether the fund applies to a level of the given category.

    Returns:
        True if the fund applies to the given category, False otherwise.
    """
    if fund.applies_to_categories is None:
        return True
    return category is not None and category in fund.applies_to_categories


def resolve_contributions(
    period_inps_base: Decimal,
    rules: YearRules,
    contract_type: Permanent | FixedTerm | Apprentice,
    category: LevelCategory | None,
    *,
    ytd_inps_base: Decimal = _ZERO,
) -> ContributionBreakdown:
    """Compute INPS contributions with per-component breakdown and IVS ceiling.

    The IVS portion of both employee and employer contributions is capped at
    the massimale retributivo (Art. 1 c. 18 L. 335/1995) when a ceiling is
    configured.  The ceiling is enforced across the year via ``ytd_inps_base``:
    only the portion of ``period_inps_base`` that fits within the remaining
    headroom (``ceiling - ytd_inps_base``) attracts IVS contributions; the
    non-IVS components (NASpI, CUAF, CIG) are applied to the full base.

    Args:
        period_inps_base: Gross INPS-liable base for this period.
        rules: Year-specific tax and contribution rules.
        contract_type: Employment type (Permanent, FixedTerm, Apprentice).
        category: Level category for employer rate lookup, or None.
        ytd_inps_base: Total INPS base already accumulated this tax year
            (from ``PeriodState.inps_base_ytd``). Used to enforce the
            annual IVS ceiling across periods.

    Returns:
        :class:`~ccnl_engine.payroll.domain.contributions.ContributionBreakdown`
        with employee/employer totals and per-component trace.
    """
    rates = resolve_rates(rules, contract_type, category)
    ceiling = rules.inps.ceiling if rules.inps is not None else None

    # IVS-eligible base for this period: capped at remaining ceiling headroom.
    if ceiling is not None:
        ivs_base = max(_ZERO, min(period_inps_base, ceiling - ytd_inps_base))
    else:
        ivs_base = period_inps_base

    # Employee side
    emp_ivs_rate = rates.employee_ivs_rate
    emp_non_ivs_rate = rates.employee_rate - emp_ivs_rate
    emp_ivs = money(ivs_base * emp_ivs_rate)
    emp_non_ivs = money(period_inps_base * emp_non_ivs_rate)
    employee_total = emp_ivs + emp_non_ivs

    # Employer side
    er_ivs_rate = rates.employer_ivs_rate
    er_non_ivs_rate = rates.employer_rate - er_ivs_rate
    er_ivs = money(ivs_base * er_ivs_rate)
    er_non_ivs = money(period_inps_base * er_non_ivs_rate)
    employer_total = er_ivs + er_non_ivs

    components: list[ContributionComponent] = []
    if emp_ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name="ivs_employee",
                base=ivs_base,
                rate=emp_ivs_rate,
                amount=emp_ivs,
            )
        )
    if emp_non_ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name="non_ivs_employee",
                base=period_inps_base,
                rate=emp_non_ivs_rate,
                amount=emp_non_ivs,
            )
        )
    if er_ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name="ivs_employer",
                base=ivs_base,
                rate=er_ivs_rate,
                amount=er_ivs,
            )
        )
    if er_non_ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name="non_ivs_employer",
                base=period_inps_base,
                rate=er_non_ivs_rate,
                amount=er_non_ivs,
            )
        )

    return ContributionBreakdown(
        employee=employee_total,
        employer=employer_total,
        components=tuple(components),
    )
