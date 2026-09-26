"""Tests for DecisionTrace, TraceState and the traces built from a run."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.handlers._totals import EVENT_FEATURES
from ccnl_engine.payroll.application.period._capability_traces import build_traces
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.trace import DecisionTrace, TraceState

_D = Decimal
_ZERO = _D(0)
_CORE = ("base_salary", "inps_employee", "inps_employer", "tfr", "irpef")
_DECIDED = (
    "worker_category",
    "seniority",
    "family_deductions",
    "ulteriore_detrazione_lavoro",
    "trattamento_integrativo",
    "addizionale_regionale",
    "addizionale_comunale",
)


def _decision(
    capability: str,
    status: CalculationStatus = CalculationStatus.FINAL,
    amount: Decimal | None = _ZERO,
) -> CalculationDecision:
    return CalculationDecision(
        capability=capability,
        status=status,
        reason_code="test_reason",
        rule=f"test/{capability}",
        rule_version="2026",
        amount=amount,
    )


def _states(
    *decisions: CalculationDecision, executed: frozenset[str] = frozenset()
) -> dict[str, TraceState]:
    return {t.feature: t.state for t in build_traces(decisions, executed)}


class TestDecisionTrace:
    """DecisionTrace is a frozen value object."""

    def test_fields_are_accessible(self) -> None:
        """DecisionTrace exposes feature and state."""
        trace = DecisionTrace(feature="irpef", state=TraceState.COMPUTED)
        assert trace.feature == "irpef"
        assert trace.state == TraceState.COMPUTED

    def test_is_frozen(self) -> None:
        """DecisionTrace is immutable."""
        trace = DecisionTrace(feature="tfr", state=TraceState.SKIPPED)
        with pytest.raises(FrozenInstanceError):
            trace.state = TraceState.COMPUTED  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two DecisionTrace instances with same fields are equal."""
        a = DecisionTrace(feature="irpef", state=TraceState.COMPUTED)
        b = DecisionTrace(feature="irpef", state=TraceState.COMPUTED)
        assert a == b

    def test_trace_state_values(self) -> None:
        """All TraceState members expose their string value."""
        assert TraceState.COMPUTED.value == "computed"
        assert TraceState.PARTIAL.value == "partial"
        assert TraceState.SKIPPED.value == "skipped"
        assert TraceState.UNRESOLVED.value == "unresolved"
        assert TraceState.NOT_APPLICABLE.value == "not_applicable"


class TestBuildTraces:
    """build_traces derives every trace from decisions and executed events."""

    def test_core_stages_are_computed(self) -> None:
        """The pipeline stages every run executes are always COMPUTED."""
        states = _states()
        for feature in _CORE:
            assert states[feature] is TraceState.COMPUTED, feature

    def test_nothing_executed_is_never_computed(self) -> None:
        """Without decisions or event effects only the core stages are COMPUTED."""
        computed = {f for f, s in _states().items() if s is TraceState.COMPUTED}
        assert computed == set(_CORE)

    def test_credits_are_not_applicable_without_decision(self) -> None:
        """Trattamento and ulteriore detrazione are no longer always included."""
        states = _states()
        assert states["trattamento_integrativo"] is TraceState.NOT_APPLICABLE
        assert states["ulteriore_detrazione_lavoro"] is TraceState.NOT_APPLICABLE

    @pytest.mark.parametrize("feature", _DECIDED)
    def test_decided_feature_defaults_to_not_applicable(self, feature: str) -> None:
        """A feature traced from decisions is NOT_APPLICABLE without one."""
        assert _states()[feature] is TraceState.NOT_APPLICABLE

    @pytest.mark.parametrize("feature", _DECIDED)
    def test_zero_amount_final_decision_is_computed(self, feature: str) -> None:
        """A final decision computes the feature even with a zero amount."""
        assert _states(_decision(feature))[feature] is TraceState.COMPUTED

    def test_bonus_pdr_skipped_without_decision(self) -> None:
        """No bonus routed to the PdR substitute tax leaves bonus_pdr SKIPPED."""
        assert _states()["bonus_pdr"] is TraceState.SKIPPED

    def test_bonus_pdr_computed_from_decision(self) -> None:
        """A PdR decision computes bonus_pdr."""
        states = _states(_decision("bonus_pdr", amount=_D("50")))
        assert states["bonus_pdr"] is TraceState.COMPUTED

    @pytest.mark.parametrize(
        ("status", "state"),
        [
            (CalculationStatus.FINAL, TraceState.COMPUTED),
            (CalculationStatus.PROVISIONAL, TraceState.PARTIAL),
            (CalculationStatus.INCOMPLETE, TraceState.UNRESOLVED),
            (CalculationStatus.REJECTED, TraceState.UNRESOLVED),
        ],
    )
    def test_decision_status_sets_state(
        self, status: CalculationStatus, state: TraceState
    ) -> None:
        """Each decision status maps to one trace state."""
        decision = _decision("addizionale_regionale", status, amount=None)
        assert _states(decision)["addizionale_regionale"] is state

    def test_worst_decision_of_a_capability_wins(self) -> None:
        """Two decisions of one capability trace as the worse of the two."""
        states = _states(
            _decision("seniority"),
            _decision("seniority", CalculationStatus.INCOMPLETE),
            _decision("seniority"),
        )
        assert states["seniority"] is TraceState.UNRESOLVED

    def test_capability_without_default_is_traced_from_decision(self) -> None:
        """A regime decision gets its own trace, partial when provisional."""
        decision = _decision("rinnovo_substitute_tax", CalculationStatus.PROVISIONAL)
        assert _states(decision)["rinnovo_substitute_tax"] is TraceState.PARTIAL

    @pytest.mark.parametrize("feature", sorted(EVENT_FEATURES.values()))
    def test_event_feature_follows_execution(self, feature: str) -> None:
        """An event feature is COMPUTED only when one of its events had an effect."""
        assert _states()[feature] is TraceState.SKIPPED
        executed = _states(executed=frozenset({feature}))
        assert executed[feature] is TraceState.COMPUTED
        others = set(EVENT_FEATURES.values()) - {feature}
        assert all(executed[f] is TraceState.SKIPPED for f in others)

    def test_one_trace_per_feature(self) -> None:
        """No feature is traced twice."""
        traces = build_traces(
            (_decision("seniority"), _decision("rinnovo_substitute_tax")),
            frozenset({"overtime"}),
        )
        features = [t.feature for t in traces]
        assert len(features) == len(set(features))

    def test_result_is_deterministic(self) -> None:
        """Same decisions and executed features produce identical traces."""
        decisions = (_decision("seniority"),)
        executed = frozenset({"welfare"})
        assert build_traces(decisions, executed) == build_traces(decisions, executed)
