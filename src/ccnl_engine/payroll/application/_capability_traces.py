"""Build DecisionTrace list from a PeriodCalculationRequest."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.trace import DecisionTrace, TraceState

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationRequest

_STANDARD_FEATURES: frozenset[str] = frozenset({
    "base_salary",
    "seniority",
    "inps_employee",
    "inps_employer",
    "tfr",
    "irpef",
    "trattamento_integrativo",
    "ulteriore_detrazione_lavoro",
})

_EVENT_FEATURE_MAP: tuple[tuple[type, str], ...] = (
    (OvertimeEvent, "overtime"),
    (NightShiftEvent, "night_work"),
    (HolidayWorkEvent, "holiday_work"),
    (AbsenceEvent, "absence"),
    (SickLeaveEvent, "leave"),
    (SicknessCaseEvent, "sickness"),
    (FringeEvent, "fringe_benefit"),
    (WelfareEvent, "welfare"),
    (BonusEvent, "bonus_pdr"),
    (ArrearsEvent, "contract_renewal_arrears"),
    (BilateralFundEvent, "bilateral_funds"),
    (TerminationTFREvent, "termination_tfr"),
)


def build_traces(request: PeriodCalculationRequest) -> tuple[DecisionTrace, ...]:
    """Build decision traces from a period request for capability reporting.

    Standard features are always COMPUTED.  Event-based features are COMPUTED
    when matching events are present, SKIPPED otherwise.  Parameter-dependent
    features use NOT_APPLICABLE when the required input is absent.

    Returns:
        One :class:`~ccnl_engine.payroll.domain.trace.DecisionTrace` per feature.
    """
    traces: list[DecisionTrace] = [
        DecisionTrace(feature=f, state=TraceState.COMPUTED) for f in _STANDARD_FEATURES
    ]
    present = {type(e) for e in request.events}
    for event_cls, feature in _EVENT_FEATURE_MAP:
        state = TraceState.COMPUTED if event_cls in present else TraceState.SKIPPED
        traces.append(DecisionTrace(feature=feature, state=state))
    na = TraceState.NOT_APPLICABLE
    ok = TraceState.COMPUTED
    traces.extend([
        DecisionTrace(
            feature="addizionale_regionale",
            state=ok if request.regione is not None else na,
        ),
        DecisionTrace(
            feature="addizionale_comunale",
            state=ok if request.comune_belfiore is not None else na,
        ),
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
