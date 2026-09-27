"""Build the capability traces and report of a run from what executed.

A trace never looks at the request: a capability is computed only when it
took a :class:`~ccnl_engine.payroll.domain.decisions.CalculationDecision`
(a zero amount with its reason counts) or, for an event feature, when an
event handler had an effect.  A caller-supplied decision records the value
the caller gave in place of a rule; it is reported apart and does not trace
its capability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.handlers._totals import EVENT_FEATURES
from ccnl_engine.payroll.application.period._caller_rules import (
    CALLER_DECLARED_AMOUNT,
)
from ccnl_engine.payroll.domain.capability_catalog import CapabilityReport
from ccnl_engine.payroll.domain.decisions import CalculationStatus, DecisionOrigin
from ccnl_engine.payroll.domain.trace import DecisionTrace, TraceState
from ccnl_engine.payroll.service.pension_fund import NOT_ENROLLED
from ccnl_engine.payroll.service.withholding_agent import NOT_WITHHOLDING_AGENT

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.provenance.domain.chain import ProvenanceStatus

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
    "shortfall_deferral": TraceState.NOT_APPLICABLE,
    "foreign_tax_credit": TraceState.NOT_APPLICABLE,
    "addizionale_regionale": TraceState.NOT_APPLICABLE,
    "addizionale_comunale": TraceState.NOT_APPLICABLE,
    "bonus_pdr": TraceState.SKIPPED,
    "rinnovo_substitute_tax": TraceState.NOT_APPLICABLE,
    "notte_festivi_turni_substitute_tax": TraceState.NOT_APPLICABLE,
    "pension_fund_contribution": TraceState.NOT_APPLICABLE,
}

#: Reasons of a decision that leaves its capability not applicable.
_NOT_APPLICABLE_REASONS = frozenset({NOT_WITHHOLDING_AGENT, NOT_ENROLLED})

_STATE_OF_STATUS: dict[CalculationStatus, TraceState] = {
    CalculationStatus.FINAL: TraceState.COMPUTED,
    CalculationStatus.PROVISIONAL: TraceState.PARTIAL,
    CalculationStatus.INCOMPLETE: TraceState.UNRESOLVED,
    CalculationStatus.REJECTED: TraceState.UNRESOLVED,
}


def _worst_state_by_capability(
    decisions: Iterable[CalculationDecision],
) -> dict[str, TraceState]:
    """Return the state each capability decided, in decision order.

    A capability whose every decision has a not-applicable reason is not
    applicable: the employer does not compute it
    (:data:`NOT_WITHHOLDING_AGENT`) or the worker is not enrolled in a
    pension fund (:data:`NOT_ENROLLED`).  Otherwise the worst status of its
    decisions gives the state.  Caller-supplied decisions are left out.

    Returns:
        Mapping of capability to its trace state.
    """
    worst: dict[str, CalculationStatus] = {}
    skipped: set[str] = set()
    applied: set[str] = set()
    for decision in decisions:
        if decision.origin is DecisionOrigin.CALLER_SUPPLIED:
            continue
        capability = decision.capability
        previous = worst.get(capability, CalculationStatus.FINAL)
        worst[capability] = CalculationStatus.worst((previous, decision.status))
        if decision.reason_code in _NOT_APPLICABLE_REASONS:
            skipped.add(capability)
        else:
            applied.add(capability)
    return {
        capability: (
            TraceState.NOT_APPLICABLE
            if capability in skipped - applied
            else _STATE_OF_STATUS[status]
        )
        for capability, status in worst.items()
    }


def build_traces(
    decisions: Iterable[CalculationDecision],
    executed_features: frozenset[str],
) -> tuple[DecisionTrace, ...]:
    """Build one trace per feature from what the run executed.

    The core stages are computed unless their decisions say the employer
    does not compute them (not a withholding agent, for ``irpef``).  An
    event feature follows its decisions when it took any (e.g.
    ``fringe_benefit``); otherwise it is computed when one of its events
    had an effect, skipped otherwise.  Every other feature
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
    decided = _worst_state_by_capability(decisions)
    traces = [
        DecisionTrace(f, decided.get(f, TraceState.COMPUTED)) for f in _CORE_FEATURES
    ]
    events = tuple(EVENT_FEATURES.values())
    traces.extend(
        DecisionTrace(
            f,
            decided.get(
                f,
                TraceState.COMPUTED if f in executed_features else TraceState.SKIPPED,
            ),
        )
        for f in events
    )
    traces.extend(
        DecisionTrace(f, decided.get(f, default))
        for f, default in _DECISION_FEATURES.items()
    )
    traced = {*_CORE_FEATURES, *events, *_DECISION_FEATURES}
    traces.extend(
        DecisionTrace(capability, state)
        for capability, state in decided.items()
        if capability not in traced
    )
    return tuple(traces)


def traces_to_observed(traces: tuple[DecisionTrace, ...]) -> dict[str, str]:
    """Convert a tuple of decision traces to the observed map for gap detection.

    Returns:
        Mapping of feature name to its :class:`TraceState` string value.
    """
    return {t.feature: t.state for t in traces}


def caller_supplied_fields(
    decisions: Iterable[CalculationDecision],
) -> dict[str, tuple[str, ...]]:
    """Return the event fields each capability took from the caller for a rule.

    A declared amount (a bonus, a welfare benefit) is a fact of the run, not
    a rule, and is left out.

    Returns:
        Capability to the sorted names of the fields listed in the
        ``fields`` input of its caller-supplied decisions.
    """
    fields: dict[str, set[str]] = {}
    for decision in decisions:
        if (
            decision.origin is DecisionOrigin.CALLER_SUPPLIED
            and decision.reason_code != CALLER_DECLARED_AMOUNT
        ):
            names = str(decision.inputs.get("fields", ""))
            fields.setdefault(decision.capability, set()).update(
                name for name in names.split(",") if name
            )
    return {capability: tuple(sorted(names)) for capability, names in fields.items()}


def capability_report(
    catalog: CapabilityCatalog,
    decisions: Iterable[CalculationDecision],
    executed_features: frozenset[str],
    year: int,
    rule_sources: Mapping[str, ProvenanceStatus] | None = None,
) -> CapabilityReport:
    """Return the gaps between the catalog and what the run executed.

    Args:
        catalog: Capability catalog of ``year``.
        decisions: Every decision of the run.
        executed_features: Event features whose handler had an effect.
        year: Tax year of the run.
        rule_sources: Weakest provenance status per executed capability.

    Returns:
        The capability report of the run for ``year``, with the fields
        each capability took from the caller.
    """
    decisions = tuple(decisions)
    observed = traces_to_observed(build_traces(decisions, executed_features))
    return CapabilityReport(
        catalog_year=year,
        gaps=catalog.gaps(observed, detect_absent=True, year=year),
        rule_sources=rule_sources or {},
        caller_supplied=caller_supplied_fields(decisions),
    )
