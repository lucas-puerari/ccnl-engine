"""A diaria that is a share of the daily pay: Commercio art. 179.

"una diaria non inferiore al doppio della quota giornaliera della
retribuzione di fatto di cui all'art. 208; qualora non vi sia pernottamento
fuori sede la diaria verrà ridotta di un terzo".  Level 4 in March 2026:
(1257.46 + 524.22) x 2 / 26 = 137.05 a day; 91.37 without the night away.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.errors import MissingRuleError
from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
from ccnl_engine.working_time.travel.models import TravelDailyShare
from ccnl_engine.working_time.travel.quotas import share_amount
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_DAY = date(2026, 3, 10)


def _trip(**changes: object) -> TravelAllowanceEvent:
    fields: dict[str, object] = {
        "event_date": _DAY,
        "days": 2,
        "outside_municipality": True,
        "meals_lodging": "none",
        "overnight": True,
        "tfr_base": "none",
        **changes,
    }
    return TravelAllowanceEvent(**fields)  # type: ignore[arg-type]


def _daily(event: TravelAllowanceEvent) -> Decimal:
    result = _run(event, ccnl=("commercio-confcommercio", "4"))
    (decision,) = (d for d in result.decisions if d.capability == "travel_allowance")
    value = decision.inputs["daily_amount"]
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("changes", "daily"),
    [
        ({}, "137.05"),
        ({"overnight": False}, "91.37"),
        ({"habitual_travel": True}, "123.35"),
        ({"mission_over_month": True, "overnight": False}, "82.23"),
    ],
    ids=["night-away", "no-night", "habitual", "long-no-night"],
)
def test_twice_the_daily_pay_less_its_discounts(
    changes: dict[str, object], daily: str
) -> None:
    """A third less without the night away; 10% less for habitual or long travel."""
    assert _daily(_trip(**changes)) == Decimal(daily)


def test_the_night_away_is_a_fact_the_event_states() -> None:
    """The CCNL lowers the diaria without it: unstated, the run stops."""
    with pytest.raises(MissingRuleError, match="overnight stay"):
        _daily(_trip(overnight=None))


def test_a_share_without_discounts_reads_no_fact() -> None:
    """20% of a 1300 minimum over 26 is 10.00, whatever the night."""
    share = TravelDailyShare(rate=Decimal("0.20"), base="minimum")
    assert share_amount(_trip(overnight=None), share, Decimal(1300)) == Decimal(10)


def test_the_hiring_letter_exempts_only_where_the_ccnl_says_so() -> None:
    """Agreed at hiring: nothing; unstated: the run stops."""
    share = TravelDailyShare(
        rate=Decimal("0.20"), base="minimum", hiring_letter_exempts=True
    )
    assert share_amount(_trip(agreed_at_hiring=True), share, Decimal(1300)) == 0
    with pytest.raises(MissingRuleError, match="hiring letter"):
        share_amount(_trip(), share, Decimal(1300))


def test_the_share_is_bounded() -> None:
    """A share above five days of pay or a discount of the whole is rejected."""
    with pytest.raises(ValidationError):
        TravelDailyShare(rate=Decimal(6), base="pay")
    with pytest.raises(ValidationError):
        TravelDailyShare(rate=Decimal(1), base="pay", no_overnight_discount=Decimal(1))
