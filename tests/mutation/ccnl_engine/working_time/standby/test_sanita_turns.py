"""Art. 60-61 event allowances: 2 * 12h on-call + 6h on-call + 3 * 8h night.

= 43.38 + 11.93 + 65.76 = EUR 121.07 for one hand-computed month.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
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


def test_intervention_is_not_a_standby_fee() -> None:
    """An intervention needs its own work event, not an invented call fee."""
    with pytest.raises(MissingRuleError):
        _run(StandbyEvent(date(2026, 7, 3), StandbyKind.HOURS, Decimal(12), calls=1))
