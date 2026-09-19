"""Feature coverage and confidence of a payroll result."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from ccnl_engine.engine.metadata.domain.rules import SourceType, VerificationStatus
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import ScopeItem

if TYPE_CHECKING:
    from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

_ZERO = Decimal(0)


def compute_result_status(
    scope: tuple[ScopeItem, ...],
) -> Literal["complete", "partial"]:
    """Derive the overall result status from the calculation scope.

    Returns ``"complete"`` when every scope item is included in totals and
    fully engine-verified (nothing requested was blocked or caller-declared).
    Returns ``"partial"`` otherwise.

    Returns:
        ``"complete"`` or ``"partial"``.
    """
    for item in scope:
        if item.calculation_status in {"not_computed", "partial"}:
            return "partial"
        if item.integration_status == "informational_only":
            return "partial"
        if item.eligibility_status == "caller_declared":
            return "partial"
    return "complete"


def compute_confidence(
    status: Literal["complete", "partial"],
    warnings: tuple[str, ...],
    provenance: tuple[RuleProvenance, ...],
    rulesets: tuple[RulesetIdentity | None, ...] = (),
) -> Literal["low", "medium", "high"]:
    """Derive a confidence level from result status, warnings, and provenance.

    Three-tier scale:

    ``"low"``
        Any active warning is present — the engine was asked to compute
        something it could not handle (missing CCNL schema), so the result
        is knowingly incomplete in a way the caller cannot quantify.

    ``"high"``
        The computation is complete, there are no warnings, and every record
        in the provenance chain and every consumed ruleset has
        :attr:`~ccnl_engine.engine.metadata.domain.rules.VerificationStatus\
.VERIFIED` status.

    ``"medium"``
        All other cases: any unverified provenance source or ruleset, partial
        computation without active warnings, or features explicitly excluded
        by the caller.

    The ``fiscal_simplifications`` frozenset is intentionally excluded from
    this formula — those reflect deliberate caller choices (omitted region,
    commune, etc.), not engine uncertainty.  They appear in
    ``calculation_scope`` as ``"excluded"`` items.

    Args:
        status: Whether the computation is ``"complete"`` or ``"partial"``.
        warnings: Active engine warnings from the computation.
        provenance: Provenance chain for salary rules consumed.
        rulesets: Identity records for all consumed rulesets (fiscal, INPS,
            surtax, and optional-feature rulesets).  Each entry's
            ``verification_status`` is included in the check.  A ``None``
            entry means a ruleset was consumed but its identity is absent
            or incomplete; it is treated as unverified.

    Returns:
        One of ``"low"``, ``"medium"``, or ``"high"``.
    """
    if warnings:
        return "low"
    any_unverified = any(
        prov.extraction.verification_status != VerificationStatus.VERIFIED
        for prov in provenance
    ) or any(
        ruleset_id is None
        or ruleset_id.verification_status != VerificationStatus.VERIFIED
        for ruleset_id in rulesets
    )
    any_low_confidence_source = any(
        ruleset_id is not None
        and ruleset_id.source_type in {SourceType.DERIVED, SourceType.ESTIMATED}
        and ruleset_id.verification_status != VerificationStatus.VERIFIED
        for ruleset_id in rulesets
    )
    if status == "complete" and not any_unverified and not any_low_confidence_source:
        return "high"
    return "medium"


def _computed(
    feature: str,
    *,
    elig: Literal[
        "engine_verified", "caller_declared", "unknown", "n_a"
    ] = "engine_verified",
    qual: Literal[
        "verified_primary", "unverified", "estimated", "n_a"
    ] = "verified_primary",
    assumptions: tuple[str, ...] = (),
) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status="computed",
        integration_status="included_in_totals",
        eligibility_status=elig,
        source_quality=qual,
        assumptions=assumptions,
    )


def _excluded(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status="excluded",
        integration_status="n_a",
        eligibility_status="n_a",
        source_quality="n_a",
    )


def _not_computed(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status="not_computed",
        integration_status="n_a",
        eligibility_status="n_a",
        source_quality="n_a",
    )


def _informational(
    feature: str,
    *,
    elig: Literal[
        "engine_verified", "caller_declared", "unknown", "n_a"
    ] = "engine_verified",
) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status="computed",
        integration_status="informational_only",
        eligibility_status=elig,
        source_quality="verified_primary",
    )


def _partial(
    feature: str,
    *,
    assumptions: tuple[str, ...] = (),
) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status="partial",
        integration_status="included_in_totals",
        eligibility_status="engine_verified",
        source_quality="verified_primary",
        assumptions=assumptions,
    )


def _work_feature(feature: str, requested: bool, supported: bool) -> ScopeItem:
    """Classify a work-time feature from request and support flags.

    Returns:
        The appropriate :class:`ScopeItem` for the feature.
    """
    if not requested:
        return _excluded(feature)
    if not supported:
        return _not_computed(feature)
    return _computed(feature)


def _surtax_scope(
    feature: str,
    no_flag: FiscalSimplification,
    unknown_flag: FiscalSimplification,
    fs: frozenset[FiscalSimplification],
) -> ScopeItem:
    """Classify a surtax feature given its exclude and unknown simplification flags.

    Returns:
        Excluded, not_computed, or computed scope item for the feature.
    """
    if no_flag in fs:
        return _excluded(feature)
    if unknown_flag in fs:
        return _not_computed(feature)
    return _computed(feature)


def _fiscal_scope(
    scenario: PayrollScenario,
    fiscal: FiscalPay,
) -> list[ScopeItem]:
    """Build scope items for fiscal (L1/L2) features.

    Returns:
        Scope items for base salary, INPS, TFR, IRPEF, deductions.
    """
    fs = fiscal.fiscal_simplifications
    family_ok = scenario.family is not None and scenario.family.has_any_dependent
    art15_ok = (
        scenario.art15_deductions is not None
        and scenario.art15_deductions.has_any_onere
    )
    return [
        _computed("base_salary"),
        _computed("seniority"),
        _computed("inps_employee"),
        _computed("inps_employer"),
        _computed("tfr"),
        _computed("irpef") if fiscal.employer_withholds_irpef else _excluded("irpef"),
        (
            _excluded("trattamento_integrativo")
            if FiscalSimplification.NO_TRATTAMENTO_INTEGRATIVO in fs
            else _computed("trattamento_integrativo")
        ),
        (
            _excluded("ulteriore_detrazione_lavoro")
            if FiscalSimplification.NO_ULTERIORE_DETRAZIONE_LAVORO in fs
            else _computed("ulteriore_detrazione_lavoro")
        ),
        _surtax_scope(
            "addizionale_regionale",
            FiscalSimplification.NO_ADDIZIONALE_REGIONALE,
            FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN,
            fs,
        ),
        _surtax_scope(
            "addizionale_comunale",
            FiscalSimplification.NO_ADDIZIONALE_COMUNALE,
            FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN,
            fs,
        ),
        (
            _computed("family_deductions", elig="caller_declared")
            if family_ok
            else _excluded("family_deductions")
        ),
        (
            _partial("art15_deductions", assumptions=("partial_detrazioni_art15",))
            if art15_ok
            else _excluded("art15_deductions")
        ),
    ]


def _work_time_scope(
    scenario: PayrollScenario,
    work: WorkRulesPay,
) -> list[ScopeItem]:
    """Build scope items for work-time and variable-pay (L3) features.

    Returns:
        Scope items for overtime, absence, fringe, welfare, bonus, funds.
    """
    zero = Decimal(0)
    ts = scenario.time_supplements
    ot_hours = (ts.weekday_hours + ts.supplementare_hours) if ts is not None else zero
    night_hours = ts.night_hours if ts is not None else zero
    holiday_hours = (
        (ts.holiday_hours + ts.night_holiday_hours) if ts is not None else zero
    )
    return [
        _work_feature("overtime", ot_hours > _ZERO, work.wr_overtime_supported),
        _work_feature("night_work", night_hours > _ZERO, work.wr_night_supported),
        _work_feature("holiday_work", holiday_hours > _ZERO, work.wr_holiday_supported),
        _work_feature(
            "absence",
            scenario.absence_days is not None
            and scenario.absence_days.unpaid_days != _ZERO,
            work.wr_absence_present,
        ),
        _work_feature("leave", scenario.leave_input is not None, work.wr_leave_present),
        _work_feature(
            "sickness",
            scenario.sick_input is not None and scenario.sick_input.sick_days > _ZERO,
            work.wr_sickness_present,
        ),
        _informational("fringe_benefit")
        if scenario.fringe_benefit_input is not None
        else _excluded("fringe_benefit"),
        _computed("welfare", elig="caller_declared")
        if scenario.welfare_input is not None
        else _excluded("welfare"),
        _informational("bonus_pdr")
        if scenario.bonus_input is not None
        else _excluded("bonus_pdr"),
        _computed("bilateral_funds")
        if len(scenario.bilateral_funds) > 0
        else _excluded("bilateral_funds"),
    ]


def build_scope(
    scenario: PayrollScenario,
    fiscal: FiscalPay,
    work: WorkRulesPay,
) -> tuple[ScopeItem, ...]:
    """Describe which requested features were computed.

    Returns:
        Scope entries in their stable presentation order.
    """
    return tuple(_fiscal_scope(scenario, fiscal) + _work_time_scope(scenario, work))
