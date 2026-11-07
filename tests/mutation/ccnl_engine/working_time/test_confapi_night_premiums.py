"""Hand oracle: the ordinary night premiums of Metalmeccanico Confapi.

Art. 29 row b (p. 101 of the CCNL 3 July 2017): night work until 22:00
25%, after 22:00 35% for the workers not on shifts, 25% for shift workers;
the night starts 12 hours after the start of the morning shift.  Level 4,
March 2026: 2049.91 / 173 = 11.849; 2 h x 25% = 5.92, 6 h x 35% = 24.88,
6 h x 25% = 17.77.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import NightShiftEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _run(event: NightShiftEvent, roles: frozenset[str]) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="metalmeccanico-confapi",
            level_code="4",
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(event,),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


@pytest.mark.parametrize(
    ("hours", "before_22", "roles", "band", "amount"),
    [
        (2, True, frozenset(), "CONFAPI_NOTTURNO_FINO_22", "5.92"),
        (6, False, frozenset(), "CONFAPI_NOTTURNO", "24.88"),
        (6, False, frozenset({"turnista"}), "CONFAPI_NOTTURNO_TURNI", "17.77"),
    ],
)
def test_the_night_premium_by_the_hour_of_the_night(
    hours: int, before_22: bool, roles: frozenset[str], band: str, amount: str
) -> None:
    """Row b by the hour of the night and the column of the worker."""
    event = NightShiftEvent(
        date(2026, 3, 10), hours=Decimal(hours), before_22=before_22
    )
    (decision,) = (
        d for d in _run(event, roles).decisions if d.capability == "night_work"
    )

    assert (decision.inputs["band_code"], decision.amount) == (band, Decimal(amount))


def test_before_22_is_a_boolean() -> None:
    """``1`` is not a flag."""
    with pytest.raises(InvalidInputError, match="before_22"):
        NightShiftEvent(date(2026, 3, 10), hours=Decimal(2), before_22=1)  # type: ignore[arg-type]
