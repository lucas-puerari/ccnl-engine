"""Feature coverage and confidence of a payroll result."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Literal

from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import ScopeItem
from ccnl_engine.engine.provenance.domain.source import SourceKind

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

_ZERO = Decimal(0)


def _compute_result_status(
    scope: tuple[ScopeItem, ...],
) -> Literal["complete", "partial"]:
    """Derive the overall result status from the calculation scope.

    Returns ``"complete"`` when every scope item is either ``"verified"``
    or ``"excluded"`` (nothing was requested but blocked by missing CCNL
    schema).  Returns ``"partial"`` otherwise.

    Returns:
        ``"complete"`` or ``"partial"``.
    """
    for item in scope:
        if item.status == "not_computed":
            return "partial"
    return "complete"


def _compute_confidence(
    status: Literal["complete", "partial"],
    warnings: tuple[str, ...],
    provenance: tuple[RuleProvenance, ...],
) -> Literal["low", "medium", "high"]:
    """Derive a confidence level from result status, warnings, and provenance.

    Three-tier scale:

    ``"low"``
        Any active warning is present — the engine was asked to compute
        something it could not handle (missing CCNL schema), so the result
        is knowingly incomplete in a way the caller cannot quantify.

    ``"high"``
        The computation is complete, there are no warnings, and every
        :attr:`~ccnl_engine.engine.provenance.domain.source.SourceKind\
.TABELLA_RETRIBUTIVA` record in the provenance chain has
        :attr:`~ccnl_engine.engine.metadata.domain.rules.VerificationStatus\
.VERIFIED` status.

    ``"medium"``
        All other cases: unverified salary-table sources, partial computation
        without active warnings, or features explicitly excluded by the caller.

    The ``fiscal_simplifications`` frozenset is intentionally excluded from
    this formula — those reflect deliberate caller choices (omitted region,
    commune, etc.), not engine uncertainty.  They appear in
    ``calculation_scope`` as ``"excluded"`` items.

    Returns:
        One of ``"low"``, ``"medium"``, or ``"high"``.
    """
    if warnings:
        return "low"
    salary_table_unverified = any(
        p.location.source_document.kind == SourceKind.TABELLA_RETRIBUTIVA
        and p.extraction.verification_status != VerificationStatus.VERIFIED
        for p in provenance
    )
    if status == "complete" and not salary_table_unverified:
        return "high"
    return "medium"


def _feature_status(
    requested: bool,
    supported: bool = True,
) -> Literal["verified", "excluded", "not_computed"]:
    """Classify a feature from its request and rule availability.

    Returns:
        Excluded for omitted inputs, not computed for unsupported requests,
        or verified for supported requests.
    """
    if not requested:
        return "excluded"
    if not supported:
        return "not_computed"
    return "verified"


def build_scope(
    scenario: PayrollScenario,
    fiscal: FiscalPay,
    work: WorkRulesPay,
) -> tuple[ScopeItem, ...]:
    """Describe which requested features were computed.

    Returns:
        Scope entries in their stable presentation order.
    """
    fs = fiscal.fiscal_simplifications
    zero = Decimal(0)
    ot_hours = (
        (
            scenario.time_supplements.weekday_hours
            + scenario.time_supplements.supplementare_hours
        )
        if (scenario.time_supplements is not None)
        else zero
    )
    night_hours = (
        scenario.time_supplements.night_hours
        if scenario.time_supplements is not None
        else zero
    )
    holiday_hours = (
        scenario.time_supplements.holiday_hours
        if scenario.time_supplements is not None
        else zero
    )
    items: list[ScopeItem] = [
        ScopeItem(feature="base_salary", status="verified"),
        ScopeItem(feature="seniority", status="verified"),
        ScopeItem(feature="inps_employee", status="verified"),
        ScopeItem(feature="inps_employer", status="verified"),
        ScopeItem(feature="tfr", status="verified"),
        ScopeItem(
            feature="irpef",
            status="verified" if fiscal.employer_withholds_irpef else "excluded",
        ),
        ScopeItem(
            feature="trattamento_integrativo",
            status=(
                "excluded"
                if FiscalSimplification.NO_TRATTAMENTO_INTEGRATIVO in fs
                else "verified"
            ),
        ),
        ScopeItem(
            feature="addizionale_regionale",
            status=(
                "excluded"
                if FiscalSimplification.NO_ADDIZIONALE_REGIONALE in fs
                else (
                    "not_computed"
                    if FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN in fs
                    else "verified"
                )
            ),
        ),
        ScopeItem(
            feature="addizionale_comunale",
            status=(
                "excluded"
                if FiscalSimplification.NO_ADDIZIONALE_COMUNALE in fs
                else (
                    "not_computed"
                    if FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN in fs
                    else "verified"
                )
            ),
        ),
        ScopeItem(
            feature="family_deductions",
            status=(
                "verified"
                if (scenario.family is not None and scenario.family.has_any_dependent)
                else "excluded"
            ),
        ),
        ScopeItem(
            feature="art15_deductions",
            status=(
                "verified"
                if (
                    scenario.art15_deductions is not None
                    and scenario.art15_deductions.has_any_onere
                )
                else "excluded"
            ),
        ),
        ScopeItem(
            feature="overtime",
            status=_feature_status(ot_hours > _ZERO, work.wr_schema_present),
        ),
        ScopeItem(
            feature="night_work",
            status=_feature_status(night_hours > _ZERO, work.wr_schema_present),
        ),
        ScopeItem(
            feature="holiday_work",
            status=_feature_status(holiday_hours > _ZERO, work.wr_schema_present),
        ),
        ScopeItem(
            feature="absence",
            status=_feature_status(
                scenario.absence_days is not None
                and scenario.absence_days.unpaid_days != _ZERO,
                work.wr_absence_present,
            ),
        ),
        ScopeItem(
            feature="leave",
            status=_feature_status(
                scenario.leave_input is not None, work.wr_leave_present
            ),
        ),
        ScopeItem(
            feature="sickness",
            status=_feature_status(
                scenario.sick_input is not None, work.wr_sickness_present
            ),
        ),
        ScopeItem(
            feature="fringe_benefit",
            status=_feature_status(scenario.fringe_benefit_input is not None),
        ),
        ScopeItem(
            feature="welfare",
            status=_feature_status(scenario.welfare_input is not None),
        ),
        ScopeItem(
            feature="bonus_pdr",
            status=_feature_status(scenario.bonus_input is not None),
        ),
    ]
    return tuple(items)
