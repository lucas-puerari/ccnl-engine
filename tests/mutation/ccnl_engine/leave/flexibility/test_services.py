"""Studi art. 92: the permits of a programme of flexibility, credited and paid.

A programme from January 2026: four weeks of March of 42, 46, 50 and 40
hours earn 0.5 + 1 + 0 + 0 = 1.5 hours.  Not taken, they are paid with the
June 2027 pay, the sixth month after December 2026, at the hourly quota of
the monthly pay (1,614.12 / 170, art. 137) with the 15% overtime premium of
art. 95: 1.5 x 1,614.12 x 1.15 / 170 = 16.379 -> 16.38.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.balance.models import LeaveAccount, LeaveBalance
from ccnl_engine.leave.flexibility.inputs import FlexibilityWeekEvent
from ccnl_engine.leave.flexibility.services import (
    accrue_weeks,
    flexibility_payout,
    flexibility_premiums,
    payout_month,
    programme_year,
)
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.leave.models import LeaveRules

_STUDI = "studi-professionali-confprofessioni"
_FLEX = LeaveBucket.FLESSIBILITA
_WEEKS = tuple(
    FlexibilityWeekEvent(date(2026, 3, day), Decimal(hours))
    for day, hours in ((2, 42), (9, 46), (16, 50), (23, 40))
)
_OWED = LeaveBalance(_FLEX, 2026, Decimal(18), Decimal(0))


def _rules() -> LeaveRules:
    work = load_ccnl(_STUDI).work_rules
    assert work is not None
    assert work.leave_rules is not None
    return work.leave_rules


def _run(
    period: PeriodId,
    events: tuple[FlexibilityWeekEvent, ...] = (),
    *balances: LeaveBalance,
    month: int | None = 1,
    end: date | None = None,
) -> PeriodResult:
    opening = PeriodState.zero()
    opening = replace(
        opening, accrual=replace(opening.accrual, leave=LeaveAccount(balances))
    )
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(10),
                flexibility_programme_month=month,
                permit_carryover=True,
            ),
            period_id=period,
            payment_date=date(period.year, period.month, 27),
            ccnl_id=_STUDI,
            level_code="4",
            opening_state=opening,
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2020, 1, 1), end),
            events=events,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return result


def _flex(result: PeriodResult) -> list[LeaveBalance]:
    return [b for b in result.closing_state.accrual.leave.balances if b.bucket is _FLEX]


def _paid(result: PeriodResult) -> dict[str, Decimal]:
    return {
        i.item_id: i.amount for i in result.pay_items if "flessibilita" in i.item_id
    }


def test_the_weeks_credit_their_programme_year() -> None:
    """March 2026: 1.5 hours, 18 twelfths, to the programme of 2026."""
    assert _flex(_run(PeriodId(2026, 3), _WEEKS)) == [_OWED]


def test_the_hours_left_are_paid_in_the_sixth_month_after() -> None:
    """Nothing in May 2027; 16.38 with the June 2027 pay, then settled."""
    assert _paid(_run(PeriodId(2027, 5), (), _OWED)) == {}
    june = _run(PeriodId(2027, 6), (), _OWED)
    assert _paid(june) == {"leave_flessibilita_2027-06-regular": Decimal("16.38")}
    assert all(b.settled for b in _flex(june))


def test_without_the_programme_month_nothing_is_paid() -> None:
    """The calendar year keeps the hours, inexact; no payment is due."""
    (balance,) = _flex(_run(PeriodId(2026, 3), _WEEKS, month=None))
    assert not balance.exact
    assert _paid(_run(PeriodId(2027, 6), (), _OWED, month=None)) == {}


def test_the_end_of_the_employment_pays_them_with_the_premium() -> None:
    """Closing in March 2026: 1.5 x 1,595.42 x 1.15 / 170 = 16.188 -> 16.19."""
    closing = _run(PeriodId(2026, 3), _WEEKS, end=date(2026, 3, 31))
    assert _paid(closing) == {"leave_flessibilita_2026-03-regular": Decimal("16.19")}


@pytest.mark.parametrize(
    ("day", "month", "year"),
    [
        (date(2026, 3, 2), 1, 2026),
        (date(2026, 3, 2), 4, 2025),
        (date(2026, 3, 2), None, 2026),
    ],
)
def test_the_programme_year_of_a_day(day: date, month: int | None, year: int) -> None:
    """The year of the last start of the programme on or before the day."""
    assert programme_year(day, month) == year


def test_the_payout_month() -> None:
    """A programme from April 2026 ends in March 2027, paid in September."""
    assert payout_month(2026, 4, 6) == (2027, 9)
    assert payout_month(2026, 1, 6) == (2027, 6)


def test_other_events_credit_nothing() -> None:
    """Only the weeks of flexibility count."""
    flex = _rules().flexibility
    assert flex is not None
    account = accrue_weeks(LeaveAccount(()), flex, ("not an event",), 1)
    assert account.balances == ()


def test_the_premium_needs_flexibility_and_its_band() -> None:
    """15% for Studi; nothing without flexibility, without the band or rules."""
    ccnl = load_ccnl(_STUDI)
    day = date(2026, 6, 1)
    assert flexibility_premiums(ccnl, _rules(), day) == {_FLEX: Decimal("0.15")}
    assert flexibility_premiums(ccnl, None, day) == {}
    flex = _rules().flexibility
    assert flex is not None
    other = _rules().model_copy(
        update={"flexibility": flex.model_copy(update={"premium_band": "NONE"})}
    )
    assert flexibility_premiums(ccnl, other, day) == {}
    bare = ccnl.model_copy(update={"work_rules": None})
    assert flexibility_premiums(bare, _rules(), day) == {}


def test_a_month_out_of_the_year_is_rejected() -> None:
    """The programme month is 1 to 12."""
    with pytest.raises(InvalidInputError):
        EmployerProfile(headcount=Headcount(10), flexibility_programme_month=13)


def test_nothing_due_pays_nothing() -> None:
    """No balance of a programme due in the month."""
    flex = _rules().flexibility
    assert flex is not None
    account = LeaveAccount((_OWED,))
    assert flexibility_payout(account, flex, None, 1, (2027, 5)) is None  # type: ignore[arg-type]
