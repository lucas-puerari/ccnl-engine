"""Hand oracle: the premiums on ordinary hours of Edilizia ANCE, March 2026.

Art. 19 (p. 40): night outside shifts 28%, guardiano 8%, festivo 45%; the
overtime 35% on top of the hour.  Art. 24 point 3 (p. 49): the base is
paga base di fatto, ex contingenza and indennità territoriale di settore,
not the EDR: level 2, 1823.74 / 173 = 10.5418; 8 h x 28% = 23.61, 8 h x 8%
= 6.75, 8 h x 45% = 37.95, 2 h x 135% = 28.46.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import HolidayWorkEvent, NightShiftEvent, OvertimeEvent
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


def _run(event: object, roles: frozenset[str] = frozenset()) -> PeriodResult:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="edilizia-ance",
            level_code="2",
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
            "ANCE_NOTTURNO",
            "23.61",
        ),
        (
            NightShiftEvent(date(2026, 3, 10), hours=_HOURS),
            frozenset({"guardiano"}),
            "night_work",
            "ANCE_NOTTURNO_GUARDIANO",
            "6.75",
        ),
        (
            HolidayWorkEvent(date(2026, 3, 19), hours=_HOURS),
            frozenset(),
            "holiday_work",
            "ANCE_FESTIVO",
            "37.95",
        ),
    ],
)
def test_the_ordinary_hour_premiums(
    event: object, roles: frozenset[str], capability: str, band: str, amount: str
) -> None:
    """The band of each kind of work on the 1823.74 / 173 hour."""
    (decision,) = (
        d
        for d in _run(event, roles).decisions
        if d.capability == capability and d.reason_code == "ccnl_supplement_applied"
    )

    assert (decision.inputs["band_code"], decision.amount) == (band, Decimal(amount))
    assert decision.inputs["hourly_base_monthly"] == Decimal("1823.74")
    assert "hourly_base[EDR]" not in decision.inputs


@pytest.mark.parametrize(("in_shift", "expected"), [(False, "6.75"), (True, "0.00")])
def test_sunday_rest_excludes_shift_workers(in_shift: bool, expected: str) -> None:
    """8 Sunday hours on 1823.74 / 173: non-shift 8% = 6.75; shift = 0."""
    event = HolidayWorkEvent(
        date(2026, 3, 15),
        hours=_HOURS,
        kind=HolidayWorkKind.HOLIDAY_COMPENSATORY_REST,
        in_periodic_shift=in_shift,
    )
    (decision,) = (
        d
        for d in _run(event).decisions
        if d.reason_code == "ccnl_supplement_applied" and d.capability == "holiday_work"
    )
    assert decision.inputs["band_code"] == "ANCE_DOMENICA_RIPOSO"
    assert decision.inputs["in_periodic_shift"] == ("yes" if in_shift else "no")
    assert decision.amount == Decimal(expected)


def test_shift_fact_is_needed_only_for_the_restricted_band() -> None:
    """Other holiday bands need no shift fact; Sunday needs it for 8% or 0%."""
    with pytest.raises(InvalidInputError, match="worker is a turnista is not stated"):
        _run(
            HolidayWorkEvent(
                date(2026, 3, 15),
                hours=_HOURS,
                kind=HolidayWorkKind.HOLIDAY_COMPENSATORY_REST,
            )
        )
    assert any(
        d.amount == Decimal("37.95") and d.reason_code == "ccnl_supplement_applied"
        for d in _run(HolidayWorkEvent(date(2026, 3, 19), hours=_HOURS)).decisions
    )


def test_the_overtime_hour_leaves_the_edr_out() -> None:
    """2 h at 135% of 10.5418."""
    (decision,) = (
        d
        for d in _run(OvertimeEvent(date(2026, 3, 11), Decimal(2))).decisions
        if d.capability == "overtime" and d.reason_code == "ccnl_hourly_rate_derived"
    )

    assert decision.amount == Decimal("28.46")
