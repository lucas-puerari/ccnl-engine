"""Scope and gaps of a run against the registry, and the report status."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ccnl_engine.payroll.domain.assurance import CoverageStatus, EvidenceStatus
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityApplicability,
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityHandler,
    CapabilityImplementation,
    CapabilityLayer,
)
from ccnl_engine.payroll.domain.capability_report import (
    CapabilityGap,
    CapabilityGapKind,
    CapabilityReport,
    CapabilityScope,
    CaseFacts,
    compare_with_catalog,
)
from ccnl_engine.provenance.source.models_chain import ProvenanceStatus

_APPLIES = CapabilityApplicability
_HANDLER = CapabilityHandler
_IMPL = CapabilityImplementation
_KIND = CapabilityGapKind
_SCOPE = CapabilityScope


def _entry(
    feature: str,
    applies_when: CapabilityApplicability,
    implementation: CapabilityImplementation = _IMPL.NATIVE,
) -> CapabilityEntry:
    handler = {
        _APPLIES.ALWAYS: _HANDLER.PIPELINE,
        _APPLIES.DECIDED: _HANDLER.DECISION,
        _APPLIES.EVENT: _HANDLER.EVENT,
    }.get(applies_when, _HANDLER.EVENT)
    return CapabilityEntry(
        feature,
        CapabilityLayer.NET,
        implementation,
        applies_when,
        None if implementation is _IMPL.UNSUPPORTED else handler,
    )


_CATALOG = CapabilityCatalog(
    2026,
    (
        _entry("irpef", _APPLIES.ALWAYS),
        _entry("seniority", _APPLIES.DECIDED),
        _entry("family_deductions", _APPLIES.DECIDED, _IMPL.PARTIAL),
        _entry("overtime", _APPLIES.EVENT, _IMPL.CALLER_SUPPLIED),
        _entry("residual_leave", _APPLIES.TERMINATION_RUN, _IMPL.UNSUPPORTED),
        _entry("inail", _APPLIES.OUTSIDE_INPUT, _IMPL.UNSUPPORTED),
    ),
)
_ORDINARY = {
    "irpef": "computed",
    "seniority": "not_applicable",
    "family_deductions": "not_applicable",
    "overtime": "skipped",
}


def _compare(
    observed: dict[str, str], case: CaseFacts | None = None, year: int = 2026
) -> tuple[dict[str, CapabilityGapKind], dict[str, CapabilityScope]]:
    gaps, scope = compare_with_catalog(
        _CATALOG, {**_ORDINARY, **observed}, case or CaseFacts(), year
    )
    return {g.feature: g.kind for g in gaps}, scope


class TestScope:
    """The predicate, the case and the trace decide the scope."""

    def test_ordinary_case(self) -> None:
        """Only the always-applicable stage applies; nothing is a gap."""
        gaps, scope = _compare({})
        assert gaps == {}
        assert scope == {
            "irpef": _SCOPE.APPLICABLE,
            "seniority": _SCOPE.NOT_APPLICABLE,
            "family_deductions": _SCOPE.NOT_APPLICABLE,
            "overtime": _SCOPE.NOT_APPLICABLE,
            "residual_leave": _SCOPE.NOT_APPLICABLE,
            "inail": _SCOPE.OUTSIDE_INPUT,
        }

    def test_handler_rules_out_an_always_stage(self) -> None:
        """An employer that does not withhold makes IRPEF not applicable."""
        _, scope = _compare({"irpef": "not_applicable"})
        assert scope["irpef"] is _SCOPE.NOT_APPLICABLE

    @pytest.mark.parametrize("state", ["skipped", None])
    def test_decided_without_decision(self, state: str | None) -> None:
        """A decision owner that took no decision leaves it out of scope."""
        observed = {k: v for k, v in _ORDINARY.items() if k != "seniority"}
        if state is not None:
            observed["seniority"] = state
        gaps, scope = compare_with_catalog(_CATALOG, observed, CaseFacts(), 2026)
        assert scope["seniority"] is _SCOPE.NOT_APPLICABLE
        assert gaps == ()

    def test_declared_event_applies(self) -> None:
        """An event of the capability makes it applicable, even without effect."""
        gaps, scope = _compare({}, CaseFacts(event_features=frozenset({"overtime"})))
        assert scope["overtime"] is _SCOPE.APPLICABLE
        assert gaps == {}

    def test_closing_run_needs_residual_leave(self) -> None:
        """An unsupported capability that applies is a gap."""
        gaps, scope = _compare({}, CaseFacts(closes_employment=True))
        assert scope["residual_leave"] is _SCOPE.APPLICABLE
        assert gaps == {"residual_leave": _KIND.UNSUPPORTED}


class TestGapKinds:
    """An applicable capability is classified by its trace."""

    @pytest.mark.parametrize(
        ("feature", "state", "kind"),
        [
            ("irpef", "unresolved", _KIND.UNRESOLVED),
            ("irpef", "partial", _KIND.PARTIAL_RESULT),
            ("family_deductions", "computed", _KIND.PARTIAL_IMPLEMENTATION),
            ("family_deductions", "partial", _KIND.PARTIAL_IMPLEMENTATION),
            ("family_deductions", "unresolved", _KIND.UNRESOLVED),
            ("seniority", "computed", None),
        ],
    )
    def test_kind(
        self, feature: str, state: str, kind: CapabilityGapKind | None
    ) -> None:
        """Unresolved, partial result and partial implementation are gaps."""
        gaps, _ = _compare({feature: state})
        assert gaps.get(feature) is kind

    def test_untraced_capability_is_unsupported(self) -> None:
        """A capability that applies but left no trace is not covered."""
        observed = {k: v for k, v in _ORDINARY.items() if k != "irpef"}
        (gap,) = compare_with_catalog(_CATALOG, observed, CaseFacts(), 2026)[0]
        assert gap == CapabilityGap("irpef", _IMPL.NATIVE, "absent", _KIND.UNSUPPORTED)

    def test_wrong_year_comes_first(self) -> None:
        """A catalog of another year is a gap of the whole run."""
        gaps, _ = compare_with_catalog(_CATALOG, _ORDINARY, CaseFacts(), 2025)
        assert gaps[0] == CapabilityGap(
            "__catalog__", _IMPL.NATIVE, "2025", _KIND.WRONG_YEAR
        )


def _gap(kind: CapabilityGapKind) -> CapabilityGap:
    return CapabilityGap("f", _IMPL.NATIVE, "computed", kind)


class TestReport:
    """The report status is the coverage axis of the assurance."""

    def test_empty_is_complete(self) -> None:
        """No gap is complete coverage."""
        report = CapabilityReport.empty(2026)
        assert report.catalog_year == 2026
        assert report.status is CoverageStatus.COMPLETE
        assert dict(report.scope) == {}

    @pytest.mark.parametrize(
        ("kinds", "status"),
        [
            ((_KIND.PARTIAL_RESULT,), CoverageStatus.PARTIAL),
            ((_KIND.PARTIAL_IMPLEMENTATION,), CoverageStatus.PARTIAL),
            ((_KIND.UNSUPPORTED,), CoverageStatus.INCOMPLETE),
            ((_KIND.PARTIAL_RESULT, _KIND.UNRESOLVED), CoverageStatus.INCOMPLETE),
        ],
    )
    def test_status(
        self, kinds: tuple[CapabilityGapKind, ...], status: CoverageStatus
    ) -> None:
        """Only partial gaps leave the coverage partial."""
        report = CapabilityReport(2026, tuple(_gap(k) for k in kinds))
        assert report.status is status

    def test_mappings_are_read_only(self) -> None:
        """The report does not share or expose mutable mappings."""
        scope = {"irpef": _SCOPE.APPLICABLE}
        report = CapabilityReport(2026, (), scope=scope)
        scope["irpef"] = _SCOPE.NOT_APPLICABLE
        assert report.scope["irpef"] is _SCOPE.APPLICABLE
        with pytest.raises(TypeError):
            report.scope["irpef"] = _SCOPE.APPLICABLE  # type: ignore[index]
        with pytest.raises(FrozenInstanceError):
            report.catalog_year = 2027  # type: ignore[misc]

    def test_weak_sources_follow_the_required_evidence(self) -> None:
        """Derived is accepted by default; a stricter capability rejects it."""
        report = CapabilityReport(
            2026,
            (),
            rule_sources={
                "irpef": ProvenanceStatus.DERIVED,
                "seniority": ProvenanceStatus.DERIVED,
                "somma_esente": ProvenanceStatus.ASSUMED,
            },
            evidence_required={"seniority": EvidenceStatus.VERIFIED},
        )
        assert report.weak_sources() == {
            "seniority": ProvenanceStatus.DERIVED,
            "somma_esente": ProvenanceStatus.ASSUMED,
        }
