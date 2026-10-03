"""Contract tests for ccnl_engine's public API surface.

These tests guard against accidental drift in __all__ and ensure that
every advertised name is importable.
"""

import dataclasses
import inspect
import re

import ccnl_engine
from ccnl_engine.payroll.domain.decisions import PUBLIC_FACTS
from ccnl_engine.shared.domain import errors as errors_module
from ccnl_engine.shared.domain.errors import PUBLIC_ERROR_CODES, CcnlEngineError

EXPECTED_PUBLIC: frozenset[str] = frozenset({
    "AbsenceEvent",
    "Apprentice",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "BlockerCode",
    "CoverageStatus",
    "Payability",
    "ResultAssurance",
    "LimitationStatus",
    "MissingRequiredFactError",
    "MissingRuleError",
    "ModelLimitation",
    "MonetaryImpact",
    "ResultBlocker",
    "EvidenceStatus",
    "RulesetIdentity",
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
    "EngineMode",
    "RulesetAssurance",
    "RulesetKind",
    "RulesetReadiness",
    "VerificationStatus",
    "ContributableHours",
    "ContributionHistory",
    "DataIntegrityError",
    "DecisionOrigin",
    "DeferredShortfall",
    "CurrentYearTaxFacts",
    "Dependent",
    "DependentRelationship",
    "EmployerActivity",
    "EmployerProfile",
    "Employment",
    "EmploymentPeriod",
    "EmploymentSector",
    "FamilyComposition",
    "FixedTerm",
    "ForeignTaxPaid",
    "FringeEvent",
    "Headcount",
    "HolidayWorkEvent",
    "InpsBaseYtd",
    "InvalidInputError",
    "NightShiftEvent",
    "OpeningBalances",
    "OutOfScopeError",
    "OvertimeEvent",
    "OvertimeKind",
    "PayrollEngine",
    "PayrollRun",
    "PayrollRunId",
    "PaymentId",
    "PeriodFacts",
    "PeriodInput",
    "PeriodResult",
    "PensionFundEnrolment",
    "PeriodState",
    "Permanent",
    "PriorYearTaxFacts",
    "IncomeEstimateQuality",
    "ShortfallDeferralRequest",
    "RecoveryObligation",
    "RecoveryPlan",
    "RemittanceColumn",
    "RemittanceLine",
    "SeniorityFact",
    "SenioritySource",
    "ShiftWorkEvent",
    "SickLeaveEvent",
    "SicknessCaseEvent",
    "SubstituteTaxRegime",
    "TaxYearPlan",
    "TaxYearResult",
    "TerminationTFREvent",
    "UnknownCcnlError",
    "UnknownLevelError",
    "UnsupportedTaxYearError",
    "SurtaxComponent",
    "SurtaxObligation",
    "WeeklyHours",
    "WelfareEvent",
    "WorkCalendar",
    "WorkEvent",
    "WorkerCategory",
    "CompetenceYearPlan",
    "CompetenceYearResult",
    "engine_version",
    "get_ccnl",
    "search_ccnls",
})


def test_all_exact() -> None:
    """__all__ must match the expected set exactly — no more, no less."""
    assert set(ccnl_engine.__all__) == EXPECTED_PUBLIC


def test_all_names_resolve() -> None:
    """Every name in __all__ must be importable from ccnl_engine."""
    for name in ccnl_engine.__all__:
        assert hasattr(ccnl_engine, name), f"Missing from ccnl_engine: {name}"


def _engine_errors() -> list[type[CcnlEngineError]]:
    pending, found = [CcnlEngineError], []
    while pending:
        for sub in pending.pop().__subclasses__():
            found.append(sub)
            pending.append(sub)
    return found


def test_every_engine_error_is_public_with_a_public_code() -> None:
    """Each error a caller can catch is exported at the root.

    Its code is a :data:`PUBLIC_ERROR_CODES` commitment and it is not a
    builtin error such as ``ValueError``: one hierarchy, caught as
    :class:`CcnlEngineError`.
    """
    errors = _engine_errors()
    assert errors
    for error in errors:
        assert error.__module__ == errors_module.__name__, error
        assert error.__name__ in ccnl_engine.__all__, error
        assert not issubclass(error, ValueError | TypeError | LookupError), error
    assert {_code_of(error) for error in errors} == PUBLIC_ERROR_CODES


def _code_of(error: type[CcnlEngineError]) -> str:
    source = inspect.getsource(error)
    codes: list[str] = re.findall(r'code="([a-z_]+)"', source)
    (code,) = codes
    return code


def test_every_public_fact_is_a_field_of_a_public_input() -> None:
    """``CalculationIssue.fact`` names the public field the caller sets."""
    for fact, path in PUBLIC_FACTS.items():
        owner, field = path.split(".")
        cls = getattr(ccnl_engine, owner)
        assert field == fact, path
        assert field in {f.name for f in dataclasses.fields(cls)}, path
