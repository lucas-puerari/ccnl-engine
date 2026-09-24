"""Social security and TFR contribution calculations.

IVS ceiling split: when the ceiling applies and the tax file carries a non-null
``ceiling``, only the IVS portion of each INPS rate is capped at the massimale
retributivo (Art. 1 c. 18 L. 335/1995); the remainder (NASpI, CUAF, CIG, etc.)
is applied to the full base.  The ceiling is enforced via ``ytd_inps_base``:
only the portion of ``period_inps_base`` fitting within the remaining headroom
attracts IVS contributions.  Defaulting ``ivs_ceiling_applies`` to True
preserves correct behaviour for post-1995 enrollees; set it to False only for
workers enrolled before 1 Jan 1996 (Art. 1 c. 18 L. 335/1995).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.service._contributions_apprentice import (
    apprentice_employer_ivs_rate as apprentice_employer_ivs_rate,
)
from ccnl_engine.payroll.service._contributions_apprentice import (
    apprentice_employer_rate as apprentice_employer_rate,
)
from ccnl_engine.payroll.service._contributions_domestic import (
    resolve_domestic_inps_rate as resolve_domestic_inps_rate,
)
from ccnl_engine.payroll.service._contributions_rates import (
    ContributionRates as ContributionRates,
)
from ccnl_engine.payroll.service._contributions_rates import (
    inps_employer_rate as inps_employer_rate,
)
from ccnl_engine.payroll.service._contributions_rates import (
    resolve_rates as resolve_rates,
)
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import EmployerFund, LevelCategory
    from ccnl_engine.engine.tax.domain.rules import InpsRates, YearRules
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent

_ZERO = Decimal(0)


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


def fund_applies_to(fund: EmployerFund, category: LevelCategory | None) -> bool:
    """Return whether the fund applies to a level of the given category.

    Returns:
        True if the fund applies to the given category, False otherwise.
    """
    if fund.applies_to_categories is None:
        return True
    return category is not None and category in fund.applies_to_categories


def _addizionale_1pct(
    period_inps_base: Decimal,
    rules: YearRules,
    *,
    ytd_inps_base: Decimal,
    ceiling: Decimal | None,
) -> ContributionComponent | None:
    """Return the 1% addizionale INPS component, or None when not applicable.

    INPS circ. 4/2026: charged on the portion of the annual INPS base
    exceeding the statutory threshold but capped at the IVS massimale.

    Returns:
        A :class:`ContributionComponent` or ``None`` if not applicable.
    """
    inps = rules.inps
    if (
        inps is None
        or inps.employee_additional_rate is None
        or inps.employee_additional_threshold is None
    ):
        return None
    add_threshold = inps.employee_additional_threshold
    ytd_capped = min(ytd_inps_base, ceiling) if ceiling is not None else ytd_inps_base
    ytd_after_capped = (
        min(ytd_inps_base + period_inps_base, ceiling)
        if ceiling is not None
        else ytd_inps_base + period_inps_base
    )
    period_excess = max(_ZERO, ytd_after_capped - add_threshold) - max(
        _ZERO, ytd_capped - add_threshold
    )
    add_amount = money(period_excess * inps.employee_additional_rate)
    if add_amount <= _ZERO:
        return None
    return ContributionComponent(
        name="addizionale_1pct",
        base=period_excess,
        rate=inps.employee_additional_rate,
        amount=add_amount,
    )


def resolve_contributions(
    period_inps_base: Decimal,
    rules: YearRules,
    contract_type: Permanent | FixedTerm | Apprentice,
    category: LevelCategory | None,
    *,
    ytd_inps_base: Decimal = _ZERO,
    ivs_ceiling_applies: bool = True,
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
        ivs_ceiling_applies: When False the massimale ceiling is bypassed
            and all contributions are applied to the full base.

    Returns:
        :class:`~ccnl_engine.payroll.domain.contributions.ContributionBreakdown`
        with employee/employer totals and per-component trace.
    """
    rates = resolve_rates(rules, contract_type, category)
    ceiling = (
        rules.inps.ceiling if (rules.inps is not None and ivs_ceiling_applies) else None
    )

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

    add_comp = _addizionale_1pct(
        period_inps_base, rules, ytd_inps_base=ytd_inps_base, ceiling=ceiling
    )
    if add_comp is not None:
        employee_total += add_comp.amount
        components.append(add_comp)

    return ContributionBreakdown(
        employee=employee_total,
        employer=employer_total,
        components=tuple(components),
    )
