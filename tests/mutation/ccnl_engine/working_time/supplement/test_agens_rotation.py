"""Hand oracle: the Mobilità AF shift allowance by rotation, and its trasferta.

Renewal of 22 May 2025, art. 81 punto 1 (PDF pp. 131-132), for each day of
presence from 1 August 2025: 2.20 in rotations over the 24 hours, 2.45 in
uncadenced rotations, 1.30 in rotations over two daily periods.  Art. 77
(PDF pp. 124-125): over 12 hours away 35.00 a day, over 4 and up to 12 hours
16.00, abroad 30% more (45.50 and 20.80).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError, MissingRuleError
from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
from ccnl_engine.working_time.inputs import ShiftKind, ShiftWorkEvent
from tests.mutation.ccnl_engine.variable_pay.travel.test_handlers import _run

_AGENS = ("trasporto-ferroviario-agens", "C1")
_DAY = date(2026, 3, 10)


def _shift(service: str | None, kind: ShiftKind = ShiftKind.DAY) -> Decimal:
    event = ShiftWorkEvent(_DAY, hours=Decimal(8), kind=kind, shifts=3, service=service)
    (decision,) = (
        d for d in _run(event, ccnl=_AGENS).decisions if d.capability == "shift_work"
    )
    assert decision.amount is not None
    return decision.amount


@pytest.mark.parametrize(
    ("service", "amount"),
    [
        ("rotating_24h", "6.60"),
        ("non_cadenced_24h", "7.35"),
        ("two_periods", "3.90"),
    ],
)
def test_the_rotation_sets_the_daily_allowance(service: str, amount: str) -> None:
    """Three days of presence at the rate of the rotation."""
    assert _shift(service) == Decimal(amount)


def test_a_night_shift_pays_the_same_rotation_rate() -> None:
    """Art. 81 pays the day of presence, day or night alike."""
    assert _shift("rotating_24h", ShiftKind.NIGHT) == Decimal("6.60")


def test_a_shift_without_its_rotation_is_rejected() -> None:
    """The bands differ by the rotation: an unstated one blocks."""
    with pytest.raises(InvalidInputError, match="by the service"):
        _shift(None)


def test_a_rotation_the_ccnl_does_not_name_is_rejected() -> None:
    """No band pays a rotation the CCNL does not name."""
    with pytest.raises(MissingRuleError, match="for the service 'nope'"):
        _shift("nope")


def test_the_service_must_be_a_code() -> None:
    """A blank rotation is rejected."""
    with pytest.raises(InvalidInputError, match=r"ShiftWorkEvent\.service"):
        ShiftWorkEvent(_DAY, hours=Decimal(8), service=" ")


@pytest.mark.parametrize(
    ("hours", "abroad", "daily"),
    [
        ("5", False, "16.00"),
        ("12", False, "16.00"),
        ("13", False, "35.00"),
        ("5", True, "20.80"),
        ("13", True, "45.50"),
    ],
)
def test_the_hours_away_choose_the_trasferta_band(
    hours: str, abroad: bool, daily: str
) -> None:
    """Over 4 and up to 12 hours the flat refund; over 12 the full allowance."""
    event = TravelAllowanceEvent(
        event_date=_DAY,
        days=1,
        hours_away=Decimal(hours),
        abroad=abroad,
        outside_municipality=True,
        meals_lodging="none",
        tfr_base="none",
    )
    (decision,) = (
        d
        for d in _run(event, ccnl=_AGENS).decisions
        if d.capability == "travel_allowance"
    )
    assert decision.inputs["daily_amount"] == Decimal(daily)
