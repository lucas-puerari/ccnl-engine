"""The days of a permit to assist a disabled person: their checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
from ccnl_engine.errors import InvalidInputError

_MARCH = (date(2026, 3, 1), date(2026, 3, 31))


def test_the_permits_are_dated_by_their_first_day_and_cut_to_the_month() -> None:
    """The run pays the days of its month."""
    permits = DisabilityPermitEvent((date(2026, 3, 30), date(2026, 4, 2)))

    assert permits.event_date == date(2026, 3, 30)
    assert permits.within(*_MARCH) == (date(2026, 3, 30), date(2026, 3, 30))
    assert permits.within(date(2026, 5, 1), date(2026, 5, 31)) is None


def test_the_hours_count_among_the_days_of_the_month() -> None:
    """An hourly day before the whole days dates the event and the span."""
    permits = DisabilityPermitEvent(
        (date(2026, 3, 10),),
        (
            LeaveHours(date(2026, 3, 2), Decimal(4)),
            LeaveHours(date(2026, 4, 1), Decimal("2.5")),
        ),
    )

    assert permits.event_date == date(2026, 3, 2)
    assert permits.within(*_MARCH) == (date(2026, 3, 2), date(2026, 3, 10))
    assert permits.days_within(*_MARCH) == (date(2026, 3, 10),)
    assert permits.hours_within(*_MARCH) == Decimal(4)
    assert permits.hours_within(date(2026, 5, 1), date(2026, 5, 31)) == 0
    assert permits.within(date(2026, 3, 2), date(2026, 3, 2)) == (
        date(2026, 3, 2),
        date(2026, 3, 2),
    )
    assert permits.hours_within(date(2026, 4, 1), date(2026, 4, 1)) == Decimal("2.5")


def test_a_month_without_hours_sums_to_a_decimal_zero() -> None:
    """No hours in the span: Decimal zero, not the int of an empty sum."""
    hours = DisabilityPermitEvent((date(2026, 3, 2),)).hours_within(*_MARCH)

    assert (hours, type(hours)) == (Decimal(0), Decimal)


@pytest.mark.parametrize(
    ("days", "match"),
    [
        ((), "must hold a day"),
        ([date(2026, 3, 2)], "must be a tuple"),
        (("2026-03-02",), "DisabilityPermitEvent.days"),
        ((date(2026, 3, 3), date(2026, 3, 2)), "in order, each day once"),
        ((date(2026, 3, 2), date(2026, 3, 2)), "in order, each day once"),
    ],
)
def test_wrong_days_are_rejected(days: tuple[date, ...], match: str) -> None:
    """Whole days, in order, each once."""
    with pytest.raises(InvalidInputError, match=match) as error:
        DisabilityPermitEvent(days)

    assert (error.value.field, error.value.feature) == (
        "DisabilityPermitEvent.days",
        "disability_permits",
    )


_HOUR = LeaveHours(date(2026, 3, 2), Decimal(2))


@pytest.mark.parametrize(
    ("days", "hours", "match"),
    [
        ((), [_HOUR], "must be a tuple"),
        ((), (date(2026, 3, 2),), "LeaveHours"),
        ((), (_HOUR, _HOUR), "in order, each day once"),
        (
            (date(2026, 3, 2),),
            (_HOUR,),
            "^DisabilityPermitEvent.hours must not hold a whole day of permit$",
        ),
    ],
)
def test_wrong_hours_are_rejected(
    days: tuple[date, ...], hours: tuple[LeaveHours, ...], match: str
) -> None:
    """Hours on days apart from the whole days, each day once."""
    with pytest.raises(InvalidInputError, match=match) as error:
        DisabilityPermitEvent(days, hours)

    assert (error.value.field, error.value.feature) == (
        "DisabilityPermitEvent.hours",
        "disability_permits",
    )
