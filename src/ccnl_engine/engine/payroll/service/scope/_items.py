"""ScopeItem factory helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification

from ccnl_engine.engine.payroll.domain.payroll_result import (
    CalculationStatus,
    EligibilityStatus,
    ScopeItem,
    SourceQuality,
)


def _computed(
    feature: str,
    *,
    elig: EligibilityStatus = EligibilityStatus.ENGINE_VERIFIED,
    qual: SourceQuality = SourceQuality.VERIFIED_PRIMARY,
    assumptions: tuple[str, ...] = (),
    gross: bool = True,
    contribution: bool = True,
    tax: bool = True,
    net: bool = True,
    cost: bool = True,
) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        gross_integrated=gross,
        contribution_integrated=contribution,
        tax_integrated=tax,
        net_integrated=net,
        cost_integrated=cost,
        eligibility_status=elig,
        source_quality=qual,
        assumptions=assumptions,
    )


def _excluded(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.EXCLUDED,
        eligibility_status=EligibilityStatus.N_A,
        source_quality=SourceQuality.N_A,
    )


def _not_computed(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.NOT_COMPUTED,
        eligibility_status=EligibilityStatus.N_A,
        source_quality=SourceQuality.N_A,
    )


def _partial(
    feature: str,
    *,
    assumptions: tuple[str, ...] = (),
    gross: bool = True,
    contribution: bool = True,
    tax: bool = True,
    net: bool = True,
    cost: bool = True,
) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.PARTIAL,
        gross_integrated=gross,
        contribution_integrated=contribution,
        tax_integrated=tax,
        net_integrated=net,
        cost_integrated=cost,
        eligibility_status=EligibilityStatus.ENGINE_VERIFIED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
        assumptions=assumptions,
    )


def _informational(
    feature: str,
    *,
    elig: EligibilityStatus = EligibilityStatus.ENGINE_VERIFIED,
    qual: SourceQuality = SourceQuality.VERIFIED_PRIMARY,
) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        eligibility_status=elig,
        source_quality=qual,
    )


def _caller_declared_or_excluded(
    feature: str,
    value: object,
    *,
    gross: bool = True,
    contribution: bool = True,
    tax: bool = True,
    net: bool = True,
    cost: bool = True,
) -> ScopeItem:
    if value is not None:
        return _computed(
            feature,
            elig=EligibilityStatus.CALLER_DECLARED,
            qual=SourceQuality.ESTIMATED,
            gross=gross,
            contribution=contribution,
            tax=tax,
            net=net,
            cost=cost,
        )
    return _excluded(feature)


def _work_feature(feature: str, requested: bool, supported: bool) -> ScopeItem:
    """Classify a work-time feature from request and support flags.

    L3 work-time amounts are informational: they are computed and stored in
    the result but do not flow into ``net_annual`` or ``employer_cost``.

    Returns:
        The appropriate :class:`ScopeItem` for the feature.
    """
    if not requested:
        return _excluded(feature)
    if not supported:
        return _not_computed(feature)
    return _informational(feature)


def _surtax_scope(
    feature: str,
    no_flag: FiscalSimplification,
    unknown_flag: FiscalSimplification,
    fs: frozenset[FiscalSimplification],
    advance_flag: FiscalSimplification | None = None,
) -> ScopeItem:
    """Classify a surtax feature given its exclude and unknown simplification flags.

    Returns:
        Excluded, not_computed, partial, or computed scope item for the feature.
    """
    if no_flag in fs:
        return _excluded(feature)
    if unknown_flag in fs:
        return _not_computed(feature)
    if advance_flag is not None and advance_flag in fs:
        return _partial(
            feature,
            assumptions=("advance_only",),
            gross=False,
            contribution=False,
            tax=True,
            net=True,
            cost=False,
        )
    return _computed(
        feature, gross=False, contribution=False, tax=True, net=True, cost=False
    )
