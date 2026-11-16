"""Night work in regular shifts of the operai agricoli e florovivaisti.

Art. 43 (p. 48): night work of the agricoli in regular periodic shifts on
specific duties is paid "soltanto" 10%, not 40%; art. 44 (p. 49): the
florovivaisti 10% instead of 48%.  Area2, 8 hours in March 2026: agricoli
1330.25 / 169 = 7.871 an hour, 25.19 at 40% and 6.30 at 10%; florovivaisti
8.09 an hour (Tabella n. 2), 31.07 at 48% and 6.47 at 10%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import NightShiftEvent
from ccnl_engine.events import ShiftWorkEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.event_kinds import ShiftKind

_DAY = date(2026, 3, 10)


def _paid(subsector: str, event: NightShiftEvent | ShiftWorkEvent) -> Decimal | None:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(5), subsector=subsector),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area2",
            opening_state=PeriodState.zero(),
            events=(event,),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (decision,) = (
        d for d in result.decisions if d.reason_code == "ccnl_supplement_applied"
    )
    return decision.amount


@pytest.mark.parametrize(
    ("subsector", "night", "shift"),
    [("agricoli", "25.19", "6.30"), ("florovivaisti", "31.07", "6.47")],
)
def test_the_shift_pays_ten_percent_instead(
    subsector: str, night: str, shift: str
) -> None:
    """8 night hours: the ordinary premium, or 10% in regular shifts."""
    hours = Decimal(8)
    assert _paid(subsector, NightShiftEvent(_DAY, hours=hours)) == Decimal(night)
    assert _paid(
        subsector, ShiftWorkEvent(_DAY, hours=hours, kind=ShiftKind.NIGHT)
    ) == Decimal(shift)
