"""Hand oracle: the premiums on ordinary hours of DMO, March 2026, level IV.

Testo Unico 29 September 2025: art. 134 (p. 43) ordinary night 15%; art.
136 c. 7 (p. 43) Sunday 30%; art. 139 (p. 44) weekly rest day 30%; art.
138 (p. 44) holidays as straordinario festivo, 30% of art. 132 with the
hour paid apart.  Hourly base: art. 189 normale retribuzione over 168 (art.
194): 1781.68 / 168 = 10.6052; 8 h x 30% = 25.45, 8 h x 15% = 12.73.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import HolidayWorkEvent, HolidayWorkKind, NightShiftEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_HOURS = Decimal(8)


def _run(event: object) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="dmo-federdistribuzione",
            level_code="IV",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(event,),  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


@pytest.mark.parametrize(
    ("event", "capability", "band", "amount"),
    [
        (
            HolidayWorkEvent(
                date(2026, 3, 15), hours=_HOURS, kind=HolidayWorkKind.SUNDAY
            ),
            "holiday_work",
            "DMO_DOMENICA",
            "25.45",
        ),
        (
            HolidayWorkEvent(
                date(2026, 3, 22), hours=_HOURS, kind=HolidayWorkKind.REST_DAY
            ),
            "holiday_work",
            "DMO_RIPOSO",
            "25.45",
        ),
        (
            HolidayWorkEvent(date(2026, 3, 19), hours=_HOURS),
            "holiday_work",
            "DMO_FESTIVO",
            "25.45",
        ),
        (
            NightShiftEvent(date(2026, 3, 10), hours=_HOURS),
            "night_work",
            "DMO_NOTTURNO",
            "12.73",
        ),
    ],
)
def test_the_ordinary_hour_premiums(
    event: object, capability: str, band: str, amount: str
) -> None:
    """The band of each kind of work on the 1781.68 / 168 hour."""
    (decision,) = (
        d
        for d in _run(event).decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )

    assert (decision.inputs["band_code"], decision.amount) == (band, Decimal(amount))
    assert decision.inputs["hourly_base_monthly"] == Decimal("1781.68")
