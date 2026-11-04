"""A holiday falling on the worker's weekly rest day, Turismo art. 127 c. 4.

FIPE art. 131 c. 4, art. 133 c. 4 and art. 159 (CCNL Pubblici Esercizi
2018) carry the same words and divisor for both FIPE rulesets, as do
Industria Turistica arts. 86, 87 and 108 (2016) and Turismo Confesercenti
arts. 117, 118 and 142 (2003).

"A tutto il personale assente nelle giornate di festività, per riposo
settimanale [...] dovrà essere corrisposta una giornata di retribuzione
contrattuale" (art. 127 c. 4, CCNL Turismo 2010), 4 November included on
its own date (art. 128 c. 4); the daily pay is the monthly pay over 26
(art. 150).  L. 260/1949 art. 5 still pays the statutory holidays on the
Sunday of the calendar.  In 2026 Easter Monday is 6 April, 25 April a
Saturday, 4 October and 1 November Sundays, 4 November a Wednesday; 25
April 2027 is a Sunday.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.compensation.sunday_holiday.services import (
    CAPABILITY,
    CLAUSE_LIMITATION,
)
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_TURISMO = ("turismo-federalberghi", "4")
_COMMERCIO = ("commercio-confcommercio", "4")
_FIPE = ("pubblici-esercizi-fipe-angem", "4")
_FIPE_COLLETTIVA = ("pubblici-esercizi-fipe-angem-ristorazione-collettiva", "4")
_FEDERTURISMO = ("industria-turistica-federturismo", "B1")
_CONFESERCENTI = ("turismo-confesercenti", "4")
_SAME_CLAUSE = [_FIPE, _FIPE_COLLETTIVA, _FEDERTURISMO, _CONFESERCENTI]
_SAME_IDS = ["fipe", "collettiva", "federturismo", "confesercenti"]
_CENT = Decimal("0.01")


def _run(
    ccnl: tuple[str, str], year: int, month: int, rest: Weekday = Weekday.SUNDAY
) -> PeriodResult:
    slug, level = ccnl
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20)),
            period_id=PeriodId(year, month),
            payment_date=date(year, month, 27),
            ccnl_id=slug,
            level_code=level,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            sector=EmploymentSector.PRIVATE,
            weekly_rest_day=rest,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _paid(result: PeriodResult) -> tuple[str, Decimal] | None:
    """Return the days and amount of the quota.

    Returns:
        The days and amount of the one decision, ``None`` without one.
    """
    decisions = [d for d in result.decisions if d.capability == CAPABILITY]
    if not decisions:
        return None
    (decision,) = decisions
    assert decision.amount is not None
    return str(decision.inputs["days"]), decision.amount


def _limited(result: PeriodResult) -> bool:
    return CLAUSE_LIMITATION in {lim.id for lim in result.limitations}


def _quota(result: PeriodResult) -> Decimal:
    """Return the daily pay of art. 150.

    Returns:
        The monthly pay of the run less the quota, over 26.
    """
    paid = _paid(result)
    assert paid is not None
    monthly = result.period_gross - paid[1]
    return (monthly / 26).quantize(_CENT, rounding=ROUND_HALF_UP)


@pytest.mark.parametrize(
    ("year", "month", "rest", "days"),
    [
        (2026, 11, Weekday.SUNDAY, "2026-11-01"),
        (2026, 11, Weekday.WEDNESDAY, "2026-11-04"),
        (2026, 4, Weekday.MONDAY, "2026-04-06"),
        (2026, 4, Weekday.SATURDAY, "2026-04-25"),
        (2027, 4, Weekday.MONDAY, "2027-04-25"),
    ],
    ids=[
        "ognissanti-on-sunday-rest",
        "fourth-november-on-wednesday-rest",
        "easter-monday-on-monday-rest",
        "liberation-on-saturday-rest",
        "liberation-on-sunday-by-law",
    ],
)
def test_a_holiday_on_the_rest_day_pays_one_day(
    year: int, month: int, rest: Weekday, days: str
) -> None:
    """One twenty-sixth of the monthly pay for each such holiday."""
    result = _run(_TURISMO, year, month, rest)

    assert _paid(result) == (days, _quota(result))
    assert not _limited(result)


def test_ognissanti_and_the_first_sunday_are_one_day() -> None:
    """1 November 2026 is not also 4 November: the 4th is a Wednesday."""
    result = _run(_TURISMO, 2026, 11)

    assert _paid(result) == ("2026-11-01", _quota(result))


@pytest.mark.parametrize(
    ("year", "month", "rest"),
    [
        (2026, 11, Weekday.MONDAY),
        (2026, 4, Weekday.SUNDAY),
        (2027, 3, Weekday.SATURDAY),
    ],
    ids=["ognissanti-on-sunday", "holidays-on-workdays", "easter-monday-workday"],
)
def test_a_holiday_off_the_rest_day_pays_nothing(
    year: int, month: int, rest: Weekday
) -> None:
    """A clause holiday on a Sunday that is not the rest day is not paid."""
    result = _run(_TURISMO, year, month, rest)

    assert _paid(result) is None
    assert not _limited(result)


def test_a_recent_holiday_on_the_rest_day_is_open() -> None:
    """4 October 2026, not in art. 127, records the limitation."""
    result = _run(_TURISMO, 2026, 10)

    assert _paid(result) == ("2026-10-04", Decimal(0))
    assert _limited(result)


@pytest.mark.parametrize("ccnl", _SAME_CLAUSE, ids=_SAME_IDS)
@pytest.mark.parametrize(
    ("year", "month", "rest", "days"),
    [
        (2026, 11, Weekday.WEDNESDAY, "2026-11-04"),
        (2026, 12, Weekday.FRIDAY, "2026-12-25"),
        (2026, 4, Weekday.SATURDAY, "2026-04-25"),
    ],
    ids=["fourth-november", "christmas-on-friday-rest", "liberation-on-saturday"],
)
def test_the_same_clause_pays_a_holiday_on_the_rest_day(
    ccnl: tuple[str, str], year: int, month: int, rest: Weekday, days: str
) -> None:
    """The holiday and 4 November on the rest day pay one twenty-sixth."""
    result = _run(ccnl, year, month, rest)

    assert _paid(result) == (days, _quota(result))
    assert not _limited(result)


@pytest.mark.parametrize("ccnl", _SAME_CLAUSE, ids=_SAME_IDS)
def test_the_same_clause_pays_nothing_off_the_rest_day(ccnl: tuple[str, str]) -> None:
    """1 November 2026 is a Sunday, the rest day a Monday: nothing is due."""
    result = _run(ccnl, 2026, 11, Weekday.MONDAY)

    assert _paid(result) is None


def test_a_sunday_clause_ignores_the_rest_day() -> None:
    """Commercio art. 154 pays 1 November 2026 on the Sunday, rest or not."""
    sunday = _run(_COMMERCIO, 2026, 11)
    monday = _run(_COMMERCIO, 2026, 11, Weekday.MONDAY)

    assert _paid(monday) == _paid(sunday)
    paid = _paid(sunday)
    assert paid is not None
    assert paid[0] == "2026-11-01,2026-11-01"
