"""Build the capability traces and report of a run from what executed.

A trace never looks at the request: a capability is computed only when it
took a :class:`~ccnl_engine.payroll.domain.decisions.CalculationDecision`
(a zero amount with its reason counts) or, for an event feature, when an
event handler had an effect.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.handlers._totals import EVENT_FEATURES
from ccnl_engine.payroll.domain.capability_catalog import CapabilityReport
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.trace import DecisionTrace, TraceState

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog
    from ccnl_engine.payroll.domain.decisions import CalculationDecision

# Pipeline stages every run executes unconditionally.
_CORE_FEATURES = ("base_salary", "inps_employee", "inps_employer", "tfr", "irpef")

# Features traced from their decisions, with the state they take when the
# run took no decision for them.
_DECISION_FEATURES: dict[str, TraceState] = {
    "worker_category": TraceState.NOT_APPLICABLE,
    "seniority": TraceState.NOT_APPLICABLE,
    "family_deductions": TraceState.NOT_APPLICABLE,
    "ulteriore_detrazione_lavoro": TraceState.NOT_APPLICABLE,
    "trattamento_integrativo": TraceState.NOT_APPLICABLE,
    "somma_esente": TraceState.NOT_APPLICABLE,
    "withholding_shortfall": TraceState.NOT_APPLICABLE,
    "addizionale_regionale": TraceState.NOT_APPLICABLE,
    "addizionale_comunale": TraceState.NOT_APPLICABLE,
    "bonus_pdr": TraceState.SKIPPED,
    "rinnovo_substitute_tax": TraceState.NOT_APPLICABLE,
    "notte_festivi_turni_substitute_tax": TraceState.NOT_APPLICABLE,
}

_STATE_OF_STATUS: dict[CalculationStatus, TraceState] = {
    CalculationStatus.FINAL: TraceState.COMPUTED,
    CalculationStatus.PROVISIONAL: TraceState.PARTIAL,
    CalculationStatus.INCOMPLETE: TraceState.UNRESOLVED,
    CalculationStatus.REJECTED: TraceState.UNRESOLVED,
}


def _worst_status_by_capability(
    decisions: Iterable[CalculationDecision],
) -> dict[str, CalculationStatus]:
    """Return the worst status each capability decided, in decision order.

    Returns:
        Mapping of capability to the most severe status of its decisions.
    """
    worst: dict[str, CalculationStatus] = {}
    for decision in decisions:
        previous = worst.get(decision.capability, CalculationStatus.FINAL)
        worst[decision.capability] = CalculationStatus.worst((
            previous,
            decision.status,
        ))
    return worst


def build_traces(
    decisions: Iterable[CalculationDecision],
    executed_features: frozenset[str],
) -> tuple[DecisionTrace, ...]:
    """Build one trace per feature from what the run executed.

    The core stages are always computed.  An event feature is computed when
    one of its events had an effect, skipped otherwise.  Every other feature
    follows its decisions: final is computed, provisional is partial,
    incomplete or rejected is unresolved; with no decision it takes its
    default (not applicable, or skipped for ``bonus_pdr``).  A capability
    that decided without a catalog default (e.g. a substitute tax regime)
    is traced from its decisions too.

    Args:
        decisions: Every decision of the run.
        executed_features: Event features whose handler had an effect.

    Returns:
        One :class:`~ccnl_engine.payroll.domain.trace.DecisionTrace` per
        feature.
    """
    decided = _worst_status_by_capability(decisions)
    traces = [DecisionTrace(f, TraceState.COMPUTED) for f in _CORE_FEATURES]
    traces.extend(
        DecisionTrace(
            f,
            TraceState.COMPUTED if f in executed_features else TraceState.SKIPPED,
        )
        for f in EVENT_FEATURES.values()
    )
    traces.extend(
        DecisionTrace(f, _STATE_OF_STATUS[decided[f]] if f in decided else default)
        for f, default in _DECISION_FEATURES.items()
    )
    traces.extend(
        DecisionTrace(capability, _STATE_OF_STATUS[status])
        for capability, status in decided.items()
        if capability not in _DECISION_FEATURES
    )
    return tuple(traces)


def traces_to_observed(traces: tuple[DecisionTrace, ...]) -> dict[str, str]:
    """Convert a tuple of decision traces to the observed map for gap detection.

    Returns:
        Mapping of feature name to its :class:`TraceState` string value.
    """
    return {t.feature: t.state for t in traces}


def capability_report(
    catalog: CapabilityCatalog,
    decisions: Iterable[CalculationDecision],
    executed_features: frozenset[str],
    year: int,
) -> CapabilityReport:
    """Return the gaps between the catalog and what the run executed.

    Returns:
        The capability report of the run for ``year``.
    """
    observed = traces_to_observed(build_traces(decisions, executed_features))
    return CapabilityReport(
        catalog_year=year,
        gaps=catalog.gaps(observed, detect_absent=True, year=year),
    )
