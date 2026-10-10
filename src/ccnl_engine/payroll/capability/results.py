"""Capability report of one run: scope and gaps against the registry.

For every capability of the :class:`~ccnl_engine.payroll.capability\
.models_catalog.CapabilityCatalog` the run decides its scope from the
applicability predicate, the facts of the case and the trace of the
capability.  Only an applicable capability can leave a gap:

- an unsupported capability (or one the run did not trace) is not covered;
- a traced capability that could not decide is unresolved;
- a capability the engine implements in full that came out partial, and a
  partial capability that executed, leave the run partially covered;
- a required capability whose applicability fact was left to its default,
  and that no decision of the run ruled out, is unresolved
  (:mod:`~ccnl_engine.payroll.capability.rules_requirement`).

The report status is the ``coverage`` axis of the result assurance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models import CoverageStatus, EvidenceStatus
from ccnl_engine.payroll.capability.models_catalog import (
    CapabilityApplicability,
    CapabilityImplementation,
)
from ccnl_engine.payroll.capability.models_trace import TraceState
from ccnl_engine.primitives import FrozenDict

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.capability.models_catalog import (
        CapabilityCatalog,
        CapabilityEntry,
    )
    from ccnl_engine.payroll.capability.rules_requirement import UnresolvedRequirement
    from ccnl_engine.provenance.source.models_chain import ProvenanceStatus

__all__ = [
    "CapabilityGap",
    "CapabilityGapKind",
    "CapabilityReport",
    "CapabilityScope",
    "CaseFacts",
    "compare_with_catalog",
]


class CapabilityScope(StrEnum):
    """Whether a capability concerns the run.

    Attributes:
        APPLICABLE: It applies: it must be computed for the run to be covered.
        NOT_APPLICABLE: Its predicate is false for the case, or its handler
            ruled it out.
        OUTSIDE_INPUT: The fact that makes it apply has no field in the
            request; a case with that fact is outside the engine input.
    """

    APPLICABLE = "applicable"
    NOT_APPLICABLE = "not_applicable"
    OUTSIDE_INPUT = "outside_input"


class CapabilityGapKind(StrEnum):
    """Why an applicable capability is not covered in full.

    Attributes:
        UNSUPPORTED: The engine does not compute it, or did not trace it.
        UNRESOLVED: It ran but could not decide (e.g. a surtax without a
            table for the jurisdiction).
        PARTIAL_RESULT: Implemented in full, it came out partial.
        PARTIAL_IMPLEMENTATION: Implemented for some variants only, it
            executed.
        WRONG_YEAR: The catalog year differs from the tax year of the run.
    """

    UNSUPPORTED = "unsupported"
    UNRESOLVED = "unresolved"
    PARTIAL_RESULT = "partial_result"
    PARTIAL_IMPLEMENTATION = "partial_implementation"
    WRONG_YEAR = "wrong_year"


#: Gap kinds that leave the run partially, not insufficiently, covered.
_PARTIAL_KINDS = frozenset({
    CapabilityGapKind.PARTIAL_RESULT,
    CapabilityGapKind.PARTIAL_IMPLEMENTATION,
})


@dataclass(frozen=True)
class CapabilityGap:
    """An applicable capability the run does not cover in full.

    Attributes:
        feature: The capability name.
        implementation: How the registry says the engine implements it.
        observed: Trace state of the run, ``"absent"`` when untraced.
        kind: Why it is not covered.
    """

    feature: str
    implementation: CapabilityImplementation
    observed: str
    kind: CapabilityGapKind


@dataclass(frozen=True)
class CaseFacts:
    """Facts of a run the applicability predicates read.

    Attributes:
        event_features: Capabilities of the events the request declares.
        closes_employment: Whether the run closes the employment.
        absent_facts: Applicability facts of the registry the request left
            to their default.
    """

    event_features: frozenset[str] = frozenset()
    closes_employment: bool = False
    absent_facts: frozenset[str] = frozenset()


def _scope(
    entry: CapabilityEntry, case: CaseFacts, observed: str | None
) -> CapabilityScope:
    when = entry.applies_when
    if when is CapabilityApplicability.OUTSIDE_INPUT:
        return CapabilityScope.OUTSIDE_INPUT
    applies = {
        CapabilityApplicability.ALWAYS: True,
        CapabilityApplicability.DECIDED: observed not in {None, TraceState.SKIPPED},
        CapabilityApplicability.EVENT: entry.feature in case.event_features,
        CapabilityApplicability.TERMINATION_RUN: case.closes_employment,
    }[when]
    if not applies or observed == TraceState.NOT_APPLICABLE:
        return CapabilityScope.NOT_APPLICABLE
    return CapabilityScope.APPLICABLE


def _gap_kind(entry: CapabilityEntry, observed: str | None) -> CapabilityGapKind | None:
    implementation = entry.implementation
    if implementation is CapabilityImplementation.UNSUPPORTED or observed is None:
        return CapabilityGapKind.UNSUPPORTED
    if observed == TraceState.UNRESOLVED:
        return CapabilityGapKind.UNRESOLVED
    if implementation is CapabilityImplementation.PARTIAL and observed in {
        TraceState.COMPUTED,
        TraceState.PARTIAL,
    }:
        return CapabilityGapKind.PARTIAL_IMPLEMENTATION
    if observed == TraceState.PARTIAL:
        return CapabilityGapKind.PARTIAL_RESULT
    return None


def compare_with_catalog(
    catalog: CapabilityCatalog,
    observed: Mapping[str, str],
    case: CaseFacts,
    year: int,
) -> tuple[tuple[CapabilityGap, ...], dict[str, CapabilityScope]]:
    """Return the gaps and the scope of every capability of the run.

    Args:
        catalog: Capability registry of the year.
        observed: Trace state of each traced capability.
        case: Facts the applicability predicates read.
        year: Tax year of the run; a different catalog year is a gap.

    Returns:
        The gaps in declaration order (a ``wrong_year`` gap first), and
        the scope of each capability.
    """
    gaps: list[CapabilityGap] = []
    if year != catalog.year:
        gaps.append(
            CapabilityGap(
                "__catalog__",
                CapabilityImplementation.NATIVE,
                str(year),
                CapabilityGapKind.WRONG_YEAR,
            )
        )
    scope: dict[str, CapabilityScope] = {}
    for entry in catalog.capabilities:
        state = observed.get(entry.feature)
        scope[entry.feature] = _scope(entry, case, state)
        if scope[entry.feature] is not CapabilityScope.APPLICABLE:
            continue
        kind = _gap_kind(entry, state)
        if kind is not None:
            gaps.append(
                CapabilityGap(
                    entry.feature,
                    entry.implementation,
                    "absent" if state is None else state,
                    kind,
                )
            )
    return tuple(gaps), scope


def _frozen[V](mapping: Mapping[str, V]) -> Mapping[str, V]:
    return FrozenDict(dict(mapping))


@dataclass(frozen=True)
class CapabilityReport:
    """Capability coverage of one run.

    Attributes:
        catalog_year: The year of the catalog used for verification.
        gaps: Applicable capabilities the run does not cover in full.
        scope: Scope of every capability of the catalog for the run.
        rule_sources: Weakest provenance status of the payable rules each
            executed capability read.  It does not change :attr:`status`;
            it feeds the ``evidence`` axis of the result assurance.
        evidence_required: Weakest provenance each executed capability
            accepts, from the registry; a weaker rule blocks the run.
        caller_supplied: Capabilities whose amounts rest on values the
            caller supplied in place of a rule, each with the names of the
            event fields it took them from.
        unresolved: Required capabilities no decision of the run ruled
            out, one per applicability fact left to its default.
    """

    catalog_year: int
    gaps: tuple[CapabilityGap, ...]
    scope: Mapping[str, CapabilityScope] = field(default_factory=dict)
    rule_sources: Mapping[str, ProvenanceStatus] = field(default_factory=dict)
    evidence_required: Mapping[str, EvidenceStatus] = field(default_factory=dict)
    caller_supplied: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    unresolved: tuple[UnresolvedRequirement, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("scope", "rule_sources", "evidence_required", "caller_supplied"):
            object.__setattr__(self, name, _frozen(getattr(self, name)))

    @classmethod
    def empty(cls, year: int) -> CapabilityReport:
        """Return an empty report (no gaps) for *year*.

        Returns:
            A :class:`CapabilityReport` with no gaps and a complete status.
        """
        return cls(catalog_year=year, gaps=())

    @property
    def status(self) -> CoverageStatus:
        """Coverage of the run, the ``coverage`` axis of its assurance.

        Returns:
            :attr:`~CoverageStatus.INCOMPLETE` with an unresolved
            requirement, else :attr:`~CoverageStatus.COMPLETE` when no gap
            exists, :attr:`~CoverageStatus.PARTIAL` when every gap is a
            partial result or a partial implementation,
            :attr:`~CoverageStatus.INCOMPLETE` otherwise.
        """
        if self.unresolved:
            return CoverageStatus.INCOMPLETE
        if not self.gaps:
            return CoverageStatus.COMPLETE
        if {g.kind for g in self.gaps} <= _PARTIAL_KINDS:
            return CoverageStatus.PARTIAL
        return CoverageStatus.INCOMPLETE

    def weak_sources(self) -> dict[str, ProvenanceStatus]:
        """Return the executed capabilities whose rules miss their evidence.

        A capability absent from :attr:`evidence_required` accepts
        ``derived`` rules.

        Returns:
            Capability to the provenance of its weakest rule, for each
            capability whose weakest rule is weaker than it accepts.
        """
        order = list(EvidenceStatus)
        return {
            feature: status
            for feature, status in self.rule_sources.items()
            if order.index(EvidenceStatus(status))
            > order.index(self.evidence_required.get(feature, EvidenceStatus.DERIVED))
        }
