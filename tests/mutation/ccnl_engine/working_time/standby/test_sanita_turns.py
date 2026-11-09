"""Art. 60-61 event allowances: 2 * 12h on-call + 6h on-call + 3 * 8h night.

= 43.38 + 11.93 + 65.76 = EUR 121.07 for one hand-computed month.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.agreement.validity.rules import SeriesGapError
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.facade import (
    NightShiftEvent,
    ShiftKind,
    ShiftWorkEvent,
    StandbyEvent,
    StandbyKind,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.standby.handlers import _turn_pay
from ccnl_engine.working_time.standby.models import StandbyRules


def _run(*events: ShiftWorkEvent | NightShiftEvent | StandbyEvent) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=7),
            payment_date=date(2026, 7, 27),
            ccnl_id="sanita-privata-aiop-aris",
            level_code="D",
            opening_state=PeriodState.zero(),
            events=events,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def test_month_of_on_call_turns_and_night_shifts() -> None:
    """Two full turns, six hours, and three eight-hour night shifts.

    At 21.69/12*6*1.10 and 2.74/hour they pay EUR 121.07 in all.
    """
    events: tuple[ShiftWorkEvent | StandbyEvent, ...] = (
        StandbyEvent(date(2026, 7, 2), StandbyKind.HOURS, Decimal(12)),
        StandbyEvent(date(2026, 7, 9), StandbyKind.HOURS, Decimal(12)),
        StandbyEvent(date(2026, 7, 16), StandbyKind.HOURS, Decimal(6)),
        *(
            ShiftWorkEvent(date(2026, 7, day), hours=Decimal(8), kind=ShiftKind.NIGHT)
            for day in (3, 10, 17)
        ),
    )
    result = _run(*events)
    derived = [d for d in result.decisions if d.capability in {"standby", "shift_work"}]
    assert sum((d.amount or Decimal(0) for d in derived), Decimal(0)) == Decimal(
        "121.07"
    )
    assert [d.amount for d in derived if d.capability == "standby"] == [
        Decimal("21.69"),
        Decimal("21.69"),
        Decimal("11.93"),
    ]


@pytest.mark.parametrize("hours", ["3", "13"])
def test_out_of_range_turn_is_not_paid(hours: str) -> None:
    """Neither a three-hour turn nor a thirteen-hour turn qualifies."""
    with pytest.raises(MissingRuleError):
        _run(StandbyEvent(date(2026, 7, 3), StandbyKind.HOURS, Decimal(hours)))


def test_ordinary_night_hours_use_the_same_fixed_rate() -> None:
    """Five ordinary hours worked at night pay 5 * 2.74 = EUR 13.70."""
    result = _run(NightShiftEvent(date(2026, 7, 3), hours=Decimal(5)))
    assert [d.amount for d in result.decisions if d.capability == "night_work"] == [
        Decimal("13.70")
    ]


@pytest.mark.parametrize(
    "event",
    [
        StandbyEvent(date(2020, 10, 8), StandbyKind.HOURS, Decimal(12)),
        ShiftWorkEvent(date(2020, 10, 8), hours=Decimal(8), kind=ShiftKind.NIGHT),
        NightShiftEvent(date(2020, 10, 8), hours=Decimal(8)),
    ],
)
def test_signing_day_does_not_receive_new_rates(
    event: ShiftWorkEvent | NightShiftEvent | StandbyEvent,
) -> None:
    """On 8 October, 12h standby and 8h night earn EUR 0 at new rates.

    From 9 October they would earn EUR 21.69 and 8 * 2.74 = EUR 21.92.
    """
    work = load_ccnl("sanita-privata-aiop-aris").work_rules
    assert work is not None
    if isinstance(event, StandbyEvent):
        assert work.standby_rules is not None
        with pytest.raises(MissingRuleError, match="starts on 2020-10-09"):
            _turn_pay(event, work.standby_rules, "ccnl/sanita-privata-aiop-aris")
    else:
        assert work.time_supplements is not None
        code = (
            "NIGHT_SHIFT_FIXED" if isinstance(event, ShiftWorkEvent) else "NIGHT_FIXED"
        )
        band = next(b for b in work.time_supplements.supplement_bands if b.code == code)
        with pytest.raises(SeriesGapError):
            band.rate.value_at(event.event_date)


def test_rates_begin_day_after_signing() -> None:
    """On 9 October, 12h standby plus 8 night hours pay 21.69 + 21.92 = EUR 43.61."""
    work = load_ccnl("sanita-privata-aiop-aris").work_rules
    assert work is not None
    assert work.standby_rules is not None
    assert work.time_supplements is not None
    event = StandbyEvent(date(2020, 10, 9), StandbyKind.HOURS, Decimal(12))
    _, standby_pay = _turn_pay(
        event, work.standby_rules, "ccnl/sanita-privata-aiop-aris"
    )
    night = next(
        b
        for b in work.time_supplements.supplement_bands
        if b.code == "NIGHT_SHIFT_FIXED"
    )
    night_pay = night.rate.value_at(date(2020, 10, 9)) * Decimal(8)
    assert (standby_pay, night_pay) == (Decimal("21.69"), Decimal("21.92"))


@pytest.mark.parametrize("missing", ["bands", "hourly_divisor", "call_fee"])
def test_non_turn_rules_require_all_legacy_rate_inputs(missing: str) -> None:
    """A legacy band must be complete before paying any turn (e.g. EUR 21.69)."""
    data = {
        "in_tfr_base": False,
        "bands": [{"levels": ["D"], "rates": _legacy_rates()}],
        "hourly_divisor": "16",
        "call_fee": _legacy_rates()["worked_day"],
    }
    data.pop(missing)
    with pytest.raises(
        ValueError, match="without turn_rate require bands, hourly_divisor and call_fee"
    ):
        StandbyRules.model_validate(data)


def _legacy_rates() -> dict[str, object]:
    series = {
        "periods": [{"valid_from": "2020-10-09", "valid_until": None, "value": "21.69"}]
    }
    return dict.fromkeys(
        (
            "worked_day",
            "rest_day",
            "holiday",
            "week",
            "week_holiday",
            "week_holiday_rest_day",
        ),
        series,
    )


def test_intervention_is_not_a_standby_fee() -> None:
    """An intervention needs its own work event, not an invented call fee."""
    with pytest.raises(MissingRuleError):
        _run(StandbyEvent(date(2026, 7, 3), StandbyKind.HOURS, Decimal(12), calls=1))
