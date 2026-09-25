"""Tests for DecisionTrace and TraceState domain types."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application._capability_traces import build_traces
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
    WorkEvent,
)
from ccnl_engine.payroll.domain.family import FamilyComposition
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState
from ccnl_engine.payroll.domain.sickness import SicknessCase
from ccnl_engine.payroll.domain.trace import DecisionTrace, TraceState

_YEAR = 2026
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_DATE = date(_YEAR, 1, 15)
_D = Decimal


def _req(**kwargs: object) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=1),
        payment_date=date(_YEAR, 1, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        **kwargs,  # type: ignore[arg-type]
    )


def _make_sickness_case_event() -> SicknessCaseEvent:
    case = SicknessCase(
        episode_start=_DATE,
        episode_end=_DATE,
        working_days=1,
        waiting_period_days=0,
        gross_daily=_D("70"),
        inps_daily_rate=_D("0.50"),
        integration_rate=_D("1"),
        carenza_integration_rate=_D("0"),
    )
    return SicknessCaseEvent(event_date=_DATE, case=case)


def _all_event_types() -> tuple[WorkEvent, ...]:
    return (
        OvertimeEvent(event_date=_DATE, hours=_D(2), hourly_rate=_D("15")),
        NightShiftEvent(event_date=_DATE, supplement_amount=_D("10")),
        HolidayWorkEvent(event_date=_DATE, supplement_amount=_D("20")),
        AbsenceEvent(event_date=_DATE, hours=_D(8), hourly_rate=_D("15")),
        SickLeaveEvent(event_date=_DATE, amount=_D("100")),
        _make_sickness_case_event(),
        FringeEvent(event_date=_DATE, amount=_D("50")),
        WelfareEvent(event_date=_DATE, amount=_D("100")),
        BonusEvent(event_date=_DATE, amount=_D("500")),
        ArrearsEvent(event_date=_DATE, amount=_D("200"), separate_tax_rate=_D("0.23")),
        BilateralFundEvent(
            event_date=_DATE, employee_amount=_D("5"), employer_amount=_D("5")
        ),
        TerminationTFREvent(
            event_date=_DATE, amount=_D("3000"), separate_tax_rate=_D("0.23")
        ),
    )


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
    """build_traces derives traces from the request without a static list."""

    def test_standard_features_always_computed(self) -> None:
        """Standard features are always traced as COMPUTED."""
        traces = build_traces(_req())
        by_feature = {t.feature: t.state for t in traces}
        for feature in (
            "base_salary",
            "seniority",
            "inps_employee",
            "inps_employer",
            "tfr",
            "irpef",
            "trattamento_integrativo",
            "ulteriore_detrazione_lavoro",
        ):
            assert by_feature[feature] == TraceState.COMPUTED, feature

    def test_event_features_skipped_without_events(self) -> None:
        """Event-based features are SKIPPED when no matching events are present."""
        traces = build_traces(_req())
        by_feature = {t.feature: t.state for t in traces}
        for feature in (
            "overtime",
            "night_work",
            "holiday_work",
            "absence",
            "leave",
            "sickness",
            "fringe_benefit",
            "welfare",
            "bonus_pdr",
            "contract_renewal_arrears",
            "bilateral_funds",
            "termination_tfr",
        ):
            assert by_feature[feature] == TraceState.SKIPPED, feature

    def test_all_event_features_computed_when_events_present(self) -> None:
        """All event-based features become COMPUTED when event types are present."""
        req = _req(events=_all_event_types())
        by_feature = {t.feature: t.state for t in build_traces(req)}
        for feature in (
            "overtime",
            "night_work",
            "holiday_work",
            "absence",
            "leave",
            "sickness",
            "fringe_benefit",
            "welfare",
            "bonus_pdr",
            "contract_renewal_arrears",
            "bilateral_funds",
            "termination_tfr",
        ):
            assert by_feature[feature] == TraceState.COMPUTED, feature

    @pytest.mark.parametrize(
        ("event", "feature"),
        [
            (
                OvertimeEvent(event_date=_DATE, hours=_D(2), hourly_rate=_D("15")),
                "overtime",
            ),
            (FringeEvent(event_date=_DATE, amount=_D("50")), "fringe_benefit"),
            (
                BilateralFundEvent(
                    event_date=_DATE, employee_amount=_D(5), employer_amount=_D(5)
                ),
                "bilateral_funds",
            ),
        ],
    )
    def test_single_event_type_does_not_affect_others(
        self, event: WorkEvent, feature: str
    ) -> None:
        """A single event type only marks its own feature as COMPUTED."""
        req = _req(events=(event,))
        by_feature = {t.feature: t.state for t in build_traces(req)}
        assert by_feature[feature] == TraceState.COMPUTED
        other = "fringe_benefit" if feature == "overtime" else "overtime"
        assert by_feature[other] == TraceState.SKIPPED

    def test_parameter_features_not_applicable_without_params(self) -> None:
        """Parameter-dependent features are NOT_APPLICABLE when inputs absent."""
        traces = build_traces(_req())
        by_feature = {t.feature: t.state for t in traces}
        assert by_feature["addizionale_regionale"] == TraceState.NOT_APPLICABLE
        assert by_feature["addizionale_comunale"] == TraceState.NOT_APPLICABLE
        assert by_feature["family_deductions"] == TraceState.NOT_APPLICABLE

    def test_parameter_features_computed_when_params_present(self) -> None:
        """Parameter-dependent features are COMPUTED when inputs are provided."""
        req = _req(
            regione="LOM",
            comune_belfiore="F205",
            family_composition=FamilyComposition(),
        )
        by_feature = {t.feature: t.state for t in build_traces(req)}
        assert by_feature["addizionale_regionale"] == TraceState.COMPUTED
        assert by_feature["addizionale_comunale"] == TraceState.COMPUTED
        assert by_feature["family_deductions"] == TraceState.COMPUTED

    def test_result_is_deterministic(self) -> None:
        """Same request produces identical traces."""
        req = _req()
        assert build_traces(req) == build_traces(req)
