"""Hand oracle: the night allowance and the trasferta of the Vigilanza FEDERDAT GPG.

CCNL of 4 May 2023, art. 104 (renewal of 9 July 2026, art. 121): a daily
night allowance by the service, 5.61 in the zona stradale and trasporto
scorta valori, 4.18 in the piantonamento fisso, sala conta and centrale
operativa.  Art. 100 of the renewal: a trasferta pays 30% of the daily
normale retribuzione, the monthly over 26.  Level IV, March 2026: 1,338.85
x 0.30 / 26 = 15.45 a day.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
from ccnl_engine.variable_pay.travel.terms import TravelTerms
from ccnl_engine.working_time.inputs import NightShiftEvent
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)
_LEVEL = ("vigilanza-privata-federdat-gpg", "IV")


@pytest.mark.parametrize(
    ("service", "nights", "amount"),
    [("road_zone_escort", 2, "11.22"), ("fixed_watch_count_room", 3, "12.54")],
)
def test_each_night_pays_the_allowance_of_its_service(
    service: str, nights: int, amount: str
) -> None:
    """The allowance is daily: the nights times the amount of the service."""
    event = NightShiftEvent(_DAY, hours=Decimal(8), shifts=nights, service=service)
    result = _run(event, ccnl=_LEVEL)
    (decision,) = (d for d in result.decisions if d.capability == "night_work")
    assert decision.amount == Decimal(amount)


def test_a_day_of_trasferta_pays_thirty_percent_of_the_daily_pay() -> None:
    """30% of the monthly normale retribuzione over 26."""
    event = TravelAllowanceEvent(
        event_date=_DAY,
        days=1,
        outside_municipality=True,
        meals_lodging="none",
        tfr_base="none",
    )
    result = _run(event, ccnl=_LEVEL)
    (decision,) = (d for d in result.decisions if d.capability == "travel_allowance")
    assert decision.inputs["daily_amount"] == Decimal("15.45")


@pytest.mark.parametrize(
    ("base", "monthly"), [("minimum", "1000"), ("normal", "1100"), ("pay", "1300")]
)
def test_each_base_takes_its_monthly_pay(base: str, monthly: str) -> None:
    """The minimum, the minimum with the scatti, or the whole pay of fact."""
    terms = TravelTerms(None, "r", Decimal(1000), Decimal(1300), Decimal(1100))
    assert terms.monthly(base) == Decimal(monthly)
