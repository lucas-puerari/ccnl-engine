"""The rate INPS pays each day of a parental leave taken by the hour.

INPS counts and pays the leave by the hour by the day (circ. 152/2015 par.
2.2): the hours that make a day of leave take one day of the counters and
its rate (:class:`~ccnl_engine.absence.insured.parental.rules._Counters`).
Under the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 a day of
leave is two days of half the average daily hours; a CCNL that sets its own
hours to a day of leave (art. 32 c. 1-bis: ARAN 6 hours) makes each day the
share its hours are of them ("una giornata di congedo parentale è
equivalente a 6 ore", circ. 152/2015 example 1).  A day whose hours fall in
two days of leave takes each one's rate for its part.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from fractions import Fraction
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
    from ccnl_engine.absence.insured.parental.top_up import ParentalTopUp

__all__ = ["HourlyDays", "allocate_hours", "hourly_top_up", "hours_indemnity"]

_ZERO = Decimal(0)
_FIELD = "HourlyParentalLeaveEvent.hours"
_HALF = Fraction(1, 2)

#: Part of a day of leave and its rate, ``None`` beyond the indemnified months.
Piece = tuple[Fraction, Decimal | None]


@dataclass(frozen=True)
class HourlyDays:
    """The days of a leave by the hour and the days of leave they make.

    Attributes:
        pieces: Each day's parts of a day of leave, with their rates.
    """

    pieces: dict[date, tuple[Piece, ...]] = field(default_factory=dict)

    def share(self, day: date) -> Fraction:
        """Return the part of a day of leave ``day`` takes.

        Returns:
            The sum of its parts.
        """
        return sum((part for part, _ in self.pieces[day]), Fraction(0))

    def rate(self, day: date) -> Decimal | None:
        """Return the rate of ``day``.

        Returns:
            The rate of its parts, weighted by their size; ``None`` when a
            part has none.
        """
        paid = Fraction(0)
        for part, rate in self.pieces[day]:
            if rate is None:
                return None
            paid += part * Fraction(rate)
        return _decimal(paid / self.share(day))

    def leave_days(self, first: date, last: date) -> Decimal:
        """Return the days of leave the days in ``first``-``last`` make.

        Returns:
            The sum of their shares.
        """
        total = sum(
            (self.share(day) for day in self.pieces if first <= day <= last),
            Fraction(0),
        )
        return _decimal(total)

    def rates(self) -> dict[date, Decimal | None]:
        """Return the rate of each day.

        Returns:
            The rate of each day of the event.
        """
        return {day: self.rate(day) for day in self.pieces}


def _decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def _shares(
    event: HourlyParentalLeaveEvent, day_hours: Decimal | None
) -> list[tuple[date, Fraction]]:
    """Return the part of a day of leave each day of ``event`` takes.

    Returns:
        Each day with its share: a half under the general criterion, its
        hours over ``day_hours`` otherwise.

    Raises:
        InvalidInputError: Under the general criterion, when a day is not
            half the average daily hours or the days are odd in number;
            with the CCNL hours, when the hours do not make whole days.
    """
    if day_hours is None:
        half = event.average_daily_hours / 2
        if any(item.hours != half for item in event.hours):
            msg = (
                f"{_FIELD} must be half of average_daily_hours ({half}) on each "
                "day: the general criterion of art. 32 c. 1-ter"
            )
            raise InvalidInputError(msg, field=_FIELD, feature="parental_leave")
        if len(event.hours) % 2:
            msg = f"{_FIELD} must hold whole days of leave: an even number"
            raise InvalidInputError(msg, field=_FIELD, feature="parental_leave")
        return [(item.day, _HALF) for item in event.hours]
    unit = Fraction(day_hours)
    shares = [(item.day, Fraction(item.hours) / unit) for item in event.hours]
    total = sum((share for _, share in shares), Fraction(0))
    if total.denominator != 1:
        msg = (
            f"{_FIELD} must make whole days of leave of {day_hours} hours, the "
            "CCNL equivalence (INPS circ. 152/2015 par. 2.2)"
        )
        raise InvalidInputError(msg, field=_FIELD, feature="parental_leave")
    return shares


def allocate_hours(
    event: HourlyParentalLeaveEvent,
    rates: ParentalRates,
    day_hours: Decimal | None = None,
) -> tuple[HourlyDays, bool]:
    """Return the days of leave each day of ``event`` takes, with their rates.

    Args:
        event: The leave by the hour.
        rates: The statutory rates and counters.
        day_hours: Hours of a day of leave the CCNL sets; ``None`` for the
            general criterion.

    Returns:
        Each day's parts of a day of leave and their rates (``None``
        beyond the indemnified months), and whether the unstated end of
        the protected leave could give more enhanced months.

    Raises:
        InvalidInputError: When a day reaches the child's age the leave
            ends at, or the hours do not make whole days of leave.
    """
    days = [item.day for item in event.hours]
    if days[-1] >= _add_years(event.child_born_on, rates.child_age_years):
        msg = f"{_FIELD} must precede the child's {rates.child_age_years}th birthday"
        raise InvalidInputError(msg, field=_FIELD, feature="parental_leave")
    counters = _Counters(event, rates)
    taken: list[Decimal | None] = []
    position = Fraction(0)
    pieces: dict[date, tuple[Piece, ...]] = {}
    for day, share in _shares(event, day_hours):
        parts: list[Piece] = []
        left = share
        while left > 0:
            unit = int(position)
            if unit == len(taken):
                taken.append(counters.take(day))
            part = min(Fraction(unit + 1) - position, left)
            parts.append((part, taken[unit]))
            position += part
            left -= part
        pieces[day] = tuple(parts)
    return HourlyDays(pieces), cohort_unknown(event, rates, days, counters)


def hourly_top_up(
    event: HourlyParentalLeaveEvent,
    days: HourlyDays,
    span: tuple[date, date],
    daily: Decimal,
    rule: ParentalTopUp | None,
    standard_rate: Decimal,
) -> tuple[Decimal, Decimal]:
    """Top up eligible hourly leave in days of leave, including earlier runs.

    Returns:
        The employer supplement and the days of leave it covers in this
        run.  Earlier days of this event consume the cap before the run's.
    """
    if rule is None or event.topped_up_days_before is None:
        return _ZERO, _ZERO
    if rule.only_standard_rate and event.single_parent:
        return _ZERO, _ZERO
    room = max(
        Fraction(0), Fraction(rule.max_days) - Fraction(event.topped_up_days_before)
    )
    amount = Fraction(0)
    covered = Fraction(0)
    for day, part, rate in _eligible(days, span[1], rule, standard_rate):
        used = min(part, room)
        room -= used
        if used and day >= span[0]:
            amount += max(Fraction(0), Fraction(rule.rate) - Fraction(rate)) * used
            covered += used
    return money(_decimal(amount) * daily), _decimal(covered)


def _eligible(
    days: HourlyDays, last: date, rule: ParentalTopUp, standard_rate: Decimal
) -> list[tuple[date, Fraction, Decimal]]:
    """Return the parts of the days of leave the top-up may cover.

    Returns:
        Each part up to ``last``, from the rule's first day, with a rate,
        at the standard rate when the rule takes that one only.
    """
    return [
        (day, part, rate)
        for day, parts in days.pieces.items()
        if day <= last and (rule.valid_from is None or day >= rule.valid_from)
        for part, rate in parts
        if rate is not None and (not rule.only_standard_rate or rate == standard_rate)
    ]


def hours_indemnity(
    days: HourlyDays, first: date, last: date, daily: Decimal
) -> Decimal:
    """Return the INPS indemnity of the days of leave in ``first``-``last``.

    Returns:
        The daily base at the rate of each part of a day of leave, rounded
        once.
    """
    paid = sum(
        (
            part * Fraction(rate)
            for day, parts in days.pieces.items()
            if first <= day <= last
            for part, rate in parts
            if rate is not None
        ),
        Fraction(0),
    )
    return money(daily * _decimal(paid))
