"""Hand oracle for the 2026 ordinary and supplementary hours.

Level 2 tabellare 779.21, contingenza 513.96,
EDR 10.33, divisor 173. Supplementary 2 h = (1303.50 + 28% x 1293.17)
x 2 / 173 = 19.26; holiday 1 h = 50% x 1293.17 / 173 = 3.74;
night 1 h = 30% x 1293.17 / 173 = 2.24 outside shifts and
20% x 1293.17 / 173 = 1.49 in a rotating shift.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import (
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.inputs import WeeklyHours
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.event_kinds import OvertimeKind, ShiftKind

_DAY = date(2026, 3, 12)


def _run(event: object) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="multiservizi-anip",
            level_code="2",
            weekly_hours=WeeklyHours(Decimal(20)),
            full_time_weekly_hours=WeeklyHours(Decimal(40)),
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(event,),  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def test_supplementary_hour_uses_global_hour_and_base_pay_premium() -> None:
    """Two hours: 2 x (1303.50 + 0.28 x 1293.17) / 173 = 19.26, not 19.29."""
    result = _run(OvertimeEvent(_DAY, Decimal(2), kind=OvertimeKind.SUPPLEMENTARY))
    decision = next(
        d
        for d in result.decisions
        if d.capability == "overtime" and d.reason_code == "ccnl_overtime_band_applied"
    )
    assert decision.amount == Decimal("19.26")
    assert decision.inputs["band_code"] == "OT_SUPPLEMENTARE"


def test_stated_global_rate_still_uses_base_pay_for_the_premium() -> None:
    """Two hours at 1303.50/173 plus 28% of 1293.17/173 remain 19.26."""
    event = OvertimeEvent(
        _DAY,
        Decimal(2),
        hourly_rate=Decimal("1303.50") / Decimal(173),
        kind=OvertimeKind.SUPPLEMENTARY,
    )
    result = _run(event)
    decision = next(
        d
        for d in result.decisions
        if d.capability == "overtime" and d.reason_code == "ccnl_overtime_band_applied"
    )
    assert decision.amount == Decimal("19.26")


@pytest.mark.parametrize(
    ("event", "capability", "band", "amount"),
    [
        (
            HolidayWorkEvent(_DAY, hours=Decimal(1)),
            "holiday_work",
            "MS_FESTIVO",
            "3.74",
        ),
        (NightShiftEvent(_DAY, hours=Decimal(1)), "night_work", "MS_NOTTURNO", "2.24"),
        (
            ShiftWorkEvent(_DAY, hours=Decimal(1), kind=ShiftKind.NIGHT),
            "shift_work",
            "MS_NOTTURNO_TURNO",
            "1.49",
        ),
    ],
)
def test_ordinary_premiums_exclude_seniority_and_edr(
    event: object, capability: str, band: str, amount: str
) -> None:
    """One holiday or night hour: 1293.17 / 173 times 50%, 30% or 20%."""
    decision = next(
        d
        for d in _run(event).decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.amount == Decimal(amount)
    assert decision.inputs["band_code"] == band
    assert decision.inputs["hourly_base_monthly"] == Decimal("1293.17")
    assert "hourly_base[EDR]" not in decision.inputs
