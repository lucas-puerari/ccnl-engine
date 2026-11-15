"""A trasferta paid by meals and lodging: Federmeccanica art. 7.

From 1 June 2025 (verbale of 12 June 2025): "Trasferta intera" 50,33,
"Quota per il pasto meridiano o serale" 12,99, "Quota per il
pernottamento" 24,35.  March 2026 pays them.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError

from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
from ccnl_engine.working_time.travel.models import CcnlTravelAllowance
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

_DAY = date(2026, 3, 10)


def _trip(**changes: object) -> TravelAllowanceEvent:
    fields: dict[str, object] = {
        "event_date": _DAY,
        "days": 2,
        "outside_municipality": True,
        "meals_lodging": "none",
        "meals": 2,
        "overnight": True,
        **changes,
    }
    return TravelAllowanceEvent(**fields)  # type: ignore[arg-type]


def _daily(result: PeriodResult) -> Decimal:
    (decision,) = (d for d in result.decisions if d.capability == "travel_allowance")
    value = decision.inputs["daily_amount"]
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize(
    ("meals", "overnight", "daily"),
    [
        (2, True, "50.33"),
        (1, False, "12.99"),
        (2, False, "25.98"),
        (0, True, "24.35"),
        (1, True, "37.34"),
    ],
)
def test_the_quotas_of_the_day(meals: int, overnight: bool, daily: str) -> None:
    """Both meals and the night: the whole trasferta; otherwise the quotas."""
    assert _daily(_run(_trip(meals=meals, overnight=overnight))) == Decimal(daily)


@pytest.mark.parametrize(
    "changes",
    [{"overnight": None}, {"abroad": True}],
    ids=["night-unstated", "abroad"],
)
def test_a_trip_the_quotas_cannot_price(changes: dict[str, object]) -> None:
    """The meals and the night are stated; no quota abroad."""
    with pytest.raises(MissingRuleError):
        _run(_trip(**changes))


def test_the_meals_are_zero_to_two() -> None:
    """A day has at most two meals."""
    with pytest.raises(InvalidInputError, match="meals"):
        _trip(meals=3)
    with pytest.raises(InvalidInputError, match="overnight"):
        _trip(overnight="yes")


def test_bands_or_quotas_exactly_one() -> None:
    """A travel allowance has hours bands or quotas, not both or none."""
    with pytest.raises(ValidationError, match="exactly one"):
        CcnlTravelAllowance.model_validate({})
