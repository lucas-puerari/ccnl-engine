"""Hand oracle: the night and shift premiums of Chimica, March 2026, level E2.

Art. 9 (CNEL text 579): night outside shifts 50% (punto 4), night shift 34%
(5 b), night shift of a 3x7 continuous cycle 46% (5 c), on the elements of
art. 15 point 1 over 175: 1981.14 / 175 = 11.3208; 8 h x 50% = 45.28, 8 h
x 34% = 30.79, 8 h x 46% = 41.66.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import NightShiftEvent, ShiftKind, ShiftWorkEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_HOURS = Decimal(8)
_NIGHT_SHIFT = ShiftWorkEvent(date(2026, 3, 12), hours=_HOURS, kind=ShiftKind.NIGHT)


def _run(event: object, roles: frozenset[str]) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="chimica-farmaceutica-federchimica",
            level_code="E2",
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(event,),  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


@pytest.mark.parametrize(
    ("event", "roles", "capability", "band", "amount"),
    [
        (
            NightShiftEvent(date(2026, 3, 10), hours=_HOURS),
            frozenset(),
            "night_work",
            "CHIM_NOTTURNO",
            "45.28",
        ),
        (_NIGHT_SHIFT, frozenset(), "shift_work", "CHIM_TURNO_NOTTURNO", "30.79"),
        (
            _NIGHT_SHIFT,
            frozenset({"turno_3x7"}),
            "shift_work",
            "CHIM_TURNO_NOTTURNO_3X7",
            "41.66",
        ),
    ],
)
def test_the_night_and_shift_premiums(
    event: object, roles: frozenset[str], capability: str, band: str, amount: str
) -> None:
    """The band of each kind of work on the 1981.14 / 175 hour."""
    (decision,) = (
        d
        for d in _run(event, roles).decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )

    assert (decision.inputs["band_code"], decision.amount) == (band, Decimal(amount))
