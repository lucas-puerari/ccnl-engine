"""Scope, limitations, and confidence tests: result status, scope items."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    CCNLWorkRules,
    SicknessRules,
    TaxSector,
)
from ccnl_engine.engine.contract.domain.identity import (
    CCNLCoverage,
    CoverageNote,
    CoverageStatus,
    NoteKind,
)
from ccnl_engine.engine.metadata.domain.rules import (
    RulesetIdentity,
    SourceType,
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
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
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    FringeBenefitInput,
    SickInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.scope import (
    _limitations_scope,
    ccnl_notes_to_limitations,
    compute_confidence,
    compute_result_status,
)
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import (
    ExtractionMethod,
    ExtractionTrace,
)
from ccnl_engine.engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates
from ccnl_engine.engine.tax.domain.variable_pay import (
    FringeBenefitRules,
    PdRRules,
    VariablePayRules,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_art15_deduction_rules,
    load_family_deduction_rules,
)
from tests.helpers import (
    TEST_RULESET_VERIFIED,
    make_ccnl_dict,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.surtax.domain.rules import (
        SurtaxRules,
    )
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules as SurtaxRulesT
    from ccnl_engine.engine.tax.domain.art15 import Art15DeductionRules
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules
_TEST_TAX_PERIOD = TaxPeriod(
    start=_DATE,
    end=date(2026, 12, 31),
    eligible_work_days=(date(2026, 12, 31) - _DATE).days + 1,
)


def compute(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput | None = None,
) -> Calculation:
    """Route to estimate_period_effects or estimate_annual.

    When calling with a period that has no tax_period set, a test-default
    TaxPeriod covering the remainder of 2026 from _DATE is injected.

    Returns:
        Calculation from the appropriate estimator.
    """
    if period is not None:
        if period.tax_period is None:
            period = period.model_copy(update={"tax_period": _TEST_TAX_PERIOD})
        return estimate_period_effects(scenario, period, repo=_REPO)
    return estimate_annual(scenario, repo=_REPO)


_DEFAULT_CCNL = _build_ccnl()
_DEFAULT_CCNL_UC = _build_ccnl("under_classification")

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[YearRules] = [_RULES]
_mock_surtax: list[SurtaxRulesT | None] = [None]


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


def _rule_provenance(tag: str) -> RuleProvenance:
    """Build a RuleProvenance with a distinguishing document/section identity.

    Returns:
        A :class:`RuleProvenance` uniquely identified by ``tag``.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id=f"doc-{tag}",
                title=f"Document {tag}",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
            ),
            section=f"Tabella {tag}",
        ),
        extraction=ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            verification_status=VerificationStatus.UNVERIFIED,
            effective_from=date(2025, 1, 1),
        ),
        note=tag,
    )


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
        """All computed scope items → complete."""
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
        """Empty scope (no items) → complete (no blocked requests)."""
        assert compute_result_status(()) == "complete"

    def test_compute_sets_status_on_result(self) -> None:
        """compute() populates status='complete' for a basic scenario."""
        result = estimate_annual(_req(), repo=_REPO).result
        assert result.coverage.status in {"complete", "partial"}

    def test_compute_status_is_complete_without_work_rules_input(self) -> None:
        """No L3 inputs and L3 schema present → complete (all excluded)."""
        result = estimate_annual(_req(), repo=_REPO).result
        # No overtime/leave/sick input: all L3 scope items are 'excluded'.
        # All L1/L2 items are 'computed'. Mock CCNL has no simplification
        # notes, so ccnl_limitations is not injected.
        assert result.coverage.status == "complete"


def _coverage(
    *notes: CoverageNote,
    gross: CoverageStatus = CoverageStatus.IMPLEMENTED,
    net: CoverageStatus = CoverageStatus.IMPLEMENTED,
) -> CCNLCoverage:
    """Build a CCNLCoverage with the given notes for _limitations_scope tests.

    Returns:
        A :class:`CCNLCoverage` for unit-testing _limitations_scope.
    """
    return CCNLCoverage(gross=gross, net=net, notes=notes)


class TestLimitationsScope:
    """Unit tests for _limitations_scope helper."""

    def test_none_coverage_returns_empty(self) -> None:
        """None coverage → no scope items added."""
        assert _limitations_scope(None) == []

    def test_no_applicable_notes_returns_empty(self) -> None:
        """Coverage with only info/source notes → no scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="hourly divisor confirmed"),
            CoverageNote(kind=NoteKind.SOURCE, text="source: official PDF"),
        )
        assert _limitations_scope(cov) == []

    def test_simplification_note_returns_scope_item(self) -> None:
        """Coverage with a simplification note → informational scope item."""
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
        """Coverage with a missing note → informational_only scope item."""
        cov = _coverage(
            CoverageNote(kind=NoteKind.INFO, text="info"),
            CoverageNote(kind=NoteKind.MISSING, text="overtime data absent"),
            gross=CoverageStatus.PARTIAL,
        )
        result = _limitations_scope(cov)
        assert len(result) == 1
        assert result[0].feature == "ccnl_limitations"

    def test_limitations_force_partial_status(self) -> None:
        """compute_result_status with ccnl_limitations item → partial."""
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


def _verified_provenance() -> RuleProvenance:
    """Build a TABELLA_RETRIBUTIVA provenance with VERIFIED status.

    Returns:
        A :class:`RuleProvenance` with verification_status=VERIFIED.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id="doc-verified",
                title="Tabella verificata",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
            ),
            section="Art. 1",
        ),
        extraction=ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            verification_status=VerificationStatus.VERIFIED,
            effective_from=date(2025, 1, 1),
        ),
    )


class TestComputeConfidence:
    """Unit tests for compute_confidence helper."""

    def test_warnings_always_returns_low(self) -> None:
        """Any warning → low, regardless of status or provenance."""
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", ("overtime not modelled",), prov)
        assert result == "low"

    def test_warnings_override_complete_status(self) -> None:
        """Complete status + verified provenance does not rescue from low."""
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", ("a warning",), prov)
        assert result == "low"

    def test_complete_verified_returns_high(self) -> None:
        """Complete + no warnings + all provenance verified → high."""
        prov = (_verified_provenance(),)
        assert compute_confidence("complete", (), prov) == "high"

    def test_partial_status_returns_medium(self) -> None:
        """Partial status with verified provenance and no warnings → medium."""
        prov = (_verified_provenance(),)
        assert compute_confidence("partial", (), prov) == "medium"

    def test_unverified_salary_table_returns_medium(self) -> None:
        """UNVERIFIED TABELLA_RETRIBUTIVA blocks high confidence."""
        unverified = _rule_provenance("unverified")  # uses UNVERIFIED by default
        assert compute_confidence("complete", (), (unverified,)) == "medium"

    def test_needs_review_salary_table_returns_medium(self) -> None:
        """NEEDS_REVIEW status is treated as non-verified → medium."""
        needs_review = RuleProvenance(
            location=SourceLocation(
                source_document=SourceDocument(
                    document_id="doc-nr",
                    title="Da rivedere",
                    kind=SourceKind.TABELLA_RETRIBUTIVA,
                    url="https://example.com",
                ),
                section="Art. 1",
            ),
            extraction=ExtractionTrace(
                method=ExtractionMethod.MANUAL,
                extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                verification_status=VerificationStatus.NEEDS_REVIEW,
                effective_from=date(2025, 1, 1),
            ),
        )
        assert compute_confidence("complete", (), (needs_review,)) == "medium"

    def test_non_salary_table_unverified_lowers_confidence(self) -> None:
        """Any unverified source, regardless of kind, blocks high confidence."""
        rivista = RuleProvenance(
            location=SourceLocation(
                source_document=SourceDocument(
                    document_id="doc-rivista",
                    title="Rivista non verificata",
                    kind=SourceKind.RIVISTA,
                    url="https://example.com",
                ),
                section="pag. 12",
            ),
            extraction=ExtractionTrace(
                method=ExtractionMethod.MANUAL,
                extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                verification_status=VerificationStatus.UNVERIFIED,
                effective_from=date(2025, 1, 1),
            ),
        )
        assert compute_confidence("complete", (), (rivista,)) == "medium"

    def test_empty_provenance_complete_returns_high(self) -> None:
        """No provenance records + complete + no warnings → high."""
        assert compute_confidence("complete", (), ()) == "high"

    def test_unverified_ruleset_returns_medium(self) -> None:
        """An unverified consumed ruleset blocks high confidence."""
        unverified_ruleset = RulesetIdentity(
            id="inps/2026/terziario",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="a" * 64,
            verification_status=VerificationStatus.UNVERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence(
            "complete", (), prov, rulesets=(unverified_ruleset,)
        )
        assert result == "medium"

    def test_verified_ruleset_does_not_block_high(self) -> None:
        """A verified consumed ruleset does not block high confidence."""
        verified_ruleset = RulesetIdentity(
            id="inps/2026/industria",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="https://example.com",
            source_type=SourceType.OFFICIAL_PRIMARY,
            source_hash="b" * 64,
            verification_status=VerificationStatus.VERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(verified_ruleset,))
        assert result == "high"

    def test_derived_unverified_ruleset_blocks_high(self) -> None:
        """Unverified derived-source ruleset cannot produce high confidence."""
        derived_ruleset = RulesetIdentity(
            id="ccnl/test-derived",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.DERIVED,
            source_hash="f" * 64,
            verification_status=VerificationStatus.UNVERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(derived_ruleset,))
        assert result == "medium"

    def test_estimated_unverified_ruleset_blocks_high(self) -> None:
        """Unverified estimated-source ruleset cannot produce high confidence."""
        estimated_ruleset = RulesetIdentity(
            id="ccnl/test-estimated",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.ESTIMATED,
            source_hash="f" * 64,
            verification_status=VerificationStatus.UNVERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(estimated_ruleset,))
        assert result == "medium"

    def test_derived_verified_ruleset_allows_high(self) -> None:
        """Derived source with explicit verification does not block high."""
        derived_verified = RulesetIdentity(
            id="ccnl/test-derived-verified",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_at=date(2026, 1, 1),
            source="unavailable",
            source_type=SourceType.DERIVED,
            source_hash="f" * 64,
            verification_status=VerificationStatus.VERIFIED,
        )
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(derived_verified,))
        assert result == "high"

    def test_compute_result_has_confidence_field(self) -> None:
        """compute() populates confidence on the result."""
        result = estimate_annual(_req(), repo=_REPO).result
        assert result.coverage.confidence in {"low", "medium", "high"}


# ---------------------------------------------------------------------------
# Confidence: optional rulesets (N09)
# ---------------------------------------------------------------------------

_VERIFIED_PROV: dict[str, object] = {
    "location": {
        "source_document": {
            "document_id": "test-doc-verified",
            "title": "Verified Source",
            "kind": "tabella_retributiva",
            "url": "https://example.com",
        },
        "section": "Art. 1",
    },
    "extraction": {
        "method": "manual",
        "extraction_timestamp": "2026-01-01T00:00:00",
        "verification_status": "verified",
        "effective_from": "2020-01-01",
    },
}


def _verified_level(code: str, order: int, salary: str) -> dict[str, object]:
    period = {
        "valid_from": "2020-01-01",
        "valid_until": None,
        "value": salary,
        "provenance": _VERIFIED_PROV,
    }
    return {
        "code": code,
        "order": order,
        "description": f"Level {code}",
        "base_salary": {"periods": [period]},
        "fixed_allowances": [],
        "provenance": _VERIFIED_PROV,
    }


def _verified_ccnl() -> CCNL:
    """Minimal CCNL where all provenance AND the ruleset block are VERIFIED.

    Returns:
        A validated CCNL instance with fully verified salary provenance and
        a verified ruleset identity block.
    """
    raw = make_ccnl_dict()
    raw["levels"] = [
        _verified_level("2", 2, "600.00"),
        _verified_level("3", 3, "800.00"),
        _verified_level("4", 4, "1000.00"),
    ]
    raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
    raw["ruleset"] = TEST_RULESET_VERIFIED
    return CCNL.model_validate(raw)


def _var_pay_rules(status: VerificationStatus) -> VariablePayRules:
    """Build a VariablePayRules with a RulesetIdentity of the given status.

    Returns:
        A VariablePayRules instance with minimal fringe-benefit and PdR rules.
    """
    ruleset = RulesetIdentity(
        id="tax/variable-pay-rules/2026",
        version="2026.1",
        effective_from=date(2026, 1, 1),
        published_at=date(2026, 1, 1),
        source="https://example.com",
        source_type=SourceType.OFFICIAL_PRIMARY,
        source_hash="c" * 64,
        verification_status=status,
    )
    fb = FringeBenefitRules(
        threshold_standard=_D("1000"),
        threshold_with_children=_D("2000"),
    )
    pdr = PdRRules(
        max_amount=_D("5000"),
        flat_tax_rate=_D("0.05"),
        income_ceiling=_D("80000"),
    )
    return VariablePayRules(year=2026, fringe_benefit=fb, pdr=pdr, ruleset=ruleset)


_FB_INPUT = FringeBenefitInput(annual_amount=_D("500"))


class TestConfidenceWithOptionalRulesets:
    """Unverified optional rulesets downgrade confidence from high to medium."""

    def test_verified_var_pay_ruleset_does_not_downgrade_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Verified var-pay ruleset + fringe_benefit → medium (informational).

        fringe_benefit is informational (no integration axes), so
        result.coverage.status is "partial" even when all provenance and
        rulesets are verified. Confidence reaches "medium", not "high".
        """
        _mock_ccnl[0] = _verified_ccnl()
        verified = _var_pay_rules(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules_variable_pay.load_variable_pay_rules",
            lambda _: verified,
        )
        result = compute(_req(), PeriodPayrollInput(fringe_benefit_input=_FB_INPUT))
        assert result.result.coverage.confidence == "medium"

    def test_unverified_var_pay_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unverified var-pay ruleset drops confidence to medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _var_pay_rules(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules_variable_pay.load_variable_pay_rules",
            lambda _: unverified,
        )
        result = compute(_req(), PeriodPayrollInput(fringe_benefit_input=_FB_INPUT))
        assert result.result.coverage.confidence == "medium"

    def test_ccnl_without_ruleset_limits_confidence_to_medium(self) -> None:
        """Verified CCNL provenance but absent ruleset block → at most medium.

        A missing ruleset identity is treated as "consumed but unverified",
        so confidence cannot reach "high" even when all salary provenance is
        verified.
        """
        raw = make_ccnl_dict()
        raw["levels"] = [
            _verified_level("2", 2, "600.00"),
            _verified_level("3", 3, "800.00"),
            _verified_level("4", 4, "1000.00"),
        ]
        raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
        # Intentionally no "ruleset" key → ccnl.ruleset = None
        _mock_ccnl[0] = CCNL.model_validate(raw)
        result = estimate_annual(_req(), repo=_REPO)
        assert result.result.coverage.confidence == "medium"

    def test_unverified_ccnl_ruleset_downgrades_confidence(self) -> None:
        """Unverified CCNL ruleset → confidence medium."""
        ruleset_block = {
            "id": "ccnl/test",
            "version": "2026.1",
            "effective_from": "2026-01-01",
            "effective_until": None,
            "published_at": "2026-01-01",
            "source": "https://example.com",
            "source_type": "commercial_secondary",
            "source_hash": "d" * 64,
            "verification_status": "unverified",
        }
        raw = make_ccnl_dict()
        raw["levels"] = [
            _verified_level("2", 2, "600.00"),
            _verified_level("3", 3, "800.00"),
            _verified_level("4", 4, "1000.00"),
        ]
        raw["parameters"]["seniority_increments"]["provenance"] = _VERIFIED_PROV
        raw["ruleset"] = ruleset_block
        _mock_ccnl[0] = CCNL.model_validate(raw)
        result = estimate_annual(_req(), repo=_REPO)
        assert result.result.coverage.confidence == "medium"

    def test_sick_pay_rates_without_ruleset_not_added_to_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """InpsSickPayRates with ruleset=None: sick_pay absent from ruleset_ids."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    sickness_rules=SicknessRules(
                        carenza_integration_rate=_D("1"),
                        full_pay_integration_rate=_D("1"),
                    )
                )
            }
        )
        rates_no_ruleset = InpsSickPayRates(carenza_days=3, bands=[])
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules.load_sick_pay_rates",
            lambda: rates_no_ruleset,
        )
        period = PeriodPayrollInput(sick_input=SickInput(sick_days=_D("3")))
        calc = compute(_req(), period)
        assert "sick_pay" in calc.ruleset_version

    def test_var_pay_rules_without_ruleset_not_added_to_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """VariablePayRules with ruleset=None: variable_pay absent from ruleset_ids."""
        rules_no_ruleset = VariablePayRules(
            year=2026,
            fringe_benefit=FringeBenefitRules(
                threshold_standard=_D("1000"),
                threshold_with_children=_D("2000"),
            ),
            pdr=PdRRules(
                max_amount=_D("5000"),
                flat_tax_rate=_D("0.05"),
                income_ceiling=_D("80000"),
            ),
            ruleset=None,
        )
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules_variable_pay.load_variable_pay_rules",
            lambda _: rules_no_ruleset,
        )
        period = PeriodPayrollInput(fringe_benefit_input=_FB_INPUT)
        calc = compute(_req(), period)
        assert "variable_pay" in calc.ruleset_version


# ---------------------------------------------------------------------------
# Confidence: family and Art. 15 rulesets (N09 residue)
# ---------------------------------------------------------------------------


def _make_ruleset(suffix: str, status: VerificationStatus) -> RulesetIdentity:
    """Return a minimal RulesetIdentity for testing.

    Returns:
        A :class:`RulesetIdentity` with ``id`` suffixed by *suffix*.
    """
    return RulesetIdentity(
        id=f"tax/{suffix}/2026",
        version="2026.1",
        effective_from=date(2026, 1, 1),
        published_at=date(2026, 1, 1),
        source="https://example.com",
        source_type=SourceType.OFFICIAL_PRIMARY,
        source_hash="e" * 64,
        verification_status=status,
    )


def _family_rules_with_status(status: VerificationStatus) -> FamilyDeductionRules:
    """Return real family rules with *status* stamped on the ruleset.

    Returns:
        Real 2026 :class:`FamilyDeductionRules` with a synthetic identity.
    """
    base = load_family_deduction_rules(2026)
    return base.model_copy(
        update={"ruleset": _make_ruleset("family-deductions", status)}
    )


def _art15_rules_with_status(status: VerificationStatus) -> Art15DeductionRules:
    """Return real Art. 15 rules with *status* stamped on the ruleset.

    Returns:
        Real 2026 :class:`Art15DeductionRules` with a synthetic identity.
    """
    base = load_art15_deduction_rules(2026)
    return base.model_copy(
        update={"ruleset": _make_ruleset("art15-deductions", status)}
    )


_SPOUSE_DEP = Dependent(relationship=DependentRelationship.SPOUSE)
_CHILD_DEP = Dependent(
    relationship=DependentRelationship.CHILD, birth_date=date(2000, 1, 1)
)
_FAMILY_INPUT = FamilyComposition(dependents=(_SPOUSE_DEP,))
_ART15_INPUT = Art15Deductions(mortgage_interest=_D("4000"))


class TestConfidenceFamilyArt15:
    """N09 residue: family and Art. 15 rulesets participate in confidence.

    Each test uses a CCNL with fully verified provenance so that the only
    driver of confidence is the optional-feature ruleset identity.  The base
    YearRules have no ruleset block (``ruleset=None``, filtered from the
    consumed set), so they do not interfere.
    """

    def test_family_without_ruleset_downgrades_confidence(self) -> None:
        """Family deductions with missing ruleset identity → medium.

        The bundled family-deductions-2026.json carries a partial ruleset
        block (no verification_status).  _try_ruleset() returns None, which
        is treated as an unverified consumed source.
        """
        _mock_ccnl[0] = _verified_ccnl()
        result = estimate_annual(
            _req().model_copy(update={"family": _FAMILY_INPUT}), repo=_REPO
        )
        assert result.result.coverage.confidence == "medium"

    def test_family_with_verified_ruleset_still_medium(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Family deductions scope is caller_declared even with a verified ruleset.

        The engine cannot verify dependent eligibility (residency, disability
        certification, own income), so family_deductions is always
        ``"caller_declared"`` → result status is ``"partial"`` → confidence
        ``"medium"`` regardless of ruleset verification.
        """
        _mock_ccnl[0] = _verified_ccnl()
        verified = _family_rules_with_status(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_family_deduction_rules",
            lambda _: verified,
        )
        result = estimate_annual(
            _req().model_copy(update={"family": _FAMILY_INPUT}), repo=_REPO
        )
        assert result.result.coverage.confidence == "medium"

    def test_family_with_unverified_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Family deductions with an unverified ruleset → medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _family_rules_with_status(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_family_deduction_rules",
            lambda _: unverified,
        )
        result = estimate_annual(
            _req().model_copy(update={"family": _FAMILY_INPUT}), repo=_REPO
        )
        assert result.result.coverage.confidence == "medium"

    def test_art15_without_ruleset_downgrades_confidence(self) -> None:
        """Art. 15 deductions with no ruleset block in JSON → medium.

        art15-deductions-2026.json has no ruleset block at all; _try_ruleset()
        returns None, treated as an unverified consumed source.
        """
        _mock_ccnl[0] = _verified_ccnl()
        result = estimate_annual(
            _req().model_copy(update={"art15_deductions": _ART15_INPUT}), repo=_REPO
        )
        assert result.result.coverage.confidence == "medium"

    def test_art15_with_verified_ruleset_stays_medium(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Art. 15 deductions with a verified ruleset + verified CCNL → medium.

        art15_deductions is always calculation_status=partial (simplified model),
        so result.coverage.status is "partial" and confidence tops out at "medium".  A
        verified ruleset does not degrade confidence further.
        """
        _mock_ccnl[0] = _verified_ccnl()
        verified = _art15_rules_with_status(VerificationStatus.VERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_art15_deduction_rules",
            lambda _: verified,
        )
        result = estimate_annual(
            _req().model_copy(update={"art15_deductions": _ART15_INPUT}), repo=_REPO
        )
        assert result.result.coverage.confidence == "medium"

    def test_art15_with_unverified_ruleset_downgrades_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Art. 15 deductions with an unverified ruleset → medium."""
        _mock_ccnl[0] = _verified_ccnl()
        unverified = _art15_rules_with_status(VerificationStatus.UNVERIFIED)
        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.fiscal_deductions.load_art15_deduction_rules",
            lambda _: unverified,
        )
        result = estimate_annual(
            _req().model_copy(update={"art15_deductions": _ART15_INPUT}), repo=_REPO
        )
        assert result.result.coverage.confidence == "medium"

    def test_no_optional_features_confidence_unaffected(self) -> None:
        """No family or Art. 15 inputs: consumed_ruleset_ids stays empty."""
        _mock_ccnl[0] = _verified_ccnl()
        result = estimate_annual(_req(), repo=_REPO)
        assert result.result.coverage.confidence == "high"

    def test_none_ruleset_in_compute_confidence_is_unverified(self) -> None:
        """compute_confidence treats None ruleset entries as unverified."""
        prov = (_verified_provenance(),)
        result = compute_confidence("complete", (), prov, rulesets=(None,))
        assert result == "medium"


# ---------------------------------------------------------------------------
# Bilateral funds (feat/bilateral-funds)
# ---------------------------------------------------------------------------
