"""Supplements of five more CCNLs on their hourly base, July 2026, eight hours.

Farmacie private Q3: 1969.97 / 173, holiday 30%.  Gas-acqua 3: 2191.09 /
167, day shift 5.5%.  Impianti sportivi IV: 1506.82 / 173, night 10%,
holiday 30%.  Scuole private L3: 1767.98 / 164, night 15%.  Vigilanza
Federdat IV: 1468.88 / 173, holiday 35%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import HolidayWorkEvent, NightShiftEvent, ShiftWorkEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.inputs import ShiftKind

_DAY = date(2026, 7, 10)
_NIGHT = NightShiftEvent(_DAY, hours=Decimal(8))
_HOLIDAY = HolidayWorkEvent(_DAY, hours=Decimal(8))
_SHIFT = ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.DAY)


@pytest.mark.parametrize(
    ("ccnl", "level", "event", "capability", "amount"),
    [
        ("farmacie-private-h121", "Q3", _HOLIDAY, "holiday_work", "27.33"),
        ("gas-acqua-utilitalia", "3", _SHIFT, "shift_work", "5.77"),
        ("impianti-sportivi-sport", "IV", _NIGHT, "night_work", "6.97"),
        ("impianti-sportivi-sport", "IV", _HOLIDAY, "holiday_work", "20.90"),
        ("scuole-private-agidae", "L3", _NIGHT, "night_work", "12.94"),
        ("vigilanza-privata-federdat-gpg", "IV", _HOLIDAY, "holiday_work", "23.77"),
    ],
)
def test_the_supplement_on_the_hourly_base(
    ccnl: str, level: str, event: object, capability: str, amount: str
) -> None:
    """Eight hours at the CCNL share of the monthly pay over the divisor."""
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=7),
            payment_date=date(2026, 7, 28),
            ccnl_id=ccnl,
            level_code=level,
            opening_state=PeriodState.zero(),
            events=(event,),  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.amount == Decimal(amount)
