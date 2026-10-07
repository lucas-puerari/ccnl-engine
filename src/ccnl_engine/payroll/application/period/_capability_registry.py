"""Bind the capability registry to the handlers and the trace of a run.

Before the first report built from a registry, :func:`validate_registry`
rejects a registry the engine cannot honour:

- an implemented capability without a registered handler of its kind;
- a registered handler without an implemented registry entry;
- a handler whose capability the run trace does not show, an event handler
  without a traced capability included;
- a capability that takes caller values for a rule but is declared native
  or unsupported, or one declared caller-supplied that takes none;
- an applicability fact the request has no reader for.

:func:`capability_report` then compares what the run traced with the
registry, for the facts of the case.
"""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.handlers._totals import EVENT_FEATURES
from ccnl_engine.payroll.application.handlers.registry import _HANDLER_REGISTRY
from ccnl_engine.payroll.application.period._applicability_facts import (
    FACT_READERS,
    absent_facts,
)
from ccnl_engine.payroll.application.period._caller_rules import (
    CALLER_SUPPLIED_CAPABILITIES,
)
from ccnl_engine.payroll.application.period._capability_traces import (
    HANDLERS,
    build_traces,
    caller_supplied_fields,
    traces_to_observed,
)
from ccnl_engine.payroll.domain.capability_catalog import CapabilityImplementation
from ccnl_engine.payroll.domain.capability_report import (
    CapabilityReport,
    CaseFacts,
    compare_with_catalog,
)
from ccnl_engine.payroll.domain.decisions import DecisionOrigin
from ccnl_engine.payroll.domain.events import BonusEvent
from ccnl_engine.payroll.domain.requirements import unresolved_requirements
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.shared.domain.errors import DataIntegrityError

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.capability_catalog import (
        CapabilityCatalog,
        CapabilityEntry,
    )
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.provenance.domain.chain import ProvenanceStatus

__all__ = ["capability_report", "case_facts", "registry_errors", "validate_registry"]

#: Event types whose handler is traced through a decision, not an event
#: capability: a bonus is traced by the ``bonus_pdr`` decision of the run.
_TRACED_BY_DECISION = frozenset({BonusEvent})

_TAKES_CALLER_VALUES = frozenset({
    CapabilityImplementation.CALLER_SUPPLIED,
    CapabilityImplementation.PARTIAL,
})


def _handler_errors(implemented: Mapping[str, CapabilityEntry]) -> list[str]:
    """Return the entries and handlers that do not match one another.

    Returns:
        One message per implemented entry without a handler of its kind,
        and per handler without an implemented entry.
    """
    errors = [
        f"{feature}: {entry.implementation} without a registered "
        f"{entry.handler} handler"
        for feature, entry in implemented.items()
        if HANDLERS.get(feature) is not entry.handler
    ]
    errors.extend(
        f"{feature}: handler registered without an implemented registry entry"
        for feature in HANDLERS
        if feature not in implemented
    )
    return errors


def _trace_errors(implemented: Mapping[str, CapabilityEntry]) -> list[str]:
    """Return the handlers whose capability a run trace would not show.

    Returns:
        One message per untraced capability and per event handler whose
        event type has no traced capability.
    """
    traced = {trace.feature for trace in build_traces((), frozenset())}
    errors = [
        f"{feature}: handler not observable in the run trace"
        for feature in implemented
        if feature not in traced
    ]
    errors.extend(
        f"{event.__name__}: event handler not observable in the run trace"
        for event in _HANDLER_REGISTRY
        if event not in EVENT_FEATURES and event not in _TRACED_BY_DECISION
    )
    return errors


def _caller_errors(implemented: Mapping[str, CapabilityEntry]) -> list[str]:
    """Return the entries whose implementation hides or invents caller values.

    Returns:
        One message per contradicting entry.
    """
    takes = CALLER_SUPPLIED_CAPABILITIES
    errors = [
        f"{feature}: takes caller values in place of a rule but is "
        f"{entry.implementation}"
        for feature, entry in implemented.items()
        if feature in takes and entry.implementation not in _TAKES_CALLER_VALUES
    ]
    errors.extend(
        f"{feature}: declared caller_supplied but takes no caller value"
        for feature, entry in implemented.items()
        if entry.implementation is CapabilityImplementation.CALLER_SUPPLIED
        and feature not in takes
    )
    return errors


def registry_errors(catalog: CapabilityCatalog) -> list[str]:
    """Return every way *catalog* contradicts the handlers of the engine.

    Returns:
        One message per contradiction, empty when the registry holds.
    """
    implemented = {entry.feature: entry for entry in catalog.implemented()}
    return [
        *_handler_errors(implemented),
        *_trace_errors(implemented),
        *_caller_errors(implemented),
        *(
            f"{entry.feature}: applicability fact {fact} has no request reader"
            for entry in catalog.capabilities
            for fact in entry.applicability_facts
            if fact not in FACT_READERS
        ),
    ]


@cache
def validate_registry(catalog: CapabilityCatalog) -> None:
    """Reject *catalog* when it contradicts the handlers of the engine.

    Raises:
        DataIntegrityError: Listing every contradiction found.
    """
    errors = registry_errors(catalog)
    if errors:
        msg = f"capability catalog {catalog.year}: " + "; ".join(errors)
        raise DataIntegrityError(msg)


def case_facts(ctx: RunContext) -> CaseFacts:
    """Return the facts of the run the applicability predicates read.

    Returns:
        The capabilities of the declared events, whether the run is a
        termination run or the regular run of the month the employment ends
        in (an extra-month or adjustment run of that month does not close
        it), and the applicability facts the request left to their default.
    """
    request = ctx.request
    period = request.employment_period
    ended = None if period is None else period.ended_on
    month = request.period_id
    kind = ctx.run_kind
    closes = kind is RunKind.TERMINATION or (
        kind is RunKind.REGULAR
        and ended is not None
        and (ended.year, ended.month) == (month.year, month.month)
    )
    return CaseFacts(
        event_features=frozenset(
            EVENT_FEATURES[type(event)]
            for event in request.events
            if type(event) in EVENT_FEATURES
        ),
        closes_employment=closes,
        absent_facts=absent_facts(request),
    )


def capability_report(
    catalog: CapabilityCatalog,
    decisions: Iterable[CalculationDecision],
    executed_features: frozenset[str],
    case: CaseFacts,
    year: int,
    rule_sources: Mapping[str, ProvenanceStatus] | None = None,
) -> CapabilityReport:
    """Return the scope and gaps of a run against the registry.

    Args:
        catalog: Capability registry of the tax year of the run.
        decisions: Every decision of the run.
        executed_features: Event features whose handler had an effect.
        case: Facts the applicability predicates read.
        year: Tax year of the run.
        rule_sources: Weakest provenance status per executed capability.

    Returns:
        The capability report of the run, with the fields each capability
        took from the caller, the evidence each executed one accepts and
        the required capabilities nothing resolved.
    """
    validate_registry(catalog)
    decisions = tuple(decisions)
    observed = traces_to_observed(build_traces(decisions, executed_features))
    gaps, scope = compare_with_catalog(catalog, observed, case, year)
    sources = dict(rule_sources or {})
    required = {
        entry.feature: entry.evidence
        for entry in catalog.capabilities
        if entry.feature in sources
    }
    return CapabilityReport(
        catalog_year=year,
        gaps=gaps,
        scope=scope,
        rule_sources=sources,
        evidence_required=required,
        caller_supplied=caller_supplied_fields(decisions),
        unresolved=unresolved_requirements(
            catalog,
            scope,
            frozenset(
                d.capability
                for d in decisions
                if d.origin is not DecisionOrigin.CALLER_SUPPLIED
            ),
            case.absent_facts,
        ),
    )
