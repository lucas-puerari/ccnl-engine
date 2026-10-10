"""Values the caller supplies in place of a rule are flagged, not sourced.

Metalmeccanico (bundled work rules): weekday overtime band OT_DIURNO 25%,
night band OT_NOTTURNO 50%, holiday band OT_FESTIVO 55%, hourly divisor
173.  A sick pay amount overrides the native sickness capability.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.rules_validity import TimeSeries
from ccnl_engine.payroll.assurance.models_decision import DecisionOrigin
from ccnl_engine.payroll.capability.models_trace import TraceState
from ccnl_engine.payroll.capability.services_trace import (
    build_traces,
    caller_supplied_fields,
)
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.event.facade import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.period.services_caller_rule import (
    CALLER_DECLARED_AMOUNT,
    CALLER_OVERRIDE,
    CALLER_SUPPLIED_AMOUNT,
    CALLER_SUPPLIED_CAPABILITIES,
    CALLER_SUPPLIED_RATE,
    NOT_IN_BUNDLE,
    bundle_value,
    caller_supplied_decisions,
)
from ccnl_engine.payroll.state.models import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.assurance.models_decision import CalculationDecision
    from ccnl_engine.payroll.event.facade import WorkEvent

_CCNL = load_ccnl("metalmeccanico-federmeccanica.json")
_BARE = _CCNL.model_copy(update={"work_rules": None})
_DAY = date(2026, 3, 10)
_OVERTIME = OvertimeEvent(_DAY, Decimal(10), Decimal("15.00"), Decimal("1.25"))


def _only(events: tuple[WorkEvent, ...], ccnl: CCNL = _CCNL) -> CalculationDecision:
    (decision,) = caller_supplied_decisions(events, ccnl)
    return decision


class TestOvertimeRun:
    """A run with overtime at a caller multiplier of 1.25."""

    result = calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=PeriodState.zero(),
            events=(_OVERTIME,),
        )
    )

    def test_decision_flags_the_caller_fields(self) -> None:
        """The multiplier and hourly rate are caller-supplied, with no source."""
        (decision,) = (d for d in self.result.decisions if d.capability == "overtime")
        assert decision.origin is DecisionOrigin.CALLER_SUPPLIED
        assert decision.reason_code == CALLER_SUPPLIED_RATE
        assert decision.source is None
        assert decision.rule == "request:events[0].OvertimeEvent"
        assert decision.inputs["fields"] == "hourly_rate,multiplier"
        assert decision.inputs["multiplier"] == Decimal("1.25")

    def test_bundle_band_is_listed_for_comparison(self) -> None:
        """The CCNL weekday band (15%) is shown next to the caller's 25%."""
        (decision,) = (d for d in self.result.decisions if d.capability == "overtime")
        assert decision.inputs["bundle_band[OT_DIURNO]"] == Decimal("0.25")
        assert decision.inputs["caller_supplement"] == Decimal("0.25")
        assert decision.inputs["bundle_hourly_divisor"] == Decimal(173)

    def test_amount_keeps_the_caller_multiplier(self) -> None:
        """10 h * 15.00 * 1.25 = 187.50 is posted, not the CCNL 15%."""
        overtime = [
            e
            for e in self.result.ledger_entries
            if e.pay_item_kind == "overtime_earning"
        ]
        assert [e.amount for e in overtime] == [Decimal("187.50")]
        (decision,) = (d for d in self.result.decisions if d.capability == "overtime")
        assert decision.amount == Decimal("187.50")
        assert overtime[0].account is AccountKind.CASH_EARNINGS

    def test_report_shows_the_capability_as_caller_supplied(self) -> None:
        """The report lists the fields; no provenance status is claimed."""
        report = self.result.capability_report
        assert report.caller_supplied == {"overtime": ("hourly_rate", "multiplier")}
        assert "overtime" not in report.rule_sources

    def test_trace_still_follows_the_event(self) -> None:
        """Overtime is traced from its event, as before: computed, no gap."""
        executed = frozenset({"overtime"})
        traces = {
            t.feature: t.state for t in build_traces(self.result.decisions, executed)
        }
        assert traces["overtime"] is TraceState.COMPUTED
        assert all(g.feature != "overtime" for g in self.result.capability_report.gaps)
        idle = {
            t.feature: t.state for t in build_traces(self.result.decisions, frozenset())
        }
        assert idle["overtime"] is TraceState.SKIPPED


@pytest.mark.parametrize(
    ("event", "capability", "reason", "fields"),
    [
        (
            NightShiftEvent(_DAY, Decimal("30.00")),
            "night_work",
            CALLER_SUPPLIED_AMOUNT,
            "supplement_amount",
        ),
        (
            ShiftWorkEvent(_DAY, Decimal("12.00")),
            "shift_work",
            CALLER_SUPPLIED_AMOUNT,
            "supplement_amount",
        ),
        (
            AbsenceEvent(_DAY, Decimal(8), Decimal("12.00")),
            "absence",
            CALLER_SUPPLIED_RATE,
            "hourly_rate",
        ),
        (
            SickLeaveEvent(_DAY, Decimal("100.00")),
            "sickness",
            CALLER_OVERRIDE,
            "amount",
        ),
        (BonusEvent(_DAY, Decimal(500)), "bonus", CALLER_DECLARED_AMOUNT, "amount"),
        (
            WelfareEvent(_DAY, Decimal(200)),
            "welfare",
            CALLER_DECLARED_AMOUNT,
            "amount",
        ),
        (
            ArrearsEvent(_DAY, Decimal(300), Decimal("0.23")),
            "contract_renewal_arrears",
            CALLER_SUPPLIED_RATE,
            "separate_tax_rate",
        ),
        (
            BilateralFundEvent(_DAY, Decimal(5), Decimal(10)),
            "bilateral_funds",
            CALLER_SUPPLIED_AMOUNT,
            "employee_amount,employer_amount",
        ),
        (
            TerminationTFREvent(_DAY, Decimal(9000), Decimal("0.23")),
            "termination_tfr",
            CALLER_SUPPLIED_RATE,
            "separate_tax_rate",
        ),
    ],
)
def test_each_event_type_is_flagged(
    event: WorkEvent, capability: str, reason: str, fields: str
) -> None:
    """Every event with a caller value records one caller-supplied decision."""
    decision = _only((event,))
    assert decision.capability == capability
    assert decision.reason_code == reason
    assert decision.inputs["fields"] == fields
    substitute = reason not in {CALLER_DECLARED_AMOUNT, CALLER_OVERRIDE}
    assert (capability in CALLER_SUPPLIED_CAPABILITIES) is substitute


def test_amounts_follow_the_caller_values() -> None:
    """Absence 8 h * 12.00 = -96.00; bilateral 5 + 10; welfare as declared."""
    decisions = caller_supplied_decisions(
        (
            AbsenceEvent(_DAY, Decimal(8), Decimal("12.00")),
            BilateralFundEvent(_DAY, Decimal(5), Decimal(10)),
            WelfareEvent(_DAY, Decimal(200)),
        ),
        _CCNL,
    )
    assert [d.amount for d in decisions] == [
        Decimal("-96.00"),
        Decimal(15),
        Decimal(200),
    ]


def test_fringe_benefit_keeps_its_own_decision() -> None:
    """A fringe benefit records its fringe_benefit decision only."""
    assert caller_supplied_decisions((FringeEvent(_DAY, Decimal(100)),), _CCNL) == ()


def test_supplement_bands_match_their_work_kind() -> None:
    """Night and holiday compare with their bands; shifts have none here."""
    night = _only((NightShiftEvent(_DAY, Decimal(30)),))
    holiday = _only((HolidayWorkEvent(_DAY, Decimal(30)),))
    shift = _only((ShiftWorkEvent(_DAY, Decimal(12)),))
    assert night.inputs["bundle_band[OT_NOTTURNO]"] == Decimal("0.50")
    assert holiday.inputs["bundle_band[OT_FESTIVO]"] == Decimal("0.55")
    assert shift.inputs["bundle_band"] == NOT_IN_BUNDLE


def test_without_work_rules_nothing_is_in_the_bundle() -> None:
    """A CCNL without work rules offers no band."""
    overtime = _only((_OVERTIME,), _BARE)
    assert overtime.inputs["bundle_band"] == NOT_IN_BUNDLE


def test_sick_pay_override_is_reported_as_a_caller_value() -> None:
    """The override of the native sickness capability is a caller field."""
    decisions = caller_supplied_decisions(
        (SickLeaveEvent(_DAY, Decimal("100.00")),), _CCNL
    )
    assert caller_supplied_fields(decisions) == {"sickness": ("amount",)}
    assert decisions[0].amount == Decimal("100.00")


def test_bundle_value_before_the_series_is_not_in_bundle() -> None:
    """A date before the first period has no bundled value."""
    series = TimeSeries.model_validate({
        "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "173"}]
    })
    assert bundle_value(series, date(2019, 12, 31)) == NOT_IN_BUNDLE
    assert bundle_value(series, _DAY) == Decimal(173)


def test_report_leaves_out_declared_amounts() -> None:
    """A welfare amount is a fact; the absence hourly rate stands for a rule."""
    decisions = caller_supplied_decisions(
        (
            WelfareEvent(_DAY, Decimal(200)),
            AbsenceEvent(_DAY, Decimal(8), Decimal("12.00")),
        ),
        _CCNL,
    )
    assert caller_supplied_fields(decisions) == {"absence": ("hourly_rate",)}
