"""Traces of capabilities a household employer does not compute."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.capability.models_trace import TraceState
from ccnl_engine.payroll.capability.services_trace import build_traces
from ccnl_engine.payroll.withholding.rules_agent import (
    not_withholding_agent_decision,
)


def _states(*decisions: CalculationDecision) -> dict[str, TraceState]:
    return {t.feature: t.state for t in build_traces(decisions, frozenset())}


def test_not_withholding_agent_is_not_applicable() -> None:
    """IRPEF, a core stage, and a credit skipped by the employer are not applicable."""
    states = _states(
        not_withholding_agent_decision("irpef", 2026),
        not_withholding_agent_decision("somma_esente", 2026),
        not_withholding_agent_decision("rinnovo_substitute_tax", 2026),
    )

    assert states["irpef"] is TraceState.NOT_APPLICABLE
    assert states["somma_esente"] is TraceState.NOT_APPLICABLE
    assert states["rinnovo_substitute_tax"] is TraceState.NOT_APPLICABLE
    assert states["tfr"] is TraceState.COMPUTED


def test_a_capability_also_applied_follows_its_status() -> None:
    """A capability with any other decision is traced from its status."""
    applied = CalculationDecision(
        capability="somma_esente",
        status=CalculationStatus.PROVISIONAL,
        reason_code="share_paid",
        rule="l207-2024-art1-c4-c7",
        rule_version="2026",
        amount=Decimal(10),
    )
    states = _states(not_withholding_agent_decision("somma_esente", 2026), applied)

    assert states["somma_esente"] is TraceState.PARTIAL
