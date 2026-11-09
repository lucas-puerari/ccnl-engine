"""Optional-leave holiday supplement after the INPS and CCNL daily shares."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.maternity_holiday import MaternityHoliday
    from ccnl_engine.absence.insured.rules import MonthPay


def covered_parental_holidays(
    target: MaternityHoliday | None,
    first: date,
    last: date,
    patron_saint_day: str | None,
) -> frozenset[date]:
    """Return the dates covered by an optional-leave holiday clause.

    Returns:
        Covered dates, or none without a holiday target.
    """
    return (
        frozenset()
        if target is None
        else target.holidays(first, last, patron_saint_day)
    )


def parental_holiday_units(
    holidays: frozenset[date],
    in_span: list[date],
    rates: dict[date, Decimal | None],
) -> int:
    """Count the indemnified, non-Sunday holidays of the optional leave.

    Returns:
        The number of holiday days carrying the employer supplement.
    """
    return sum(
        day in in_span and day.weekday() != 6 and rates.get(day) is not None
        for day in holidays
    )


def parental_holiday_extra(
    target: MaternityHoliday | None,
    first: date,
    last: date,
    pay: MonthPay,
    daily: Decimal,
    rates: dict[date, Decimal | None],
    topped_up: list[date],
    top_up_rate: Decimal,
    sixth_days: list[date],
    sixth_rate: Decimal,
    holidays: frozenset[date],
) -> Decimal:
    """Return the remaining employer share on holidays inside optional leave.

    Returns:
        The sum of daily shortfalls to the contractual daily quota.
    """
    if target is None:
        return Decimal(0)
    extra = Decimal(0)
    for day in holidays:
        if not first <= day <= last or day.weekday() == 6 or rates.get(day) is None:
            continue
        insurer = (rates[day] or Decimal(0)) * daily
        ordinary = Decimal(0)
        if day in topped_up:
            ordinary = max(top_up_rate * daily - insurer, Decimal(0))
        if day in sixth_days:
            ordinary = max(ordinary, sixth_rate * daily - insurer, Decimal(0))
        extra += max(
            target.rate * pay.deducted(day, day)[1] - insurer - ordinary,
            Decimal(0),
        )
    return money(extra)
