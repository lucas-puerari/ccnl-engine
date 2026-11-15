"""Supplements of seven more CCNLs on their hourly base, March 2026, eight hours.

Calzaturiero 2: 1751.40 / 169, holiday 50%.  Grafica D2: 1543.15 / 173,
holiday 60%, day shift 6%.  Igiene ambientale D2s: 1631.26 / 169, night 33%.
Impiegati agricoli 5: 1278.60 / 169, night 50%.  Trasporto ferroviario F1:
1626.70 / 160, holiday 35%, night 2.50 an hour.  UNEBA 6S: 1395.94 / 164,
night 25%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.event.facade import HolidayWorkEvent, NightShiftEvent, ShiftWorkEvent
from ccnl_engine.working_time.inputs import ShiftKind
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_NIGHT = NightShiftEvent(_DAY, hours=Decimal(8))
_HOLIDAY = HolidayWorkEvent(_DAY, hours=Decimal(8))
_SHIFT = ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.DAY)


@pytest.mark.parametrize(
    ("ccnl", "level", "event", "capability", "amount"),
    [
        ("calzaturiero-assocalzaturifici", "2", _HOLIDAY, "holiday_work", "41.45"),
        ("grafica-editoria-aieg", "D2", _HOLIDAY, "holiday_work", "42.82"),
        ("grafica-editoria-aieg", "D2", _SHIFT, "shift_work", "4.28"),
        ("igiene-ambientale-utilitalia", "D2s", _NIGHT, "night_work", "25.48"),
        ("impiegati-tecnici-agricoli", "5", _NIGHT, "night_work", "30.26"),
        ("trasporto-ferroviario-agens", "F1", _HOLIDAY, "holiday_work", "28.47"),
        ("trasporto-ferroviario-agens", "F1", _NIGHT, "night_work", "20.00"),
        ("uneba-uneba", "6S", _NIGHT, "night_work", "17.02"),
    ],
)
def test_the_supplement_on_the_hourly_base(
    ccnl: str, level: str, event: object, capability: str, amount: str
) -> None:
    """Eight hours at the CCNL share of the hourly base, or its fixed amount."""
    result = _run(event, ccnl=(ccnl, level))
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.amount == Decimal(amount)
