"""Hand oracle: the night and holiday work of the Orafi argentieri industria.

Rinnovo 23 December 2021 (from 1 January 2022), art. 6: night work from
22 to 6 is 30% (20% in rotating shifts), holiday work 45%, "oltre alla
normale retribuzione" and on the paga base di fatto, without the seniority
increments.  Level 3, March 2026: 1,734.59 over 173 = 10.0265 an hour.
8 night hours: 24.06; 8 holiday hours: 80.21 for the hours and 36.10 more.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.working_time.event_kinds import HolidayWorkKind
from ccnl_engine.working_time.inputs import HolidayWorkEvent, NightShiftEvent
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_LEVEL = ("orafi-argentieri-industria-federorafi", "3")


def _paid(event: object, capability: str) -> tuple[Decimal | None, object]:
    result = _run(event, ccnl=_LEVEL)
    (decision,) = (d for d in result.decisions if d.capability == capability)
    return decision.amount, decision.inputs.get("hours_amount")


def test_night_hours_outside_shifts_add_thirty_percent() -> None:
    """The hours sit in the monthly pay: the band adds the 30% alone."""
    event = NightShiftEvent(_DAY, hours=Decimal(8))
    assert _paid(event, "night_work") == (Decimal("24.06"), None)


def test_holiday_hours_are_paid_with_forty_five_percent_more() -> None:
    """The holiday hours themselves on top of the month, and 45% on them."""
    event = HolidayWorkEvent(_DAY, hours=Decimal(8), kind=HolidayWorkKind.HOLIDAY)
    assert _paid(event, "holiday_work") == (Decimal("36.10"), Decimal("80.21"))
