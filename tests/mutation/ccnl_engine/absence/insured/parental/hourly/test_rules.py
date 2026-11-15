"""The days of leave a leave by the hour makes, with the CCNL hours or not.

INPS circ. 152/2015 par. 2.2, example 1: "una giornata di congedo parentale
è equivalente a 6 ore": twelve hours are two days of leave.  Under the
general criterion of art. 32 c. 1-ter two days of half the average day are
one day of leave.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction

import pytest

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.parental.hourly.rules import (
    HourlyDays,
    allocate_hours,
    hourly_top_up,
    hours_indemnity,
)
from ccnl_engine.absence.insured.parental.top_up import ParentalTopUp
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import (
    HourlyParentalLeaveEvent,
    LeaveHours,
    ParentalLeaveTaken,
)

_RATES = load_insured_absence_rates().parental
_BORN = date(2025, 6, 1)
_MARCH = (date(2026, 3, 1), date(2026, 3, 31))


def _leave(
    *hours: str, average: str = "8", taken: tuple[int, int, int] = (0, 0, 0)
) -> HourlyParentalLeaveEvent:
    return HourlyParentalLeaveEvent(
        tuple(
            LeaveHours(date(2026, 3, 2 + i), Decimal(h)) for i, h in enumerate(hours)
        ),
        _BORN,
        ParentalLeaveTaken(*taken),
        Decimal(average),
        protection_ended_on=date(2025, 9, 1),
    )


def test_the_ccnl_hours_make_the_days() -> None:
    """6 hours a day of leave: 4 + 4 + 4 hours are two days at 80%."""
    days, _ = allocate_hours(_leave("4", "4", "4"), _RATES, Decimal(6))
    shares = [days.share(d) for d in days.pieces]
    assert shares == [Fraction(2, 3)] * 3
    assert days.leave_days(*_MARCH) == 2
    assert days.pieces[date(2026, 3, 3)] == (
        (Fraction(1, 3), _RATES.enhanced_rate),
        (Fraction(1, 3), _RATES.enhanced_rate),
    )
    assert hours_indemnity(days, *_MARCH, Decimal(100)) == Decimal("160.00")


def test_a_day_split_across_two_rates() -> None:
    """The last enhanced day ends inside 3 March: its parts take each rate."""
    month = _RATES.month_days
    enhanced = _RATES.enhanced_months(date(2026, 3, 2), date(2025, 9, 1), _BORN)
    used = enhanced * month - 1
    leave = _leave("4", "4", "4", taken=(used, used, 0))
    days, _ = allocate_hours(leave, _RATES, Decimal(6))
    (first, second) = days.pieces[date(2026, 3, 3)]
    assert first == (Fraction(1, 3), _RATES.enhanced_rate)
    assert second == (Fraction(1, 3), _RATES.indemnity_rate)
    assert (
        days.rate(date(2026, 3, 3))
        == (_RATES.enhanced_rate + _RATES.indemnity_rate) / 2
    )


@pytest.mark.parametrize(
    ("hours", "day_hours", "match"),
    [
        (("4",), None, "even number"),
        (("3", "3"), None, "half of average_daily_hours"),
        (("4", "4"), Decimal(6), "whole days of leave of 6 hours"),
    ],
)
def test_hours_that_make_no_whole_day_are_rejected(
    hours: tuple[str, ...], day_hours: Decimal | None, match: str
) -> None:
    """Whole days of leave, under the criterion or the CCNL hours."""
    with pytest.raises(InvalidInputError, match=match):
        allocate_hours(_leave(*hours), _RATES, day_hours)


def test_the_criterion_keeps_its_pairs() -> None:
    """Two half days are one day of leave, each half at its rate."""
    days, _ = allocate_hours(_leave("4", "4"), _RATES)
    assert days.leave_days(*_MARCH) == 1
    assert days.rates() == {
        date(2026, 3, 2): _RATES.enhanced_rate,
        date(2026, 3, 3): _RATES.enhanced_rate,
    }


def test_beyond_the_months_a_day_has_no_rate() -> None:
    """No rate on a part: the day has none and pays nothing for it."""
    days = HourlyDays({date(2026, 3, 2): ((Fraction(1), None),)})
    assert days.rate(date(2026, 3, 2)) is None
    assert hours_indemnity(days, *_MARCH, Decimal(100)) == 0
    assert hourly_top_up(
        _leave("4", "4"), days, _MARCH, Decimal(100), None, Decimal("0.3")
    ) == (
        Decimal(0),
        Decimal(0),
    )


def test_the_top_up_skips_days_out_of_its_reach() -> None:
    """After the run, before the rule, beyond the months or at another rate."""
    rule = ParentalTopUp.model_validate({
        "rate": "0.5",
        "max_days": 30,
        "valid_from": "2026-03-03",
        "only_standard_rate": True,
        "provenance": {"status": "missing"},
    })
    days = HourlyDays({
        date(2026, 3, 2): ((Fraction(1, 2), Decimal("0.3")),),
        date(2026, 3, 3): ((Fraction(1, 2), None),),
        date(2026, 3, 4): ((Fraction(1, 2), Decimal("0.8")),),
        date(2026, 3, 5): ((Fraction(1, 2), Decimal("0.3")),),
        date(2026, 4, 1): ((Fraction(1, 2), Decimal("0.3")),),
    })
    leave = replace(_leave("4", "4"), topped_up_days_before=Decimal(0))
    amount, covered = hourly_top_up(
        leave, days, _MARCH, Decimal(100), rule, Decimal("0.3")
    )
    assert (amount, covered) == (Decimal("10.00"), Decimal("0.5"))
