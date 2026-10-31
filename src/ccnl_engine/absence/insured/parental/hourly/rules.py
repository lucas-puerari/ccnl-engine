"""The rate INPS pays each day of a parental leave taken by the hour.

INPS counts and pays the leave by the hour by the day (circ. 152/2015 par.
2.2): two days of half the average day are one day of leave, which takes
one day of the counters and its rate (:class:`~ccnl_engine.absence.\
insured.parental.rules._Counters`), and each of the two days is paid half
of the daily indemnity at that rate.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.parental.rules import (
    _add_years,
    _Counters,
    cohort_unknown,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.parental.hourly.inputs import (
        HourlyParentalLeaveEvent,
    )
    from ccnl_engine.absence.insured.parental.models import ParentalRates

__all__ = ["allocate_hours", "hours_indemnity"]

_ZERO = Decimal(0)
_HALF = Decimal(2)


def allocate_hours(
    event: HourlyParentalLeaveEvent, rates: ParentalRates
) -> tuple[dict[date, Decimal | None], bool]:
    """Return the rate of each day of ``event`` and whether the cohort is open.

    Returns:
        The share INPS pays on each day (``None`` beyond the indemnified
        months), and whether the unstated end of the protected leave could
        give more enhanced months.

    Raises:
        InvalidInputError: When a day reaches the child's age the leave
            ends at.
    """
    days = [item.day for item in event.hours]
    if days[-1] >= _add_years(event.child_born_on, rates.child_age_years):
        msg = (
            "HourlyParentalLeaveEvent.hours must precede the child's "
            f"{rates.child_age_years}th birthday"
        )
        raise InvalidInputError(
            msg, field="HourlyParentalLeaveEvent.hours", feature="parental_leave"
        )
    counters = _Counters(event, rates)
    result: dict[date, Decimal | None] = {}
    for first, second in zip(days[::2], days[1::2], strict=True):
        result[first] = result[second] = counters.take(first)
    return result, cohort_unknown(event, rates, result, counters)


def hours_indemnity(
    rates: dict[date, Decimal | None], first: date, last: date, daily: Decimal
) -> Decimal:
    """Return the INPS indemnity of the days of leave in ``first``-``last``.

    Returns:
        Half the daily base at the rate of each day, rounded once.
    """
    shares = (r or _ZERO for d, r in rates.items() if first <= d <= last)
    return money(daily * sum(shares, _ZERO) / _HALF)
