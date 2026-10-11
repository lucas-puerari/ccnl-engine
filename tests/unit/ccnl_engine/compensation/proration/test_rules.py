"""Payable days and share of a monthly pay of a partly employed month.

Every expected value is counted on the calendar by hand: 1 February 2026
and 1 March 2026 are Sundays, 1 April 2026 a Wednesday, 1 January 2026 a
Thursday and 1 February 2028 (leap year) a Tuesday.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.compensation.proration.rules import (
    MonthProration,
    month_working_days,
    payable_days,
)

_BY_26 = DailyDivisorMethod.BY_26
_BY_30 = DailyDivisorMethod.BY_30
_BY_HOURLY = DailyDivisorMethod.BY_HOURLY
_BY_MONTH_HOURS = DailyDivisorMethod.BY_MONTH_HOURS


@pytest.mark.parametrize(
    ("first", "last", "expected"),
    [
        # 15 March is a Sunday: 16-21, 23-28, 30-31.
        pytest.param(date(2026, 3, 15), date(2026, 3, 31), 14, id="mid-month-hire"),
        pytest.param(date(2026, 3, 31), date(2026, 3, 31), 1, id="hire-last-day"),
        pytest.param(date(2026, 3, 1), date(2026, 3, 1), 0, id="sunday-only"),
        # April 1-15: Sundays 5 and 12 left out.
        pytest.param(date(2026, 4, 1), date(2026, 4, 15), 13, id="mid-termination"),
        # February 2026: 2-7 and 9-14.
        pytest.param(date(2026, 2, 1), date(2026, 2, 14), 12, id="february"),
        pytest.param(date(2026, 2, 2), date(2026, 2, 28), 24, id="february-hire"),
        # Leap February 2028: 29 days, Sundays 6, 13, 20, 27.
        pytest.param(date(2028, 2, 1), date(2028, 2, 29), 25, id="leap-february"),
        # January 2026 has 27 Mondays to Saturdays; 1 and 6 are holidays.
        pytest.param(date(2026, 1, 1), date(2026, 1, 31), 27, id="27-day-month"),
        pytest.param(date(2026, 1, 1), date(2026, 1, 6), 5, id="holidays-count"),
    ],
)
def test_by_26_counts_mondays_to_saturdays(
    first: date, last: date, expected: int
) -> None:
    """Sundays are not paid days; a weekday public holiday is."""
    assert payable_days(_BY_26, first, last) == expected


@pytest.mark.parametrize(
    ("first", "last", "expected"),
    [
        pytest.param(date(2026, 1, 16), date(2026, 1, 31), 15, id="31-day-to-end"),
        pytest.param(date(2026, 1, 31), date(2026, 1, 31), 1, id="31st-only"),
        pytest.param(date(2026, 4, 16), date(2026, 4, 30), 15, id="30-day-to-end"),
        pytest.param(date(2026, 4, 1), date(2026, 4, 15), 15, id="30-day-from-1st"),
        pytest.param(date(2026, 2, 15), date(2026, 2, 28), 16, id="february-to-end"),
        pytest.param(date(2026, 2, 1), date(2026, 2, 14), 14, id="february-from-1st"),
        pytest.param(date(2028, 2, 1), date(2028, 2, 28), 28, id="leap-before-end"),
        pytest.param(date(2028, 2, 15), date(2028, 2, 29), 16, id="leap-to-end"),
    ],
)
def test_by_30_counts_a_commercial_month(
    first: date, last: date, expected: int
) -> None:
    """A span to the month end runs to day 30; day 31 counts as day 30."""
    assert payable_days(_BY_30, first, last) == expected


def test_by_hourly_counts_mondays_to_fridays() -> None:
    """16-30 April 2026: 16-17, 20-24 and 27-30 are 11 weekdays."""
    assert payable_days(_BY_HOURLY, date(2026, 4, 16), date(2026, 4, 30)) == 11


def test_daily_quota_divides_by_26() -> None:
    """Fourteen payable days are fourteen twenty-sixths of a monthly pay."""
    proration = MonthProration.of(_BY_26, (date(2026, 3, 15), date(2026, 3, 31)))

    assert proration is not None
    assert (proration.units, proration.divisor) == (Decimal(14), Decimal(26))
    assert proration.daily_hours is None
    assert not proration.full


def test_more_payable_days_than_the_divisor_pay_one_month() -> None:
    """2-31 January 2026 holds 26 payable days: a whole monthly pay."""
    proration = MonthProration.of(_BY_26, (date(2026, 1, 2), date(2026, 1, 31)))

    assert proration is not None
    assert proration.full


def test_hourly_quota_reads_the_hourly_divisor() -> None:
    """Eleven weekdays of 7.6 hours are 83.6 of 165 monthly hours."""
    proration = MonthProration.of(
        _BY_HOURLY,
        (date(2026, 4, 16), date(2026, 4, 30)),
        hourly_divisor=Decimal(165),
        daily_hours=Decimal("7.6"),
    )

    assert proration is not None
    assert proration.units == Decimal("83.6")
    assert proration.divisor == Decimal(165)


@pytest.mark.parametrize(
    ("hourly_divisor", "daily_hours"),
    [
        pytest.param(None, Decimal("7.6"), id="no-hourly-divisor"),
        pytest.param(Decimal(165), None, id="no-daily-hours"),
    ],
)
def test_hourly_quota_without_its_figures_is_no_rule(
    hourly_divisor: Decimal | None, daily_hours: Decimal | None
) -> None:
    """``by_hourly`` needs both hour figures to give a quota."""
    proration = MonthProration.of(
        _BY_HOURLY,
        (date(2026, 4, 16), date(2026, 4, 30)),
        hourly_divisor=hourly_divisor,
        daily_hours=daily_hours,
    )

    assert proration is None


def test_a_quota_of_one_25th_has_no_proration() -> None:
    """The CCNL states 1/25 but not which days are payable: no rule applies."""
    span = (date(2026, 6, 15), date(2026, 6, 30))

    assert MonthProration.of(DailyDivisorMethod.BY_25, span) is None


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        # March 2026: 2-6, 9-13, 16-20, 23-27, 30-31.
        pytest.param(date(2026, 3, 15), 22, id="march"),
        # February 2026: four whole weeks from Monday 2.
        pytest.param(date(2026, 2, 1), 20, id="february"),
        # January 2026: 1-2, 5-9, 12-16, 19-23, 26-30; holidays 1 and 6 count.
        pytest.param(date(2026, 1, 31), 22, id="holidays-count"),
        # Leap February 2028: 1-4, 7-11, 14-18, 21-25, 28-29.
        pytest.param(date(2028, 2, 29), 21, id="leap-february"),
    ],
)
def test_month_working_days_are_its_mondays_to_fridays(
    day: date, expected: int
) -> None:
    """The divisor of ``by_month_hours`` changes with the month."""
    assert month_working_days(day) == Decimal(expected)


def test_month_hours_quota_divides_by_the_working_days_of_the_month() -> None:
    """16-31 March 2026: 16-20, 23-27 and 30-31 are 12 of 22 working days."""
    proration = MonthProration.of(
        _BY_MONTH_HOURS, (date(2026, 3, 16), date(2026, 3, 31))
    )

    assert proration is not None
    assert (proration.units, proration.divisor) == (Decimal(12), Decimal(22))
    assert proration.daily_hours is None
    assert not proration.full
