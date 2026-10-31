"""The rate INPS pays each day of a parental leave, and the pay of a month.

Art. 34 c. 1 D.Lgs. 151/2001: each parent has three months not
transferable to the other paid at 30% (a sole parent nine), the couple
three further months at 30%; of the months not transferable, those of the
couple the leave's cohort gives are paid at 80% while the child is under
six.  The months after are paid only under the income condition of c. 3,
which the engine does not model: their days are paid nothing.

The days of the leave consume the counters in order.  INPS counts the
calendar months of a span as months and the days of shorter spans thirty
to a month (FAQ congedo parentale 2024, n. 10), so each calendar month of
the span is thirty days: every day one but the last, which takes what is
left (none in a month of 31 days, three in February).  Which days of such
a month a counter ends on when it ends inside the month is not settled by
a source: :attr:`ParentalDays.split` names those days.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from ccnl_engine.absence.insured.parental.hourly.inputs import (
        HourlyParentalLeaveEvent,
    )
    from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveEvent
    from ccnl_engine.absence.insured.parental.models import ParentalRates

__all__ = ["ParentalDays", "allocate", "cohort_unknown", "indemnity"]

_ZERO = Decimal(0)
_MONTHS = 12
_DAY = timedelta(days=1)


@dataclass
class ParentalDays:
    """The rate of each day of a leave and what the engine cannot tell.

    Attributes:
        rates: Share of the daily pay INPS pays on each day; ``None`` on a
            day beyond the indemnified months (income condition of c. 3).
        split: Days of a calendar month not of thirty days a counter ends
            inside of.
        cohort_unknown: Whether the unstated end of the maternity or
            paternity leave could give more enhanced months.
    """

    rates: dict[date, Decimal | None] = field(default_factory=dict)
    split: set[date] = field(default_factory=set)
    cohort_unknown: bool = False


def _add_years(day: date, years: int) -> date:
    year = day.year + years
    return day.replace(
        year=year, day=min(day.day, calendar.monthrange(year, day.month)[1])
    )


def _next_month(day: date) -> date:
    year, month = divmod(day.month, _MONTHS)
    year, month = day.year + year, month + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def _blocks(first: date, last: date) -> Iterator[tuple[list[date], bool]]:
    """Yield the calendar months of ``first``-``last``, then the days left.

    Yields:
        The days of each block and whether it is a whole calendar month.
    """
    cursor = first
    while cursor <= last:
        end = _next_month(cursor) - _DAY
        whole = end <= last
        end = min(end, last)
        yield [cursor + _DAY * i for i in range((end - cursor).days + 1)], whole
        cursor = end + _DAY


class _Counters:
    """The counters of the parent and of the couple, consumed day by day."""

    def __init__(
        self, event: ParentalLeaveEvent | HourlyParentalLeaveEvent, rates: ParentalRates
    ) -> None:
        days, taken = rates.month_days, event.taken
        single = event.single_parent
        self.own_cap = days * (
            rates.single_parent_months if single else rates.own_months
        )
        self.shared_cap = 0 if single else days * rates.shared_months
        self.own, self.enhanced, self.shared = (
            taken.own_days,
            taken.enhanced_days,
            taken.shared_days,
        )
        self.month_days = days
        self.rates = rates
        self.born_on = event.child_born_on
        self.enhanced_until = _add_years(event.child_born_on, rates.enhanced_age_years)
        self.protection = event.protection_ended_on or event.child_born_on

    def take(self, day: date) -> Decimal | None:
        """Consume one day of counter on ``day`` and return its rate.

        Returns:
            The share INPS pays, ``None`` beyond the indemnified months.
        """
        rates = self.rates
        if self.own < self.own_cap:
            self.own += 1
            months = rates.enhanced_months(day, self.protection, self.born_on)
            if day < self.enhanced_until and self.enhanced < months * self.month_days:
                self.enhanced += 1
                return rates.enhanced_rate
            return rates.indemnity_rate
        if self.shared < self.shared_cap:
            self.shared += 1
            return rates.indemnity_rate
        return None


def allocate(event: ParentalLeaveEvent, rates: ParentalRates) -> ParentalDays:
    """Return the rate INPS pays each day of ``event``.

    Returns:
        The rates of the days, the days of a month a counter ends inside of,
        and whether the unstated end of the protected leave matters.

    Raises:
        InvalidInputError: When the leave reaches the child's age the
            leave ends at.
    """
    if event.ended_on >= _add_years(event.child_born_on, rates.child_age_years):
        msg = (
            "ParentalLeaveEvent.ended_on must precede the child's "
            f"{rates.child_age_years}th birthday"
        )
        raise InvalidInputError(
            msg, field="ParentalLeaveEvent.ended_on", feature="parental_leave"
        )
    counters = _Counters(event, rates)
    result = ParentalDays()
    for block, whole in _blocks(event.started_on, event.ended_on):
        _take_block(block, whole, counters, result)
    result.cohort_unknown = cohort_unknown(event, rates, result.rates, counters)
    return result


def cohort_unknown(
    event: ParentalLeaveEvent | HourlyParentalLeaveEvent,
    rates: ParentalRates,
    days: Iterable[date],
    counters: _Counters,
) -> bool:
    """Return whether the unstated end of the protected leave could matter.

    Returns:
        ``True`` when the end is not stated and a later one would give a
        day of ``days`` more months at the enhanced rate.
    """
    if event.protection_ended_on is not None:
        return False
    born = event.child_born_on
    return any(
        rates.enhanced_months(day, date.max, born)
        > rates.enhanced_months(day, born, born)
        for day in days
        if day < counters.enhanced_until
    )


def _take_block(
    block: list[date], whole: bool, counters: _Counters, result: ParentalDays
) -> None:
    """Consume the counters of the days of ``block`` and record their rates.

    A whole calendar month is thirty days of counter: each day one, the
    last what is left.  A day of no counter keeps the rate of the day
    before.
    """
    seen: set[Decimal | None] = set()
    rate: Decimal | None = None
    for index, day in enumerate(block):
        last = index == len(block) - 1
        units = counters.month_days - index if whole and last else 1
        taken = [counters.take(day) for _ in range(units)]
        rate = taken[0] if taken else rate
        seen.update(taken)
        result.rates[day] = rate
    if whole and len(block) != counters.month_days and len(seen) > 1:
        result.split.update(block)


def indemnity(days: ParentalDays, first: date, last: date, daily: Decimal) -> Decimal:
    """Return the INPS indemnity of the days ``first``-``last``.

    Returns:
        The daily base times the rates of the days, rounded to the cent.
    """
    shares = (
        days.rates[first + _DAY * i] or _ZERO for i in range((last - first).days + 1)
    )
    return money(daily * sum(shares, _ZERO))
