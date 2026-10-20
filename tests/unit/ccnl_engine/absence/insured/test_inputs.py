"""The events of an absence an insurer pays: their days and their checks."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.absence.insured.inputs import MaternityLeaveEvent, WorkInjuryEvent
from ccnl_engine.errors import InvalidInputError

_MARCH = (date(2026, 3, 1), date(2026, 3, 31))


def test_a_leave_is_dated_by_its_first_day() -> None:
    """The run allocates the leave by the day it starts."""
    leave = MaternityLeaveEvent(date(2026, 2, 20), date(2026, 7, 19))

    assert leave.event_date == date(2026, 2, 20)
    assert leave.within(*_MARCH) == _MARCH


def test_an_injury_is_dated_by_the_injury_day() -> None:
    """The inability is cut to the month, the injury day included."""
    injury = WorkInjuryEvent(date(2026, 3, 10), date(2026, 4, 5))

    assert injury.event_date == date(2026, 3, 10)
    assert injury.within(*_MARCH) == (date(2026, 3, 10), date(2026, 3, 31))
    assert injury.within(date(2026, 5, 1), date(2026, 5, 31)) is None


@pytest.mark.parametrize(
    ("build", "field"),
    [
        (
            lambda: MaternityLeaveEvent(date(2026, 3, 2), date(2026, 3, 1)),
            "MaternityLeaveEvent.ended_on",
        ),
        (
            lambda: MaternityLeaveEvent("2026-03-01", date(2026, 3, 1)),  # type: ignore[arg-type]
            "MaternityLeaveEvent.started_on",
        ),
        (
            lambda: WorkInjuryEvent(date(2026, 3, 2), date(2026, 3, 1)),
            "WorkInjuryEvent.ended_on",
        ),
        (
            lambda: WorkInjuryEvent(date(2026, 3, 2), None),  # type: ignore[arg-type]
            "WorkInjuryEvent.ended_on",
        ),
    ],
)
def test_an_event_ending_before_it_starts_is_rejected(
    build: object, field: str
) -> None:
    """A day must be a date, and the absence must not end before it starts."""
    with pytest.raises(InvalidInputError) as info:
        build()  # type: ignore[operator]

    assert info.value.field == field
