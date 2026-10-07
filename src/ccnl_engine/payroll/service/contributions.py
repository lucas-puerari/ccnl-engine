"""Social security contribution calculations.

IVS ceiling split: when the ceiling applies and the INPS rules carry a non-null
``ceiling``, only the IVS portion of each INPS rate is capped at the massimale
annuo della base contributiva (Art. 2 c. 18 L. 335/1995); the remainder
(NASpI, CUAF, CIG, etc.) is applied to the full base.  The ceiling is enforced
via ``ytd_inps_base``: only the portion of ``period_inps_base`` fitting within
the remaining headroom attracts IVS contributions.  Whether it applies is
derived by the caller from the worker's contribution history (first enrolment
from 1 Jan 1996, or the contributory option of Art. 1 c. 23); this module
never assumes it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from ccnl_engine.payroll.service.additional_ivs import (
    AdditionalIvsPosition,
    additional_ivs,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
    from ccnl_engine.tax.domain.ruleset import YearRules

_ZERO = Decimal(0)
_NO_POSITION = AdditionalIvsPosition()


def _side(
    side: str,
    rate: Decimal,
    ivs_rate: Decimal,
    ivs_base: Decimal,
    full_base: Decimal,
) -> tuple[Decimal, list[ContributionComponent]]:
    """Split one side's contribution into its IVS and non-IVS parts.

    The IVS part applies ``ivs_rate`` to the capped ``ivs_base``; the rest of
    ``rate`` applies to the full base.

    Returns:
        The side's total and its components ``ivs_<side>`` and
        ``non_ivs_<side>``, each only when its rate is positive.
    """
    non_ivs_rate = rate - ivs_rate
    ivs = money(ivs_base * ivs_rate)
    non_ivs = money(full_base * non_ivs_rate)
    components: list[ContributionComponent] = []
    if ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name=f"ivs_{side}", base=ivs_base, rate=ivs_rate, amount=ivs
            )
        )
    if non_ivs_rate > _ZERO:
        components.append(
            ContributionComponent(
                name=f"non_ivs_{side}",
                base=full_base,
                rate=non_ivs_rate,
                amount=non_ivs,
            )
        )
    return ivs + non_ivs, components


def _additional(
    rules: YearRules,
    period_inps_base: Decimal,
    ytd_inps_base: Decimal,
    ceiling: Decimal | None,
    position: AdditionalIvsPosition,
) -> ContributionComponent | None:
    """Return the additional 1% IVS of the run, if the rules model it.

    Returns:
        The component of :func:`additional_ivs`, ``None`` without a rule.
    """
    rule = None if rules.inps is None else rules.inps.employee_additional
    if rule is None:
        return None
    return additional_ivs(
        rule,
        period_inps_base,
        ytd_base=ytd_inps_base,
        ceiling=ceiling,
        position=position,
    )


def resolve_contributions(
    period_inps_base: Decimal,
    rules: YearRules,
    contract_type: Permanent | FixedTerm | Apprentice,
    category: WorkerCategory | None,
    *,
    ytd_inps_base: Decimal,
    ivs_ceiling_applies: bool,
    additional: AdditionalIvsPosition = _NO_POSITION,
) -> ContributionBreakdown:
    """Compute INPS contributions with per-component breakdown and IVS ceiling.

    The IVS portion of both employee and employer contributions is capped at
    the massimale (Art. 2 c. 18 L. 335/1995) when it applies and a ceiling is
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
            (from ``TaxCashState.earnings.inps_base``). Used to enforce the
            annual IVS ceiling across periods.
        ivs_ceiling_applies: Whether the massimale applies to the worker.
            When False all contributions are applied to the full base.
        additional: Position of the run toward the additional 1% IVS
            (:mod:`~ccnl_engine.payroll.service.additional_ivs`); by default
            the first run of its month, settling nothing.

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

    employee_total, employee_items = _side(
        "employee",
        rates.employee_rate,
        rates.employee_ivs_rate,
        ivs_base,
        period_inps_base,
    )
    employer_total, employer_items = _side(
        "employer",
        rates.employer_rate,
        rates.employer_ivs_rate,
        ivs_base,
        period_inps_base,
    )
    components = [*employee_items, *employer_items]

    add_comp = _additional(rules, period_inps_base, ytd_inps_base, ceiling, additional)
    if add_comp is not None:
        employee_total += add_comp.amount
        components.append(add_comp)

    return ContributionBreakdown(
        employee=employee_total,
        employer=employer_total,
        components=tuple(components),
    )
