"""Sanità ARAN: an hourly base with the rateo of the tredicesima; fixed indennità.

CCNL 2019-2021 art. 47 c. 7: the overtime hour divides by 156 "la
retribuzione base mensile [...] comprensiva del rateo di tredicesima
mensilità".  CCNL 2022-2024 art. 67: night 4.00 an hour, holiday 2.55 an
hour, shift 2.07 a day.  Level ASSISTENTI in March 2026: 1913.48 x 13 / 12
/ 156 = 13.2881 an hour.
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
from ccnl_engine.working_time.hourly.components import rateo
from ccnl_engine.working_time.inputs import ShiftKind
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_DERIVED = frozenset({"ccnl_hourly_rate_derived", "ccnl_supplement_applied"})


def _amount(event: object, capability: str) -> Decimal:
    result = _run(event, ccnl=("sanita-aran", "ASSISTENTI"))
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code in _DERIVED
    )
    assert decision.amount is not None
    return decision.amount


def test_overtime_hour_holds_the_rateo_of_the_tredicesima() -> None:
    """4 hours x 13.2881 x 1.15 = 61.13."""
    assert _amount(OvertimeEvent(event_date=_DAY, hours=Decimal(4)), "overtime") == (
        Decimal("61.13")
    )


@pytest.mark.parametrize(
    ("event", "capability", "amount"),
    [
        (NightShiftEvent(_DAY, hours=Decimal(8)), "night_work", "32.00"),
        (HolidayWorkEvent(_DAY, hours=Decimal(8)), "holiday_work", "20.40"),
        (
            ShiftWorkEvent(_DAY, hours=Decimal(8), kind=ShiftKind.DAY, shifts=3),
            "shift_work",
            "6.21",
        ),
    ],
    ids=["night", "holiday", "shift"],
)
def test_the_indennita_are_fixed_amounts(
    event: object, capability: str, amount: str
) -> None:
    """Art. 67: by the hour at night and on a holiday, by the day in shifts."""
    assert _amount(event, capability) == Decimal(amount)


def test_the_rateo_of_further_payments() -> None:
    """13 payments add a twelfth; none add nothing."""
    parts = (("base_salary", Decimal(1200)),)
    assert rateo(parts, 13) == (("rateo", Decimal(100)),)
    assert rateo(parts, 14) == (("rateo", Decimal(200)),)
    assert rateo(parts, None) == ()
