"""The days of a parental leave by the hour: their checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.parental.hourly.inputs import (
    HourlyParentalLeaveEvent,
)
from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveTaken
from ccnl_engine.errors import InvalidInputError

_BORN = date(2025, 6, 1)
_TAKEN = ParentalLeaveTaken(0, 0, 0)


def _hours(*days: int, hours: str = "4") -> tuple[LeaveHours, ...]:
    return tuple(LeaveHours(date(2026, 3, d), Decimal(hours)) for d in days)


def test_the_leave_is_dated_and_cut_to_the_month() -> None:
    """The first day dates it; a run takes its days and hours."""
    leave = HourlyParentalLeaveEvent(_hours(30, 31), _BORN, _TAKEN, Decimal(8))

    assert leave.event_date == date(2026, 3, 30)
    assert leave.within(date(2026, 3, 31), date(2026, 4, 30)) == (
        date(2026, 3, 31),
        date(2026, 3, 31),
    )
    assert leave.within(date(2026, 4, 1), date(2026, 4, 30)) is None
    assert leave.hours_within(date(2026, 3, 1), date(2026, 3, 31)) == Decimal(8)
    empty = leave.hours_within(date(2026, 4, 1), date(2026, 4, 30))
    assert (empty, type(empty)) == (Decimal(0), Decimal)


@pytest.mark.parametrize(
    ("hours", "average", "born", "match"),
    [
        ((), Decimal(8), _BORN, "non-empty tuple"),
        (_hours(2), Decimal(8), _BORN, "even number"),
        (_hours(3, 2), Decimal(8), _BORN, "in order"),
        (_hours(2, 3, hours="3"), Decimal(8), _BORN, "half of average_daily_hours"),
        (_hours(2, 3), Decimal(8), date(2026, 3, 3), "precede child_born_on"),
    ],
)
def test_wrong_days_are_rejected(
    hours: tuple[LeaveHours, ...], average: Decimal, born: date, match: str
) -> None:
    """Whole days of leave, in order, half the average day each."""
    with pytest.raises(InvalidInputError, match=match) as error:
        HourlyParentalLeaveEvent(hours, born, _TAKEN, average)

    assert (error.value.field, error.value.feature) == (
        "HourlyParentalLeaveEvent.hours",
        "parental_leave",
    )


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"average_daily_hours": Decimal(0)}, "average_daily_hours"),
        ({"average_daily_hours": 8}, "average_daily_hours"),
        ({"protection_ended_on": "2025-09-01"}, "protection_ended_on"),
        ({"single_parent": 1}, "single_parent"),
        ({"taken": (0, 0, 0)}, "taken"),
        ({"child_born_on": "2025-06-01"}, "child_born_on"),
        ({"parental_base_pay": Decimal(1)}, "parental_base_pay"),
    ],
)
def test_wrong_fields_are_rejected(changes: dict[str, object], field: str) -> None:
    """Each field of its type."""
    values: dict[str, object] = {
        "hours": _hours(2, 3),
        "child_born_on": _BORN,
        "taken": _TAKEN,
        "average_daily_hours": Decimal(8),
    } | changes
    with pytest.raises(InvalidInputError) as error:
        HourlyParentalLeaveEvent(**values)  # type: ignore[arg-type]

    assert error.value.field == f"HourlyParentalLeaveEvent.{field}"
