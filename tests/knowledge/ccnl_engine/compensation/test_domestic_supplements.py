"""The night, holiday, Sunday-holiday and travel pay of a domestic worker.

CCNL lavoro domestico of 28 October 2025: the supplements are measured on
the "retribuzione globale di fatto", which holds the board and lodging
value even in kind (chiarimento a verbale 5).  Level BS live-in in 2026:
minimum 1053.39 plus board and lodging 199.80 = 1253.19 a month, over the
hourly divisor 234 (54 hours x 52 / 12).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.compensation.allowance.models import Allowance
from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
from ccnl_engine.working_time.inputs import HolidayWorkEvent, NightShiftEvent
from ccnl_engine.working_time.travel.models import CcnlTravelAllowance
from tests.knowledge.ccnl_engine.compensation.builders import domestic_month

_LIVE_IN = "lavoro-domestico-convivente"
_GLOBAL_PAY = Decimal("1253.19")


def _amount(capability: str, *events: object, month: int = 3) -> Decimal:
    result = domestic_month(_LIVE_IN, "BS", month, *events)  # type: ignore[arg-type]
    (decision,) = (d for d in result.decisions if d.capability == capability)
    assert decision.amount is not None
    return decision.amount


def _trip(**changes: object) -> TravelAllowanceEvent:
    fields: dict[str, object] = {
        "event_date": date(2026, 3, 10),
        "days": 3,
        "outside_municipality": False,
        "meals_lodging": "both",
        "agreed_at_hiring": False,
        **changes,
    }
    return TravelAllowanceEvent(**fields)  # type: ignore[arg-type]


def test_ordinary_night_hours_add_twenty_percent() -> None:
    """Art. 14 c. 6: 2 hours x 1253.19 / 234 x 20% = 2.14."""
    night = NightShiftEvent(event_date=date(2026, 3, 11), hours=Decimal(2))
    assert _amount("night_work", night) == Decimal("2.14")


def test_holiday_hours_add_sixty_percent() -> None:
    """Art. 16 c. 3: 3 hours x 1253.19 / 234 x 60% = 9.64."""
    holiday = HolidayWorkEvent(event_date=date(2026, 3, 12), hours=Decimal(3))
    assert _amount("holiday_work", holiday) == Decimal("9.64")


def test_a_holiday_on_sunday_pays_a_twenty_sixth_of_the_global_pay() -> None:
    """Art. 16 c. 4: 4 October 2026 is a Sunday, 1253.19 / 26 = 48.20."""
    assert _amount("sunday_holiday", month=10) == (_GLOBAL_PAY / 26).quantize(
        Decimal("0.01")
    )


def test_a_day_of_trasferta_is_a_fifth_of_the_daily_minimum() -> None:
    """Art. 33 c. 2: 1053.39 x 20% / 26 = 8.10 a day, 24.30 in three days."""
    result = domestic_month(_LIVE_IN, "BS", 3, _trip())
    (decision,) = (d for d in result.decisions if d.capability == "travel_allowance")
    assert decision.inputs["daily_amount"] == Decimal("8.10")
    assert decision.amount == Decimal("24.30")


def test_no_diaria_when_the_hiring_letter_provides_the_travel() -> None:
    """Art. 33 c. 2: no diaria when the obligation is in the hiring letter."""
    assert _amount("travel_allowance", _trip(agreed_at_hiring=True)) == 0


def test_the_hiring_letter_is_a_fact_the_event_states() -> None:
    """Unstated, the diaria is not paid on a guess: the run stops."""
    trip = _trip(agreed_at_hiring=None, hours_away=Decimal(10))
    with pytest.raises(MissingRuleError, match="hiring letter"):
        domestic_month(_LIVE_IN, "BS", 3, trip)


def test_the_hiring_letter_fact_is_a_boolean() -> None:
    """A trasferta states the letter as true or false."""
    with pytest.raises(InvalidInputError, match="agreed_at_hiring"):
        _trip(agreed_at_hiring="yes")


@pytest.mark.parametrize(
    "ccnl_id",
    ["lavoro-domestico-non-convivente", "lavoro-domestico-convivente-orario-ridotto"],
)
def test_no_trasferta_outside_the_live_in_worker_of_art_14_c_1(ccnl_id: str) -> None:
    """Art. 33 c. 1 binds the live-in worker of art. 14 c. 1 only."""
    with pytest.raises(MissingRuleError, match="no travel_allowance value"):
        domestic_month(ccnl_id, "B", 3, _trip())


def test_in_global_pay_is_for_a_benefit_in_kind() -> None:
    """A cash allowance is in the global pay anyway: the flag is for in kind."""
    series = {
        "periods": [{"valid_from": "2026-01-01", "valid_until": None, "value": "10"}]
    }
    with pytest.raises(ValidationError, match="benefit in kind"):
        Allowance.model_validate({
            "code": "X",
            "description": "x",
            "monthly": series,
            "in_global_pay": True,
        })


def test_a_share_of_the_minimum_excludes_bands_and_quotas() -> None:
    """One way to price the day: bands, quotas or a share of the minimum."""
    series = {
        "periods": [{"valid_from": "2026-01-01", "valid_until": None, "value": "10"}]
    }
    band = {"hours_from": "0", "italy": series, "abroad": series}
    with pytest.raises(ValidationError, match="exactly one"):
        CcnlTravelAllowance.model_validate({
            "bands": [band],
            "daily_share": {"rate": "0.20", "base": "minimum"},
        })
