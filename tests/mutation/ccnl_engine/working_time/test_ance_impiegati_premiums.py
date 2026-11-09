"""Hand oracle: the premiums on ordinary hours of Edilizia ANCE impiegati.

Art. 54 (p. 71): night outside periodic shifts 34%, festivo 45%, on the
elements of art. 44 over 173.  Level 3, March 2026: 1982.05 / 173 =
11.4569; 8 h x 34% = 31.16, 8 h x 45% = 41.24497 -> 41.24.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import IssueCause
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import HolidayWorkEvent, NightShiftEvent
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.inputs import HolidayWorkKind

_HOURS = Decimal(8)


def _run(event: object) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="edilizia-ance-impiegati",
            level_code="3",
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
            NightShiftEvent(date(2026, 3, 10), hours=_HOURS),
            "night_work",
            "ANCE_IMP_NOTTURNO",
            "31.16",
        ),
        (
            HolidayWorkEvent(date(2026, 3, 19), hours=_HOURS),
            "holiday_work",
            "ANCE_IMP_FESTIVO",
            "41.24",
        ),
    ],
)
def test_the_ordinary_hour_premiums(
    event: object, capability: str, band: str, amount: str
) -> None:
    """The band of each kind of work on the 1982.05 / 173 hour."""
    (decision,) = (
        d
        for d in _run(event).decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )

    assert (decision.inputs["band_code"], decision.amount) == (band, Decimal(amount))
    assert decision.inputs["hourly_base_monthly"] == Decimal("1982.05")


@pytest.mark.parametrize(("in_shift", "expected"), [(False, "45.83"), (True, "0.00")])
def test_night_holiday_excludes_periodic_shifts(in_shift: bool, expected: str) -> None:
    """8 night-holiday hours: 1982.05 / 173 x 50% = 45.83 non-turnista.

    The turnista's excluded 50% band is 0.00, not total remuneration.
    """
    event = HolidayWorkEvent(
        date(2026, 3, 19),
        hours=_HOURS,
        kind=HolidayWorkKind.NIGHT_HOLIDAY,
        in_periodic_shift=in_shift,
    )
    result = _run(event)
    (decision,) = (
        d
        for d in result.decisions
        if d.reason_code == "ccnl_supplement_applied" and d.capability == "holiday_work"
    )
    assert decision.inputs["band_code"] == "ANCE_IMP_FESTIVO_NOTTURNO"
    assert decision.inputs["work"] == "night_holiday"
    assert decision.inputs["hours"] == _HOURS
    assert decision.inputs["band_supplement"] == (
        Decimal(0) if in_shift else Decimal("0.50")
    )
    assert decision.inputs["in_periodic_shift"] == ("yes" if in_shift else "no")
    assert decision.inputs["hours_paid_apart"] == "unconfirmed"
    assert decision.reason_code == "ccnl_supplement_applied"
    assert decision.amount == Decimal(expected)
    assert decision.status.value == "provisional"
    if in_shift:
        assert any(
            issue.code == "supplement_shift_holiday_rate_unresolved"
            and issue.status.value == "provisional"
            and issue.capability == "holiday_work"
            and issue.cause is IssueCause.RULE
            and "10%" in issue.message
            for issue in result.issues
        )
    else:
        assert not any(
            issue.code == "supplement_shift_holiday_rate_unresolved"
            for issue in result.issues
        )
