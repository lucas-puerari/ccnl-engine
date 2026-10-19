"""Assessment of a run: axes, blockers and payability from what it recorded."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.assurance.models import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
    ResultTotal,
)
from ccnl_engine.assurance.policies import EngineMode
from ccnl_engine.assurance.rules import (
    assess,
    assess_nothing_computed,
)
from ccnl_engine.capability.registry.models import CapabilityImplementation
from ccnl_engine.capability.requirement.rules import UnresolvedRequirement
from ccnl_engine.capability.results import (
    CapabilityGap,
    CapabilityGapKind,
    CapabilityReport,
)
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.limitation.models import ModelLimitation, MonetaryImpact
from ccnl_engine.provenance.source.rule.models import ProvenanceStatus
from tests.unit.ccnl_engine.provenance.ruleset.builders import tax_ruleset

if TYPE_CHECKING:
    from collections.abc import Mapping

_SIMULATION = EngineMode.SIMULATION
_DERIVED = {"irpef": ProvenanceStatus.DERIVED}
_PROVISIONAL = CalculationStatus.PROVISIONAL
_INCOMPLETE_COVERAGE = CoverageStatus.INCOMPLETE


def _report(
    gaps: tuple[CapabilityGap, ...] = (),
    rule_sources: Mapping[str, ProvenanceStatus] = _DERIVED,
    caller_supplied: Mapping[str, tuple[str, ...]] | None = None,
) -> CapabilityReport:
    return CapabilityReport(
        catalog_year=2026,
        gaps=gaps,
        rule_sources=rule_sources,
        caller_supplied=caller_supplied or {},
    )


def _gap(feature: str, kind: CapabilityGapKind) -> CapabilityGap:
    return CapabilityGap(feature, CapabilityImplementation.NATIVE, "absent", kind)


def _decision(status: CalculationStatus) -> CalculationDecision:
    return CalculationDecision(
        capability="addizionale_comunale",
        status=status,
        reason_code="table_unknown",
        rule="surtax/2026/comunale",
        rule_version="2026.1",
    )


def _keys(assurance: ResultAssurance) -> list[tuple[BlockerCode, str | None, str]]:
    return [(b.code, b.feature, b.detail) for b in assurance.blockers]


class TestAssess:
    """Each recorded condition is one blocker; nothing else blocks."""

    def test_unresolved_requirement_blocks_its_capability(self) -> None:
        """A default never rules out a required capability: it blocks."""
        report = CapabilityReport(
            catalog_year=2026,
            gaps=(),
            rule_sources=_DERIVED,
            unresolved=(UnresolvedRequirement("addizionale_comunale", "facts.x"),),
        )

        assurance = assess((), (), report, (), _SIMULATION)

        (blocker,) = assurance.blockers
        assert (blocker.code, blocker.feature, blocker.detail) == (
            BlockerCode.REQUIREMENT_UNRESOLVED,
            "addizionale_comunale",
            "facts.x",
        )
        assert "facts.x was left to its default: supply facts.x" in (
            blocker.remediation
        )
        assert assurance.coverage is _INCOMPLETE_COVERAGE
        assert not assurance.is_payable

    def test_derived_rules_alone_are_payable(self) -> None:
        """A derived rule lowers the evidence axis but does not block."""
        assurance = assess((), (), _report(), (tax_ruleset("tax/2026"),), _SIMULATION)

        assert assurance.calculation is CalculationStatus.FINAL
        assert assurance.coverage is CoverageStatus.COMPLETE
        assert assurance.evidence is EvidenceStatus.DERIVED
        assert assurance.rulesets == (tax_ruleset("tax/2026"),)
        assert assurance.payability is Payability.PAYABLE
        assert assurance.is_payable
        assert assurance.blockers == ()

    def test_issue_blocks_with_its_code(self) -> None:
        """An issue blocks the run as a whole, whatever its status."""
        issue = CalculationIssue(
            "withholding_shortfall_unrecovered", "tax not withheld", _PROVISIONAL
        )

        assurance = assess((issue,), (), _report(), (), _SIMULATION)

        assert assurance.calculation is _PROVISIONAL
        assert _keys(assurance) == [
            (BlockerCode.CALCULATION_ISSUE, None, "withholding_shortfall_unrecovered")
        ]
        assert not assurance.is_payable

    def test_issue_with_a_fact_is_a_missing_fact(self) -> None:
        """An issue naming a fact becomes a missing-fact blocker on that fact."""
        issue = CalculationIssue(
            "rinnovo_eligibility_unknown",
            "sector unknown",
            _PROVISIONAL,
            fact="sector",
            capability="rinnovo_substitute_tax",
        )

        (blocker,) = assess((issue,), (), _report(), (), _SIMULATION).blockers

        assert (blocker.code, blocker.feature, blocker.detail) == (
            BlockerCode.MISSING_FACT,
            "rinnovo_substitute_tax",
            "sector",
        )
        assert blocker.remediation == "supply Employment.sector in the request"

    def test_non_final_decision_blocks_its_capability(self) -> None:
        """A decision that is not final blocks; a final one does not."""
        decisions = (
            _decision(CalculationStatus.FINAL),
            _decision(CalculationStatus.INCOMPLETE),
        )

        assurance = assess((), decisions, _report(), (), _SIMULATION)

        assert assurance.calculation is CalculationStatus.INCOMPLETE
        assert _keys(assurance) == [
            (BlockerCode.CALCULATION_ISSUE, "addizionale_comunale", "table_unknown")
        ]

    def test_every_gap_blocks_and_sets_the_coverage(self) -> None:
        """A partial gap gives partial coverage; each gap is a blocker."""
        partial = _gap("irpef", CapabilityGapKind.PARTIAL_RESULT)

        assurance = assess((), (), _report(gaps=(partial,)), (), _SIMULATION)

        assert assurance.coverage is CoverageStatus.PARTIAL
        assert _keys(assurance) == [
            (
                BlockerCode.CAPABILITY_NOT_COMPUTED,
                "irpef",
                "partial_result",
            )
        ]

    def test_assumed_and_missing_rules_block(self) -> None:
        """Only assumed and missing rules block; the weakest sets the axis."""
        sources = {
            "irpef": ProvenanceStatus.DERIVED,
            "base_salary": ProvenanceStatus.ASSUMED,
            "tfr": ProvenanceStatus.MISSING,
            "inps_employee": ProvenanceStatus.VERIFIED,
        }

        assurance = assess((), (), _report(rule_sources=sources), (), _SIMULATION)

        assert assurance.evidence is EvidenceStatus.MISSING
        assert _keys(assurance) == [
            (BlockerCode.RULE_SOURCE_WEAK, "base_salary", "assumed"),
            (BlockerCode.RULE_SOURCE_WEAK, "tfr", "missing"),
        ]

    def test_no_recorded_rule_is_missing_evidence(self) -> None:
        """A run whose rules carry no record cannot claim any evidence."""
        assurance = assess((), (), _report(rule_sources={}), (), _SIMULATION)

        (blocker,) = assurance.blockers
        assert assurance.evidence is EvidenceStatus.MISSING
        assert (blocker.code, blocker.feature, blocker.detail) == (
            BlockerCode.RULE_SOURCE_WEAK,
            None,
            "missing",
        )
        assert blocker.remediation.startswith("the run read a rule")

    def test_caller_supplied_rule_blocks_with_its_fields(self) -> None:
        """A value supplied in place of a rule has no source: it blocks."""
        report = _report(caller_supplied={"overtime": ("hourly_rate", "multiplier")})

        (blocker,) = assess((), (), report, (), _SIMULATION).blockers

        assert (blocker.code, blocker.feature, blocker.detail) == (
            BlockerCode.CALLER_SUPPLIED_RULE,
            "overtime",
            "hourly_rate,multiplier",
        )
        assert "overtime used caller values" in blocker.remediation


def test_caller_supplied_origin_is_not_a_decision_blocker() -> None:
    """A final caller-supplied decision blocks through the report only."""
    decision = CalculationDecision(
        capability="overtime",
        status=CalculationStatus.FINAL,
        reason_code="caller_supplied_rate",
        rule="caller",
        rule_version="request",
        origin=DecisionOrigin.CALLER_SUPPLIED,
    )

    assert assess((), (decision,), _report(), (), _SIMULATION).is_payable


def test_nothing_computed_is_never_payable() -> None:
    """No run read a rule; operational mode also finds no tracked readiness."""
    simulation = assess_nothing_computed(EngineMode.SIMULATION)
    operational = assess_nothing_computed(EngineMode.OPERATIONAL)

    assert simulation.evidence is EvidenceStatus.MISSING
    assert simulation.coverage is CoverageStatus.INCOMPLETE
    assert [b.code for b in simulation.blockers] == [BlockerCode.RULE_SOURCE_WEAK]
    assert [b.code for b in operational.blockers] == [
        BlockerCode.RULE_SOURCE_WEAK,
        BlockerCode.RULESET_NOT_PRODUCTION,
    ]
    assert not simulation.is_payable
    assert operational.mode is EngineMode.OPERATIONAL


def _fund(**overrides: object) -> ModelLimitation:
    fields: dict[str, object] = {
        "id": "ccnl-a/health_fund",
        "capability": "bilateral_funds",
        "variant": "health_fund",
        "summary": "the employer owes a health fund",
        "monetary_impact": MonetaryImpact.YES,
        "rulesets": ("ccnl-a",),
        "applies_when": {"trigger": "owed"},
        "totals": ["employer_cost"],
        "source": "ccnl/ccnl-a:coverage.notes",
        "remediation": "model it",
    }
    return ModelLimitation.model_validate(fields | overrides)


def test_an_open_limitation_blocks_only_the_totals_it_names() -> None:
    """An employer-only fund leaves the employer cost short, the net payable."""
    fund = _fund()

    assurance = assess((), (), _report(), (), _SIMULATION, (fund,))

    (blocker,) = assurance.blockers
    assert blocker == ResultBlocker(
        BlockerCode.OPEN_LIMITATION,
        "bilateral_funds",
        "ccnl-a/health_fund",
        "bilateral_funds is computed under the open limitation ccnl-a/health_fund: "
        "check the amount outside the engine or resolve the limitation",
        frozenset({ResultTotal.EMPLOYER_COST}),
    )
    assert assurance.limitations == (fund,)
    assert assurance.is_net_pay_payable
    assert not assurance.is_employer_cost_complete


def test_a_resolved_limitation_is_listed_without_blocking() -> None:
    """A limitation that no longer holds is reported, never a blocker."""
    fund = _fund(status="resolved")

    assurance = assess((), (), _report(), (), _SIMULATION, (fund,))

    assert assurance.limitations == (fund,)
    assert assurance.blockers == ()
    assert assurance.is_payable


def test_other_blockers_touch_both_totals() -> None:
    """A blocker that names no total leaves both unreliable."""
    report = _report(caller_supplied={"overtime": ("hourly_rate",)})

    (blocker,) = assess((), (), report, (), _SIMULATION).blockers

    assert blocker.totals == frozenset(ResultTotal)


def test_a_missing_fact_is_the_one_blocker_of_its_capability() -> None:
    """The decision and the gap that follow from a missing fact are not repeated."""
    issue = CalculationIssue(
        "comune_unknown",
        "comune unknown",
        _PROVISIONAL,
        fact="seniority",
        capability="addizionale_comunale",
    )
    gap = _gap("addizionale_comunale", CapabilityGapKind.PARTIAL_RESULT)

    assurance = assess(
        (issue,), (_decision(_PROVISIONAL),), _report((gap,)), (), _SIMULATION
    )

    assert _keys(assurance) == [
        (BlockerCode.MISSING_FACT, "addizionale_comunale", "seniority")
    ]


def test_an_issue_makes_the_gap_of_its_capability_redundant() -> None:
    """A non-final decision explains the gap of its capability; others stay."""
    gaps = (
        _gap("addizionale_comunale", CapabilityGapKind.PARTIAL_RESULT),
        _gap("irpef", CapabilityGapKind.PARTIAL_RESULT),
    )

    assurance = assess((), (_decision(_PROVISIONAL),), _report(gaps), (), _SIMULATION)

    assert _keys(assurance) == [
        (BlockerCode.CALCULATION_ISSUE, "addizionale_comunale", "table_unknown"),
        (BlockerCode.CAPABILITY_NOT_COMPUTED, "irpef", "partial_result"),
    ]
