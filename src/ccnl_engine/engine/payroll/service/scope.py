"""Feature coverage and confidence of a payroll result."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from ccnl_engine.engine.metadata.domain.rules import SourceType, VerificationStatus
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import (
    CalculationStatus,
    EligibilityStatus,
    ScopeItem,
    SourceQuality,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.identity import CCNLCoverage
    from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

_ZERO = Decimal(0)


def compute_result_status(
    scope: tuple[ScopeItem, ...],
) -> Literal["complete", "partial"]:
    """Derive the overall result status from the calculation scope.

    Returns ``"complete"`` when every scope item is integrated into totals and
    fully engine-verified (nothing requested was blocked or caller-declared).
    Returns ``"partial"`` otherwise.

    Returns:
        ``"complete"`` or ``"partial"``.
    """
    for item in scope:
        if item.calculation_status in {
            CalculationStatus.NOT_COMPUTED,
            CalculationStatus.PARTIAL,
        }:
            return "partial"
        if item.calculation_status == CalculationStatus.COMPUTED and not (
            item.gross_integrated
            or item.contribution_integrated
            or item.tax_integrated
            or item.net_integrated
            or item.cost_integrated
        ):
            return "partial"
        if item.eligibility_status == EligibilityStatus.CALLER_DECLARED:
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


def _fiscal_scope(
    scenario: _InternalScenario,
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
    inail_rate = scenario.employment.employer.inail_rate
    exemption = scenario.employment.employer.inps_employer_exemption_annual
    prior_irpef = scenario.prior_period_irpef_withheld
    maternity = scenario.maternity_inps_indemnity_annual
    injury = scenario.workplace_injury_inail_indemnity_annual
    term_leave = scenario.termination_residual_leave_payout_annual
    term_tfr = scenario.termination_tfr_liquidation_annual
    arrears = scenario.contract_renewal_arrears_annual
    una_tantum = scenario.una_tantum_annual
    withholdings = scenario.personal_withholdings_annual
    extra_irpef = scenario.additional_irpef_base_annual
    health_employee = scenario.health_fund_employee_annual
    health_employer = scenario.health_fund_employer_annual
    territorial = scenario.territorial_supplement_annual
    company = scenario.company_supplement_annual
    return [
        _computed("base_salary"),
        _computed("seniority"),
        _computed(
            "inps_employee",
            gross=False,
            contribution=True,
            tax=False,
            net=True,
            cost=False,
        ),
        _computed(
            "inps_employer",
            gross=False,
            contribution=True,
            tax=False,
            net=False,
            cost=True,
        ),
        _caller_declared_or_excluded(
            "inail",
            inail_rate,
            gross=False,
            contribution=False,
            tax=False,
            net=False,
            cost=True,
        ),
        _caller_declared_or_excluded(
            "contribution_exemption",
            exemption,
            gross=False,
            contribution=True,
            tax=False,
            net=False,
            cost=True,
        ),
        _caller_declared_or_excluded(
            "fiscal_adjustment",
            prior_irpef,
            gross=False,
            contribution=False,
            tax=True,
            net=True,
            cost=False,
        ),
        _caller_declared_or_excluded("maternity_leave", maternity),
        _caller_declared_or_excluded("workplace_injury", injury),
        _caller_declared_or_excluded("termination_residual_leave", term_leave),
        _caller_declared_or_excluded(
            "termination_tfr",
            term_tfr,
            gross=False,
            contribution=False,
            tax=False,
            net=False,
            cost=True,
        ),
        _caller_declared_or_excluded("contract_renewal_arrears", arrears),
        _caller_declared_or_excluded("una_tantum", una_tantum),
        _caller_declared_or_excluded(
            "personal_withholdings",
            withholdings,
            gross=False,
            contribution=False,
            tax=True,
            net=True,
            cost=False,
        ),
        _caller_declared_or_excluded(
            "additional_irpef_base",
            extra_irpef,
            gross=False,
            contribution=False,
            tax=True,
            net=False,
            cost=False,
        ),
        _caller_declared_or_excluded(
            "health_fund_employee",
            health_employee,
            gross=False,
            contribution=True,
            tax=False,
            net=True,
            cost=False,
        ),
        _caller_declared_or_excluded(
            "health_fund_employer",
            health_employer,
            gross=False,
            contribution=False,
            tax=False,
            net=False,
            cost=True,
        ),
        _caller_declared_or_excluded("territorial_supplement", territorial),
        _caller_declared_or_excluded("company_supplement", company),
        _computed(
            "tfr",
            gross=False,
            contribution=False,
            tax=False,
            net=False,
            cost=True,
        ),
        (
            _computed(
                "irpef",
                gross=False,
                contribution=False,
                tax=True,
                net=True,
                cost=False,
            )
            if fiscal.employer_withholds_irpef
            else _excluded("irpef")
        ),
        (
            _excluded("trattamento_integrativo")
            if FiscalSimplification.NO_TRATTAMENTO_INTEGRATIVO in fs
            else _computed(
                "trattamento_integrativo",
                gross=False,
                contribution=False,
                tax=True,
                net=True,
                cost=False,
            )
        ),
        (
            _excluded("ulteriore_detrazione_lavoro")
            if FiscalSimplification.NO_ULTERIORE_DETRAZIONE_LAVORO in fs
            else _computed(
                "ulteriore_detrazione_lavoro",
                gross=False,
                contribution=False,
                tax=True,
                net=True,
                cost=False,
            )
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
            advance_flag=FiscalSimplification.ADDIZIONALE_COMUNALE_ADVANCE_ONLY,
        ),
        (
            _computed(
                "family_deductions",
                elig=EligibilityStatus.CALLER_DECLARED,
                gross=False,
                contribution=False,
                tax=True,
                net=True,
                cost=False,
            )
            if family_ok
            else _excluded("family_deductions")
        ),
        (
            _partial(
                "art15_deductions",
                assumptions=("partial_detrazioni_art15",),
                gross=False,
                contribution=False,
                tax=True,
                net=True,
                cost=False,
            )
            if art15_ok
            else _excluded("art15_deductions")
        ),
    ]


def _work_time_scope(
    scenario: _InternalScenario,
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
        _informational("welfare", elig=EligibilityStatus.CALLER_DECLARED)
        if scenario.welfare_input is not None
        else _excluded("welfare"),
        _not_computed("bonus_pdr")
        if scenario.bonus_input is not None and work.bonus_pdr_missing_prior_year
        else _informational("bonus_pdr")
        if scenario.bonus_input is not None
        else _excluded("bonus_pdr"),
        _informational("bilateral_funds")
        if len(scenario.bilateral_funds) > 0
        else _excluded("bilateral_funds"),
    ]


def _limitations_scope(ccnl_coverage: CCNLCoverage | None) -> list[ScopeItem]:
    """Return a scope item when the CCNL declares applicable limitations.

    A ``simplification`` or ``missing`` coverage note represents a known
    engine approximation or data gap.  The result cannot be ``complete``
    when such notes are present: at least one modelled item deviates from
    the actual contractual rule.

    Returns:
        A one-element list with an ``informational_only`` scope item, or an
        empty list when no applicable limitation notes are found.
    """
    from ccnl_engine.engine.contract.domain.identity import NoteKind  # noqa: PLC0415

    if ccnl_coverage is None:
        return []
    applicable_kinds = {NoteKind.SIMPLIFICATION, NoteKind.MISSING}
    if not any(n.kind in applicable_kinds for n in ccnl_coverage.notes):
        return []
    return [_informational("ccnl_limitations")]


def build_scope(
    scenario: _InternalScenario,
    fiscal: FiscalPay,
    work: WorkRulesPay,
    ccnl_coverage: CCNLCoverage | None = None,
) -> tuple[ScopeItem, ...]:
    """Describe which requested features were computed.

    Args:
        scenario: The payroll scenario being computed.
        fiscal: Fiscal computation results.
        work: Work-rules computation results.
        ccnl_coverage: Optional CCNL coverage block.  When provided and it
            contains ``simplification`` or ``missing`` notes, a synthetic
            ``ccnl_limitations`` scope item is appended so that
            ``compute_result_status`` returns ``"partial"`` rather than
            ``"complete"``.

    Returns:
        Scope entries in their stable presentation order.
    """
    return tuple(
        _fiscal_scope(scenario, fiscal)
        + _work_time_scope(scenario, work)
        + _limitations_scope(ccnl_coverage)
    )
