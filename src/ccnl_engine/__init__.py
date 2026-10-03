"""ccnl_engine: Italian CCNL payroll computation library.

Public API
----------
The single entry point is :class:`PayrollEngine`.  Construct it with
:meth:`~PayrollEngine.bundled` and call
:meth:`~PayrollEngine.calculate_period` for one cedolino,
:meth:`~PayrollEngine.calculate_year` for every run of a tax year and
:meth:`~PayrollEngine.close_tax_year` to open the next tax year.

All types needed to call it and inspect its results are re-exported from
this module, work events included.

Usage::

    from datetime import date
    from ccnl_engine import (
        Employment, EmployerProfile, Headcount, PayrollEngine, PayrollRun,
        PeriodInput,
    )

    engine = PayrollEngine.bundled()
    result = engine.calculate_period(PeriodInput(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    ))
    print(result.is_payable, result.period_net)
    for blocker in result.blockers:
        print(blocker.code, blocker.feature, blocker.detail)
    for ruleset in result.rulesets:
        print(ruleset.id, ruleset.kind, ruleset.readiness)
    for limitation in result.assurance.limitations:
        print(limitation.id, limitation.monetary_impact, limitation.status)

``PayrollEngine.bundled(mode="operational")`` also blocks payment from any
ruleset that is not ``production``; :meth:`~PayrollEngine.list_contracts` and
:meth:`~PayrollEngine.inspect_ruleset` report readiness before any run.
"""

from __future__ import annotations

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.service.discovery import (
    CcnlId,
    ContractSummary,
    get_ccnl,
    search_ccnls,
)
from ccnl_engine.payroll.application.calculate_year import YearResult
from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.domain.assurance import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
)
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityImplementation,
)
from ccnl_engine.payroll.domain.capability_report import (
    CapabilityGap,
    CapabilityScope,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from ccnl_engine.payroll.domain.employer import (
    EmployerActivity,
    EmployerProfile,
    Headcount,
)
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    Employment,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.domain.employment_facts import (
    ContributableHours,
    EmploymentPeriod,
    WeeklyHours,
)
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput
from ccnl_engine.payroll.domain.obligations import RecoveryObligation
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import (
    ForeignTaxPaid,
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
    SubstituteTaxRegime,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.remittance import RemittanceColumn, RemittanceLine
from ccnl_engine.payroll.domain.run import PayrollRun, PayrollRunId
from ccnl_engine.payroll.domain.seniority_fact import (
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.surtax_obligations import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.payroll.domain.year_input import YearInput
from ccnl_engine.provenance.domain.ruleset_assurance import (
    RulesetAssurance,
    RulesetKind,
)
from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetIdentity,
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.shared.domain.errors import (
    CcnlEngineError,
    DataIntegrityError,
    InvalidInputError,
    MissingRequiredFactError,
    MissingRuleError,
    OutOfScopeError,
    UnknownCcnlError,
    UnknownLevelError,
    UnsupportedTaxYearError,
)
from ccnl_engine.shared.domain.limitation import (
    LimitationStatus,
    ModelLimitation,
    MonetaryImpact,
)
from ccnl_engine.tax.domain.preferential_regime import EmploymentSector
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "AbsenceEvent",
    "Apprentice",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BlockerCode",
    "BonusEvent",
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "CalendarOverride",
    "CalendarOverrideReason",
    "CapabilityCatalog",
    "CapabilityEntry",
    "CapabilityGap",
    "CapabilityImplementation",
    "CapabilityScope",
    "CcnlEngineError",
    "CcnlId",
    "ContractSummary",
    "ContributableHours",
    "ContributionHistory",
    "CoverageStatus",
    "DataIntegrityError",
    "DecisionOrigin",
    "DeferredShortfall",
    "Dependent",
    "DependentRelationship",
    "EmployerActivity",
    "EmployerProfile",
    "Employment",
    "EmploymentPeriod",
    "EmploymentSector",
    "EngineMode",
    "EvidenceStatus",
    "FamilyComposition",
    "FixedTerm",
    "ForeignTaxPaid",
    "FringeEvent",
    "Headcount",
    "HolidayWorkEvent",
    "InvalidInputError",
    "LimitationStatus",
    "MissingRequiredFactError",
    "MissingRuleError",
    "ModelLimitation",
    "MonetaryImpact",
    "NightShiftEvent",
    "OpeningBalances",
    "OutOfScopeError",
    "OvertimeEvent",
    "OvertimeKind",
    "Payability",
    "PaymentId",
    "PayrollEngine",
    "PayrollRun",
    "PayrollRunId",
    "PensionFundEnrolment",
    "PeriodFacts",
    "PeriodInput",
    "PeriodResult",
    "PeriodState",
    "Permanent",
    "PriorYearTaxFacts",
    "RecoveryObligation",
    "RecoveryPlan",
    "RemittanceColumn",
    "RemittanceLine",
    "ResultAssurance",
    "ResultBlocker",
    "RulesetAssurance",
    "RulesetIdentity",
    "RulesetKind",
    "RulesetReadiness",
    "SeniorityFact",
    "SenioritySource",
    "ShiftWorkEvent",
    "ShortfallDeferralRequest",
    "SickLeaveEvent",
    "SicknessCaseEvent",
    "SubstituteTaxRegime",
    "SurtaxComponent",
    "SurtaxObligation",
    "TerminationTFREvent",
    "UnknownCcnlError",
    "UnknownLevelError",
    "UnsupportedTaxYearError",
    "VerificationStatus",
    "WeeklyHours",
    "WelfareEvent",
    "WorkCalendar",
    "WorkEvent",
    "WorkerCategory",
    "YearInput",
    "YearResult",
    "engine_version",
    "get_ccnl",
    "search_ccnls",
]
