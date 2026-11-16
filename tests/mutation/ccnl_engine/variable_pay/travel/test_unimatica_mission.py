"""Hand oracle: the trasferta and night work of the Unimatica Confapi.

Art. 47 (agreement of 9 July 2018, PDF p. 73): 50% of the daily pay for
each day; after the first month 35%, after the second 20%; 20% when travel
is habitual to the job.  Level 5, March 2026: 2,065.18 over 26 = 79.43 a
day, so 39.72; 27.80 after a month; 15.89 after two or when habitual.
Art. 36 (renewal of 9 March 2021, from 1 January 2022): ordinary night
work 55% on 2,065.18 over 169 (art. 105) = 12.22 an hour: 8 hours 53.77.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
from ccnl_engine.working_time.inputs import NightShiftEvent
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_LEVEL = ("informatica-pmi-unimatica", "5")


@pytest.mark.parametrize(
    ("changes", "daily"),
    [
        ({}, "39.72"),
        ({"mission_over_month": True}, "27.80"),
        ({"mission_over_month": True, "mission_over_two_months": True}, "15.89"),
        ({"habitual_travel": True}, "15.89"),
        ({"habitual_travel": True, "mission_over_month": True}, "15.89"),
    ],
    ids=["first-month", "second-month", "third-month", "habitual", "largest"],
)
def test_half_the_daily_pay_falls_with_the_length_of_the_mission(
    changes: dict[str, bool], daily: str
) -> None:
    """The largest discount that applies lowers the 50% once."""
    event = TravelAllowanceEvent(
        event_date=_DAY,
        days=1,
        outside_municipality=True,
        meals_lodging="none",
        **changes,  # type: ignore[arg-type]
    )
    result = _run(event, ccnl=_LEVEL)
    (decision,) = (d for d in result.decisions if d.capability == "travel_allowance")
    assert decision.inputs["daily_amount"] == Decimal(daily)
    expected = {k: "true" for k, v in changes.items() if k.startswith("mission") and v}
    assert {
        k: v for k, v in decision.inputs.items() if k.startswith("mission_over")
    } == expected


def test_ordinary_night_hours_add_fifty_five_percent() -> None:
    """The hours sit in the monthly pay: the band adds the 55% alone."""
    result = _run(NightShiftEvent(_DAY, hours=Decimal(8)), ccnl=_LEVEL)
    (decision,) = (d for d in result.decisions if d.capability == "night_work")
    assert decision.amount == Decimal("53.77")
