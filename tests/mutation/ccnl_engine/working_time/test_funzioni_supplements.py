"""Funzioni Centrali and Funzioni Locali ARAN: supplements on the monthly pay over 156.

Funzioni Centrali, level ASSISTENTI in March 2026 (1834.56): the overtime
hour adds the rateo of the tredicesima (CCNL 12/2/2018 art. 25 c. 4):
1834.56 x 13 / 12 / 156 x 1.15 x 4 hours = 58.60; ordinary night work 20%
of 1834.56 / 156 x 8 hours = 18.82, without the rateo.  Funzioni Locali,
OPERATORI_ESPERTI (1796.60): the day shift 10% x 8 hours = 9.21.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.event.facade import (
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.inputs import ShiftKind
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_DERIVED = frozenset({"ccnl_hourly_rate_derived", "ccnl_supplement_applied"})


def _amount(ccnl: tuple[str, str], event: object, capability: str) -> Decimal:
    result = _run(event, ccnl=ccnl)
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code in _DERIVED
    )
    assert decision.amount is not None
    return decision.amount


_CENTRALI = ("funzioni-centrali-aran", "ASSISTENTI")
_LOCALI = ("funzioni-locali-aran", "OPERATORI_ESPERTI")


@pytest.mark.parametrize(
    ("ccnl", "event", "capability", "amount"),
    [
        (
            _CENTRALI,
            OvertimeEvent(event_date=_DAY, hours=Decimal(4)),
            "overtime",
            "58.60",
        ),
        (_CENTRALI, NightShiftEvent(_DAY, hours=Decimal(8)), "night_work", "18.82"),
        (_CENTRALI, HolidayWorkEvent(_DAY, hours=Decimal(8)), "holiday_work", "18.82"),
        (
            _CENTRALI,
            ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.DAY),
            "shift_work",
            "9.41",
        ),
        (_LOCALI, NightShiftEvent(_DAY, hours=Decimal(8)), "night_work", "18.43"),
        (
            _LOCALI,
            ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.DAY),
            "shift_work",
            "9.21",
        ),
    ],
    ids=["fc-overtime", "fc-night", "fc-holiday", "fc-shift", "fl-night", "fl-shift"],
)
def test_the_supplements_of_the_comparti(
    ccnl: tuple[str, str], event: object, capability: str, amount: str
) -> None:
    """The overtime hour holds the rateo; the maggiorazioni do not."""
    assert _amount(ccnl, event, capability) == Decimal(amount)
