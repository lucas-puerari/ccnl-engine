"""Scope and limitations tests: result status, scope items."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.contract.domain.identity import (
    CCNLCoverage,
    CoverageNote,
    CoverageStatus,
    NoteKind,
)
from ccnl_engine.engine.payroll.domain.payroll_result import (
    CalculationStatus,
    EligibilityStatus,
    ScopeItem,
    SourceQuality,
)
from ccnl_engine.engine.payroll.domain.quality import (
    LimitationIntegrationStatus,
    LimitationSeverity,
)
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from ccnl_engine.engine.payroll.service.scope import (
    _limitations_scope,
    ccnl_notes_to_limitations,
    compute_result_status,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_DEFAULT_CCNL = _build_ccnl()

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[YearRules] = [_RULES]
_mock_surtax: list[SurtaxRules | None] = [None]


class _MockRepo:
    """KnowledgeRepository stub for the autouse _reset_mock_state fixture."""

    def load_ccnl(self, filename: str) -> CCNL:
        return _mock_ccnl[0]

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        return _mock_rules[0]

    def load_surtax_rules(self, year: int) -> SurtaxRules | None:
        return _mock_surtax[0]

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:
        return CapabilityCatalog(year=year, capabilities=())


_REPO = _MockRepo()


@pytest.fixture(autouse=True)
def _reset_mock_state() -> None:
    """Reset mutable mock state before each test."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    _mock_surtax[:] = [None]


def _scope_computed(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        gross_integrated=True,
        contribution_integrated=True,
        tax_integrated=True,
        net_integrated=True,
        cost_integrated=True,
        eligibility_status=EligibilityStatus.ENGINE_VERIFIED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
    )


def _scope_excluded(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.EXCLUDED,
        eligibility_status=EligibilityStatus.N_A,
        source_quality=SourceQuality.N_A,
    )


def _scope_not_computed(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.NOT_COMPUTED,
        eligibility_status=EligibilityStatus.N_A,
        source_quality=SourceQuality.N_A,
    )


def _scope_informational(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        eligibility_status=EligibilityStatus.ENGINE_VERIFIED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
    )


def _scope_caller_declared(feature: str) -> ScopeItem:
    return ScopeItem(
        feature=feature,
        calculation_status=CalculationStatus.COMPUTED,
        gross_integrated=True,
        contribution_integrated=True,
        tax_integrated=True,
        net_integrated=True,
        cost_integrated=True,
        eligibility_status=EligibilityStatus.CALLER_DECLARED,
        source_quality=SourceQuality.VERIFIED_PRIMARY,
    )


class TestComputeResultStatus:
    """Unit tests for compute_result_status helper."""

    def test_all_computed_returns_complete(self) -> None:
        """All computed scope items -> complete."""
        scope = (
            _scope_computed("base_salary"),
            _scope_computed("irpef"),
        )
        assert compute_result_status(scope) == "complete"

    def test_excluded_items_do_not_block_complete(self) -> None:
        """Excluded items are acceptable; result is still complete."""
        scope = (
            _scope_computed("base_salary"),
            _scope_excluded("overtime"),
        )
        assert compute_result_status(scope) == "complete"

    def test_not_computed_returns_partial(self) -> None:
        """A single not_computed item forces partial status."""
        scope = (
            _scope_computed("base_salary"),
            _scope_not_computed("overtime"),
        )
        assert compute_result_status(scope) == "partial"

    def test_informational_only_returns_partial(self) -> None:
        """Informational scope item (no integration axes) forces partial status."""
        scope = (
            _scope_computed("base_salary"),
            _scope_informational("fringe_benefit"),
        )
        assert compute_result_status(scope) == "partial"

    def test_caller_declared_returns_partial(self) -> None:
        """caller_declared eligibility_status forces partial status."""
        scope = (
            _scope_computed("base_salary"),
            _scope_caller_declared("family_deductions"),
        )
        assert compute_result_status(scope) == "partial"

    def test_empty_scope_returns_complete(self) -> None:
        """Empty scope (no items) -> complete (no blocked requests)."""
        assert compute_result_status(()) == "complete"

    def test_compute_sets_status_on_result(self) -> None:
        """compute() populates status='complete' for a basic scenario."""
        result = estimate_annual(_req(), repo=_REPO).result
        assert result.coverage.status in {"complete", "partial"}

    def test_compute_status_is_complete_without_work_rules_input(self) -> None:
        """No L3 inputs and L3 schema present -> complete (all excluded)."""
        result = estimate_annual(_req(), repo=_REPO).result
        assert result.coverage.status == "complete"


def _coverage(
    *notes: CoverageNote,
    gross: CoverageStatus = CoverageStatus.IMPLEMENTED,
    net: CoverageStatus = CoverageStatus.IMPLEMENTED,
) -> CCNLCoverage:
    return CCNLCoverage(gross=gross, net=net, notes=notes)


class TestLimitationsScope:
    """Unit tests for _limitations_scope helper."""

    def test_none_coverage_returns_empty(self) -> None:
        """None coverage -> no scope items added."""
        assert _limitations_scope(None) == []

    def test_no_applicable_notes_returns_empty(self) -> None:
        """Coverage with only info/source notes -> no scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="hourly divisor confirmed"),
            CoverageNote(kind=NoteKind.SOURCE, text="source: official PDF"),
        )
        assert _limitations_scope(cov) == []

    def test_simplification_note_returns_scope_item(self) -> None:
        """Coverage with a simplification note -> informational scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.SIMPLIFICATION, text="hourly rate approx")
        )
        result = _limitations_scope(cov)
        assert len(result) == 1
        assert result[0].feature == "ccnl_limitations"
        assert result[0].calculation_status == CalculationStatus.COMPUTED
        assert not any([
            result[0].gross_integrated,
            result[0].contribution_integrated,
            result[0].tax_integrated,
            result[0].net_integrated,
            result[0].cost_integrated,
        ])

    def test_missing_note_returns_scope_item(self) -> None:
        """Coverage with a missing note -> informational_only scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="info"),
            CoverageNote(kind=NoteKind.MISSING, text="overtime data absent"),
            gross=CoverageStatus.PARTIAL,
        )
        result = _limitations_scope(cov)
        assert len(result) == 1
        assert result[0].feature == "ccnl_limitations"

    def test_limitations_force_partial_status(self) -> None:
        """compute_result_status with ccnl_limitations item -> partial."""
        cov = _coverage(CoverageNote(kind=NoteKind.SIMPLIFICATION, text="approx"))
        scope = (
            _scope_computed("base_salary"),
            _scope_computed("irpef"),
            *_limitations_scope(cov),
        )
        assert compute_result_status(scope) == "partial"


class TestCcnlNotesToLimitations:
    """Unit tests for ccnl_notes_to_limitations."""

    def test_none_returns_empty(self) -> None:
        """None coverage returns an empty tuple."""
        assert ccnl_notes_to_limitations(None) == ()

    def test_no_applicable_notes_returns_empty(self) -> None:
        """Coverage with only info/source notes returns no limitations."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="info text"),
            CoverageNote(kind=NoteKind.SOURCE, text="source text"),
        )
        assert ccnl_notes_to_limitations(cov) == ()

    def test_simplification_note_yields_medium_severity(self) -> None:
        """A simplification note produces a MEDIUM severity limitation."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.SIMPLIFICATION, text="hourly rate approx")
        )
        lims = ccnl_notes_to_limitations(cov)
        assert len(lims) == 1
        assert lims[0].severity == LimitationSeverity.MEDIUM
        assert lims[0].integration_status == LimitationIntegrationStatus.NOT_INTEGRATED
        assert lims[0].remediation == "hourly rate approx"

    def test_missing_note_yields_high_severity(self) -> None:
        """A missing note produces a HIGH severity limitation."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.MISSING, text="overtime data absent"),
            gross=CoverageStatus.PARTIAL,
        )
        lims = ccnl_notes_to_limitations(cov)
        assert len(lims) == 1
        assert lims[0].severity == LimitationSeverity.HIGH

    def test_multiple_notes_produces_one_limitation_per_applicable_note(self) -> None:
        """Mixed notes: only simplification/missing produce limitations."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="info"),
            CoverageNote(kind=NoteKind.SIMPLIFICATION, text="simp1"),
            CoverageNote(kind=NoteKind.MISSING, text="miss1"),
            CoverageNote(kind=NoteKind.SOURCE, text="src"),
            gross=CoverageStatus.PARTIAL,
        )
        lims = ccnl_notes_to_limitations(cov)
        assert len(lims) == 2
        codes = {lim.code for lim in lims}
        assert "simplification_1" in codes
        assert "missing_2" in codes

    def test_limitation_fields(self) -> None:
        """Produced limitations have expected default fields."""
        cov = _coverage(CoverageNote(kind=NoteKind.SIMPLIFICATION, text="desc"))
        lim = ccnl_notes_to_limitations(cov)[0]
        assert lim.affected_component == "general"
        assert lim.applicability_predicate == "always"
        assert lim.impact_axis == ()
        assert lim.source == "CCNL coverage note"
