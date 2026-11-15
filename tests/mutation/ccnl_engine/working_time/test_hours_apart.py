"""The hours worked on a public holiday, paid on top of the monthly pay.

L. 260/1949 art. 5 c. 3: "ai lavoratori [...] che prestino la loro opera
nelle festività [...] è dovuta, oltre la normale retribuzione globale di
fatto giornaliera, [...] la retribuzione per le ore di lavoro
effettivamente prestate".  Federmeccanica C3 in March 2026: 2158.26 / 173
= 12.4755 an hour; 8 holiday hours are 99.80 of hours and 49.90 of the 50%
supplement.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import HolidayWorkEvent, NightShiftEvent
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_DAY = date(2026, 3, 12)


def _run(*events: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 28),
            ccnl_id="metalmeccanico-federmeccanica",
            level_code="C3",
            opening_state=PeriodState.zero(),
            events=tuple(events),  # type: ignore[arg-type]
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _cash(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.CASH_EARNINGS
        ),
        Decimal(0),
    )


def test_the_holiday_hours_are_paid_with_their_supplement() -> None:
    """99.80 of hours and 49.90 of supplement: 149.70 more cash."""
    holiday = _run(HolidayWorkEvent(_DAY, hours=Decimal(8)))

    hours = [e for e in holiday.ledger_entries if e.entry_id.endswith("_hours")]
    assert [e.amount for e in hours] == [Decimal("99.80")]
    assert _cash(holiday) - _cash(_run()) == Decimal("149.70")
    assert not any(i.code == "supplement_hours_not_posted" for i in holiday.issues)


def test_ordinary_night_hours_are_not_paid_twice() -> None:
    """A night band inside the monthly pay posts the supplement only."""
    night = _run(NightShiftEvent(_DAY, hours=Decimal(6)))
    assert not [e for e in night.ledger_entries if e.entry_id.endswith("_hours")]
