"""Build DecisionTrace list from a PeriodCalculationRequest and computed results."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.trace import DecisionTrace, TraceState

if TYPE_CHECKING:
    from ccnl_engine.payroll.application._period_amounts import _PeriodAmounts
    from ccnl_engine.payroll.domain.period import PeriodCalculationRequest

_ZERO = Decimal(0)

# Features always computed regardless of inputs.
_ALWAYS_COMPUTED: frozenset[str] = frozenset({
    "base_salary",
    "inps_employee",
    "inps_employer",
    "tfr",
    "irpef",
    "trattamento_integrativo",
    "ulteriore_detrazione_lavoro",
})

# Event types where COMPUTED/SKIPPED is determined by event presence.
_EVENT_FEATURE_MAP: tuple[tuple[type, str], ...] = (
    (OvertimeEvent, "overtime"),
    (NightShiftEvent, "night_work"),
    (HolidayWorkEvent, "holiday_work"),
    (ShiftWorkEvent, "shift_work"),
    (AbsenceEvent, "absence"),
    (SickLeaveEvent, "leave"),
    (SicknessCaseEvent, "sickness"),
    (FringeEvent, "fringe_benefit"),
    (WelfareEvent, "welfare"),
    (ArrearsEvent, "contract_renewal_arrears"),
    (BilateralFundEvent, "bilateral_funds"),
    (TerminationTFREvent, "termination_tfr"),
)


_SURTAX_FEATURES = ("addizionale_regionale", "addizionale_comunale")


def _surtax_trace(feature: str, amounts: _PeriodAmounts) -> DecisionTrace:
    """Trace one surtax from its decision: none taken, final, or not final.

    Returns:
        NOT_APPLICABLE without a decision, COMPUTED for a final decision and
        UNRESOLVED otherwise (unknown table).
    """
    decision = next(
        (d for d in amounts.surtax.decisions if d.capability == feature), None
    )
    if decision is None:
        return DecisionTrace(feature=feature, state=TraceState.NOT_APPLICABLE)
    state = (
        TraceState.COMPUTED
        if decision.status is CalculationStatus.FINAL
        else TraceState.UNRESOLVED
    )
    return DecisionTrace(feature=feature, state=state)


def build_traces(
    request: PeriodCalculationRequest,
    amounts: _PeriodAmounts,
) -> tuple[DecisionTrace, ...]:
    """Build decision traces from actual computation results for capability reporting.

    Standard features are COMPUTED when the engine applied them; seniority is
    NOT_APPLICABLE when the caller did not supply ``seniority_months``.
    Event-based features are COMPUTED when matching events are present.
    ``bonus_pdr`` is COMPUTED only when PdR substitute tax was actually applied
    (``pdr_eligible > 0``).  Surtax features follow their decisions.
    Parameter-dependent features use NOT_APPLICABLE when the required input
    is absent.

    Args:
        request: The original period calculation request.
        amounts: Computed monetary amounts for the period.

    Returns:
        One :class:`~ccnl_engine.payroll.domain.trace.DecisionTrace` per feature.
    """
    traces: list[DecisionTrace] = [
        DecisionTrace(feature=f, state=TraceState.COMPUTED) for f in _ALWAYS_COMPUTED
    ]
    # Seniority: NOT_APPLICABLE when the caller did not supply seniority_months,
    # meaning seniority increments were not evaluated for this employee.
    seniority_state = (
        TraceState.NOT_APPLICABLE
        if request.seniority_months is None
        else TraceState.COMPUTED
    )
    traces.append(DecisionTrace(feature="seniority", state=seniority_state))

    present = {type(e) for e in request.events}
    for event_cls, feature in _EVENT_FEATURE_MAP:
        state = TraceState.COMPUTED if event_cls in present else TraceState.SKIPPED
        traces.append(DecisionTrace(feature=feature, state=state))

    # bonus_pdr is COMPUTED only when PdR substitute tax was actually applied.
    pdr_state = (
        TraceState.COMPUTED if amounts.pdr_eligible > _ZERO else TraceState.SKIPPED
    )
    traces.append(DecisionTrace(feature="bonus_pdr", state=pdr_state))

    na = TraceState.NOT_APPLICABLE
    ok = TraceState.COMPUTED
    traces.extend([
        *(_surtax_trace(feature, amounts) for feature in _SURTAX_FEATURES),
        DecisionTrace(
            feature="family_deductions",
            state=ok if request.family_composition is not None else na,
        ),
    ])
    return tuple(traces)


def traces_to_observed(traces: tuple[DecisionTrace, ...]) -> dict[str, str]:
    """Convert a tuple of decision traces to the observed map for gap detection.

    Returns:
        Mapping of feature name to its :class:`TraceState` string value.
    """
    return {t.feature: t.state for t in traces}
