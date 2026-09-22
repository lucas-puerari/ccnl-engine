"""Provenance collection and gross computation trace building."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.calculation import (
    CalculationTrace,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        Level,
        SeniorityIncrements,
        SupplementaryAllowance,
    )
    from ccnl_engine.engine.payroll.service.types import MonthlyPayChain
    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

_ZERO = Decimal(0)


def _collect_provenance(
    level: Level,
    as_of: date,
    chain: MonthlyPayChain,
    seniority_increments: SeniorityIncrements,
    *,
    ccnl: CCNL | None = None,
    under_level_code: str | None = None,
) -> tuple[RuleProvenance, ...]:
    """Collect provenance for all rules that contributed to a pay outcome.

    Gathers the effective pay level (plus per-period base-salary override),
    each applied allowance, and the seniority-increment rule.

    For under-classification apprentices, ``level`` is the destination level
    but pay is derived from ``under_level_code``.  When both ``ccnl`` and
    ``under_level_code`` are provided, the effective pay level's provenance
    is recorded instead of the destination level.

    Returns:
        Ordered provenance tuple, one entry per contributing rule.
    """
    out: list[RuleProvenance] = []

    def _add(prov: RuleProvenance | None) -> None:
        if prov is not None:
            out.append(prov)

    effective_level = (
        ccnl.level_by_code(under_level_code)
        if ccnl is not None and under_level_code is not None
        else level
    )
    _add(effective_level.provenance)
    for period in effective_level.base_salary.periods:
        if period.valid_from <= as_of and (
            period.valid_until is None or as_of < period.valid_until
        ):
            _add(period.provenance)
            break
    for allowance, _ in chain.allowances:
        _add(allowance.provenance)
    _add(seniority_increments.provenance)
    return tuple(out)


def _build_trace(
    ccnl_id: str,
    level: Level,
    chain: MonthlyPayChain,
    seniority_count: int,
    ad_personam: Decimal,
    scaled_second_level: tuple[tuple[Decimal, SupplementaryAllowance], ...],
    gross_monthly: Decimal,
) -> CalculationTrace:
    """Build the step-by-step gross computation trace, post-scaling.

    All amounts are taken from already-scaled values (part-time and
    apprenticeship percentages already applied), so the trace faithfully
    represents the actual contribution of each component.

    Returns:
        A :class:`CalculationTrace` whose non-GROSS steps sum to ``gross_monthly``.
    """
    steps: list[TraceStep] = [
        TraceStep(
            category=TraceCategory.BASE_SALARY,
            label="Base retributiva",
            amount=chain.base,
            detail=f"{level.code}@{ccnl_id}",
        ),
        TraceStep(
            category=TraceCategory.SENIORITY,
            label="Scatti di anzianità",
            amount=chain.seniority,
            detail=f"scatti={seniority_count}",
        ),
    ]

    for allowance, amount in chain.allowances:
        steps.append(
            TraceStep(
                category=TraceCategory.ALLOWANCE,
                label=allowance.description,
                amount=amount,
                detail=allowance.code,
            )
        )

    if ad_personam > _ZERO:
        steps.append(
            TraceStep(
                category=TraceCategory.AD_PERSONAM,
                label="Ad personam",
                amount=ad_personam,
            )
        )

    for scaled, sl in scaled_second_level:
        if scaled > _ZERO:
            steps.append(
                TraceStep(
                    category=TraceCategory.SECOND_LEVEL,
                    label=sl.description,
                    amount=scaled,
                    detail=sl.code,
                )
            )

    # When a negotiated RAL overrides the component sum (e.g. DestinationRalOverride
    # or a plain RalOverride), the gross_monthly differs from the sum of components.
    # A RAL_OVERRIDE step bridges the gap so the invariant always holds:
    #   sum(non-GROSS steps) == GROSS step amount
    component_sum = money(sum((s.amount for s in steps), _ZERO))
    ral_delta = money(gross_monthly - component_sum)
    if ral_delta != _ZERO:
        steps.append(
            TraceStep(
                category=TraceCategory.RAL_OVERRIDE,
                label="Rettifica RAL concordata",
                amount=ral_delta,
            )
        )

    steps.append(
        TraceStep(
            category=TraceCategory.GROSS,
            label="Lordo mensile",
            amount=gross_monthly,
        )
    )

    return CalculationTrace(steps=tuple(steps))
