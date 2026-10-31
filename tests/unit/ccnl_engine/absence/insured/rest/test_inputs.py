"""The daily rests of the first year of a child: their checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.rest.inputs import NursingRestEvent
from ccnl_engine.errors import InvalidInputError

_BORN = date(2025, 3, 31)


def _hours(*days: date) -> tuple[LeaveHours, ...]:
    return tuple(LeaveHours(day, Decimal(2)) for day in days)


def test_the_rests_are_dated_and_cut_to_the_month() -> None:
    """The run pays the hours of its month."""
    rests = NursingRestEvent(_hours(date(2026, 2, 27), date(2026, 3, 2)), _BORN)

    assert rests.event_date == date(2026, 2, 27)
    assert rests.within(date(2026, 3, 1), date(2026, 3, 31)) == (
        date(2026, 3, 2),
        date(2026, 3, 2),
    )
    assert rests.within(date(2026, 4, 1), date(2026, 4, 30)) is None
    assert rests.hours_within(date(2026, 2, 1), date(2026, 2, 28)) == Decimal(2)
    day = date(2026, 3, 2)
    assert rests.within(day, day) == (day, day)
    assert rests.hours_within(day, day) == Decimal(2)
    empty = rests.hours_within(date(2026, 4, 1), date(2026, 4, 30))
    assert (empty, type(empty)) == (Decimal(0), Decimal)


def test_the_rests_start_on_the_birth_day() -> None:
    """The day of the birth is in the first year."""
    assert NursingRestEvent(_hours(_BORN), _BORN).event_date == _BORN


def test_the_birth_is_a_date() -> None:
    """A birth day that is not a date is rejected, naming the field."""
    with pytest.raises(InvalidInputError) as error:
        NursingRestEvent(_hours(date(2026, 3, 2)), "2025-03-31")  # type: ignore[arg-type]

    assert (error.value.field, error.value.feature) == (
        "NursingRestEvent.child_born_on",
        "nursing_rests",
    )


@pytest.mark.parametrize(
    ("hours", "born", "match"),
    [
        ((), _BORN, "non-empty tuple"),
        ([LeaveHours(date(2026, 3, 2), Decimal(2))], _BORN, "non-empty tuple"),
        ((date(2026, 3, 2),), _BORN, "LeaveHours"),
        (_hours(date(2026, 3, 3), date(2026, 3, 2)), _BORN, "each day once"),
        (_hours(date(2025, 3, 30)), _BORN, "first year"),
        (_hours(date(2026, 3, 31)), _BORN, "first year"),
    ],
)
def test_wrong_rests_are_rejected(
    hours: tuple[LeaveHours, ...], born: date, match: str
) -> None:
    """In order, each day once, from the birth to the day before one year."""
    with pytest.raises(InvalidInputError, match=match) as error:
        NursingRestEvent(hours, born)

    assert (error.value.field, error.value.feature) == (
        "NursingRestEvent.hours",
        "nursing_rests",
    )


def test_a_child_born_on_29_february_is_one_on_28_february() -> None:
    """The last day of rest is 27 February of the next year."""
    born = date(2024, 2, 29)

    assert NursingRestEvent(_hours(date(2025, 2, 27)), born).hours
    with pytest.raises(InvalidInputError, match="first year"):
        NursingRestEvent(_hours(date(2025, 2, 28)), born)
