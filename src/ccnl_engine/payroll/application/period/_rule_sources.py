"""Provenance of the payable rules a run executed.

A capability the run computed read one or more payable rules; each rule
carries a provenance status (see
:class:`~ccnl_engine.provenance.source.models_chain.ProvenanceStatus`).  A rule
whose status is ``missing`` makes the result incomplete: an amount rests on
a value no source backs.  The weakest status of each executed capability is
reported in the capability report; an ``assumed`` or ``missing`` one blocks
the payability of the result (see
:mod:`~ccnl_engine.payroll.domain.assurance`), a ``derived`` one does not.

As in the capability traces, what executed is read from the decisions and
event effects of the run, never from the request.  A rule without a record
is not reported: the bundled data cannot hold one (the provenance check
rejects it), and caller-supplied rules without provenance are out of scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._capability_traces import build_traces
from ccnl_engine.payroll.application.period._rule_lookup import (
    LOADED,
    contract_rules,
    tax_rules,
)
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.trace import TraceState
from ccnl_engine.provenance.source.models_chain import ProvenanceStatus

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.provenance.source.models_chain import RuleProvenance

_EXECUTED = frozenset({TraceState.COMPUTED, TraceState.PARTIAL})
MISSING_SOURCE_CODE = "rule_source_missing"


@dataclass(frozen=True)
class RuleSource:
    """The provenance status of one payable rule a capability read.

    Attributes:
        capability: Catalog feature that read the rule.
        rule: Identifier of the rule, ``<ruleset>:<path>``.
        status: Provenance status recorded for the rule.
    """

    capability: str
    rule: str
    status: ProvenanceStatus


def _status(
    provenance: RuleProvenance | ProvenanceStatus | None,
) -> ProvenanceStatus | None:
    if provenance is None or isinstance(provenance, ProvenanceStatus):
        return provenance
    return provenance.status


def run_rule_sources(
    ctx: RunContext,
    decisions: Iterable[CalculationDecision],
    executed_features: frozenset[str],
) -> tuple[RuleSource, ...]:
    """Return the recorded provenance of every payable rule the run read.

    Args:
        ctx: Context of the run.
        decisions: Every decision of the run.
        executed_features: Event features whose handler had an effect.

    Returns:
        One entry per rule with a record, capabilities in trace order.
    """
    read = contract_rules(ctx) | tax_rules(ctx)
    sources: list[RuleSource] = []
    for trace in build_traces(decisions, executed_features):
        feature = trace.feature
        if trace.state not in _EXECUTED:
            continue
        loader = LOADED.get(feature)
        rules = loader(ctx) if loader is not None else read.get(feature, ())
        sources.extend(
            RuleSource(feature, rule, status)
            for rule, provenance in rules
            if (status := _status(provenance)) is not None
        )
    return tuple(sources)


def weakest_by_capability(
    sources: Iterable[RuleSource],
) -> Mapping[str, ProvenanceStatus]:
    """Return the weakest provenance status of each capability.

    Returns:
        Capability to the weakest status among its rules.
    """
    weakest: dict[str, ProvenanceStatus] = {}
    for source in sources:
        previous = weakest.get(source.capability, source.status)
        weakest[source.capability] = ProvenanceStatus.weakest((previous, source.status))
    return weakest


def missing_source_issues(
    sources: Iterable[RuleSource],
) -> tuple[CalculationIssue, ...]:
    """Return one incomplete issue per rule whose status is ``missing``.

    Returns:
        The issues, naming the rule and the capability that read it.
    """
    return tuple(
        CalculationIssue(
            code=MISSING_SOURCE_CODE,
            message=(
                f"{source.capability}: rule {source.rule} has no source; the "
                "amount it feeds cannot be relied upon"
            ),
            status=CalculationStatus.INCOMPLETE,
        )
        for source in sources
        if source.status is ProvenanceStatus.MISSING
    )
