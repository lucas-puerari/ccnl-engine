"""Contract tests for ccnl_engine's public API surface.

The public API is the package root plus four namespaces.  The root holds the
common path; every other public name lives in exactly one namespace.  These
tests guard each ``__all__`` against drift, keep the five modules disjoint
(one import path per name, no alias) and keep the public snippets on them.
"""

from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import re
import types
from pathlib import Path

import pytest

import ccnl_engine
from ccnl_engine import errors as errors_module
from ccnl_engine.errors import PUBLIC_ERROR_CODES, CcnlEngineError
from ccnl_engine.payroll.assurance.models_decision import PUBLIC_FACTS
from tests.architecture._imports import PUBLIC_NAMESPACES, ROOT_PACKAGE

_REPO = Path(__file__).parents[2]

EXPECTED_PUBLIC: dict[str, frozenset[str]] = {
    "ccnl_engine": frozenset({
        "CcnlEngineError",
        "CompetenceYearPlan",
        "CompetenceYearResult",
        "DataIntegrityError",
        "EmployerProfile",
        "Employment",
        "Headcount",
        "InvalidInputError",
        "MissingRequiredFactError",
        "MissingRuleError",
        "OutOfScopeError",
        "PayrollEngine",
        "PayrollRun",
        "PeriodFacts",
        "PeriodInput",
        "PeriodResult",
        "TaxYearPlan",
        "TaxYearResult",
        "UnknownCcnlError",
        "UnknownLevelError",
        "UnsupportedTaxYearError",
        "bundle_version",
        "engine_version",
    }),
    "ccnl_engine.inputs": frozenset({
        "Apprentice",
        "CalendarOverride",
        "CalendarOverrideReason",
        "ContributableHours",
        "ContributionHistory",
        "CurrentYearTaxFacts",
        "DeferredShortfall",
        "Dependent",
        "DependentRelationship",
        "EmployerActivity",
        "EmploymentPeriod",
        "EmploymentSector",
        "EmploymentSpell",
        "EngineMode",
        "FamilyComposition",
        "FixedTerm",
        "ForeignTaxPaid",
        "IncomeEstimateQuality",
        "InpsBaseYtd",
        "NaspiExclusion",
        "NoPensionFund",
        "OpeningBalances",
        "PaymentId",
        "PayrollRunId",
        "PensionFundEnrolment",
        "PeriodState",
        "Permanent",
        "PriorYearTaxFacts",
        "PublicEndOfService",
        "RecoveryObligation",
        "RecoveryPlan",
        "SeniorityFact",
        "SenioritySource",
        "ShortfallDeferralRequest",
        "SubstituteTaxRegime",
        "SurtaxComponent",
        "SurtaxObligation",
        "TfrFundBalance",
        "WeeklyHours",
        "WorkCalendar",
        "WorkerCategory",
        "period_state_from_json",
        "period_state_to_json",
    }),
    "ccnl_engine.events": frozenset({
        "AbsenceEvent",
        "ArrearsEvent",
        "BilateralFundEvent",
        "BonusEvent",
        "FringeEvent",
        "HolidayWorkEvent",
        "NightShiftEvent",
        "OvertimeEvent",
        "OvertimeKind",
        "PeriodId",
        "ShiftWorkEvent",
        "SickLeaveEvent",
        "SicknessEpisode",
        "TerminationTFREvent",
        "WelfareEvent",
        "WorkEvent",
    }),
    "ccnl_engine.results": frozenset({
        "AccountKind",
        "BlockerCode",
        "CalculationDecision",
        "CalculationIssue",
        "CalculationStatus",
        "CapabilityGap",
        "CapabilityScope",
        "CoverageStatus",
        "DecisionOrigin",
        "EvidenceStatus",
        "LimitationStatus",
        "ModelLimitation",
        "MonetaryImpact",
        "Payability",
        "RemittanceColumn",
        "RemittanceLine",
        "ResultAssurance",
        "ResultBlocker",
        "UncoveredRun",
        "UnresolvedRequirement",
    }),
    "ccnl_engine.catalog": frozenset({
        "CapabilityCatalog",
        "CapabilityEntry",
        "CapabilityImplementation",
        "CcnlId",
        "ContractSummary",
        "LevelSummary",
        "RulesetAssurance",
        "RulesetIdentity",
        "RulesetKind",
        "RulesetReadiness",
        "ValidityWindow",
        "VerificationStatus",
        "get_ccnl",
        "search_ccnls",
        "supported_tax_years",
    }),
}

#: Public snippets a caller copies: they import from the public API only.
_PUBLIC_SNIPPETS: tuple[Path, ...] = (
    _REPO / "README.md",
    _REPO / "scripts" / "quality" / "smoke_test.py",
    *sorted((_REPO / "docs" / "examples").rglob("*.py")),
)

_IMPORT = re.compile(r"^\s*(?:from|import)\s+(ccnl_engine(?:\.\w+)*)", re.MULTILINE)


def _module(name: str) -> types.ModuleType:
    return importlib.import_module(name)


def _public_owner(name: str) -> object:
    (owner,) = (
        getattr(_module(module), name)
        for module, names in EXPECTED_PUBLIC.items()
        if name in names
    )
    return owner


def test_public_modules_are_the_root_and_its_namespaces() -> None:
    """The expected surface covers the root and every public namespace."""
    assert set(EXPECTED_PUBLIC) == {ROOT_PACKAGE, *PUBLIC_NAMESPACES}


@pytest.mark.parametrize("module", sorted(EXPECTED_PUBLIC))
def test_all_exact(module: str) -> None:
    """Each ``__all__`` matches the expected set exactly."""
    assert set(_module(module).__all__) == EXPECTED_PUBLIC[module]


@pytest.mark.parametrize("module", sorted(EXPECTED_PUBLIC))
def test_all_names_resolve(module: str) -> None:
    """Every name in ``__all__`` is importable from its module."""
    namespace = _module(module)
    for name in namespace.__all__:
        assert hasattr(namespace, name), f"Missing from {module}: {name}"


@pytest.mark.parametrize("module", sorted(EXPECTED_PUBLIC))
def test_no_public_name_outside_all(module: str) -> None:
    """A public module exposes no other name: no alias of an old import.

    Submodules bound as attributes by the import system are not names.
    """
    namespace = _module(module)
    extra = {
        name
        for name, value in vars(namespace).items()
        if not name.startswith("_")
        and not isinstance(value, types.ModuleType)
        and name != "annotations"
    }
    assert extra <= set(namespace.__all__)


def test_public_modules_are_disjoint() -> None:
    """Each public name has one import path."""
    names = [name for names in EXPECTED_PUBLIC.values() for name in names]
    assert len(names) == len(set(names))


def test_root_stays_the_common_path() -> None:
    """The root stays a short list; anything else goes in a namespace."""
    assert len(ccnl_engine.__all__) <= 25


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
        cls = _public_owner(owner)
        assert dataclasses.is_dataclass(cls), path
        assert field == fact, path
        assert field in {f.name for f in dataclasses.fields(cls)}, path


def _imported_modules(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    if path.suffix == ".py":
        return {
            node.module
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith(ROOT_PACKAGE)
        }
    return set(_IMPORT.findall(source))


@pytest.mark.parametrize("path", _PUBLIC_SNIPPETS, ids=lambda p: p.name)
def test_public_snippets_import_the_public_api_only(path: Path) -> None:
    """README, examples and the wheel smoke test use no deep namespace."""
    assert _imported_modules(path) <= set(EXPECTED_PUBLIC), path
