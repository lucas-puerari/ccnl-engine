"""Ristorazione collettiva and Confapi supplements, March 2026, eight hours.

Ristorazione collettiva level 6s: 1480.77 / 172 (art. 160): night 25%,
holiday 20%.  Metalmeccanico Confapi level 3: 1964.74 / 173, night shift 25%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.event.facade import HolidayWorkEvent, NightShiftEvent, ShiftWorkEvent
from ccnl_engine.working_time.inputs import ShiftKind
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_RISTORAZIONE = ("pubblici-esercizi-fipe-angem-ristorazione-collettiva", "6s")


@pytest.mark.parametrize(
    ("ccnl", "event", "capability", "amount"),
    [
        (_RISTORAZIONE, NightShiftEvent(_DAY, hours=Decimal(8)), "night_work", "17.22"),
        (
            _RISTORAZIONE,
            HolidayWorkEvent(_DAY, hours=Decimal(8)),
            "holiday_work",
            "13.77",
        ),
        (
            ("metalmeccanico-confapi", "3"),
            ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.NIGHT),
            "shift_work",
            "22.71",
        ),
    ],
)
def test_the_supplement_on_the_hourly_base(
    ccnl: tuple[str, str], event: object, capability: str, amount: str
) -> None:
    """Eight hours at the CCNL share of the monthly pay over the divisor."""
    result = _run(event, ccnl=ccnl)
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )
    assert decision.amount == Decimal(amount)
