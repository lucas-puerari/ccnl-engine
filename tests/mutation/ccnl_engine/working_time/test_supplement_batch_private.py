"""Night and holiday supplements of private CCNLs on their hourly base, March 2026.

Telecomunicazioni A2 (1560.50 / 173): ordinary night 32%, holiday 50%.
Legno arredamento AE2 (1970.66 / 174): night 35%, holiday 50%.
Panificazione A4 (1634.12 / 173): night 50%, holiday 20%, day shift 6.5%.
ANASTE level 10 (1972.13 / 164): night 25%, holiday 15%.  Eight hours each.
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
        ("telecomunicazioni-asstel", "A2", _NIGHT, "night_work", "23.09"),
        ("telecomunicazioni-asstel", "A2", _HOLIDAY, "holiday_work", "36.08"),
        ("legno-arredamento-federlegno", "AE2", _NIGHT, "night_work", "31.71"),
        ("legno-arredamento-federlegno", "AE2", _HOLIDAY, "holiday_work", "45.30"),
        (
            "panificazione-artigianato-confartigianato",
            "A4",
            _NIGHT,
            "night_work",
            "37.78",
        ),
        (
            "panificazione-artigianato-confartigianato",
            "A4",
            _SHIFT,
            "shift_work",
            "4.91",
        ),
        (
            "istituzioni-servizi-socio-assistenziali-anaste",
            "10",
            _NIGHT,
            "night_work",
            "24.05",
        ),
        (
            "istituzioni-servizi-socio-assistenziali-anaste",
            "10",
            _HOLIDAY,
            "holiday_work",
            "14.43",
        ),
    ],
)
def test_the_supplement_on_the_hourly_base(
    ccnl: str, level: str, event: object, capability: str, amount: str
) -> None:
    """Eight hours at the CCNL share of the monthly pay over the divisor."""
    result = _run(event, ccnl=(ccnl, level))
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.amount == Decimal(amount)
