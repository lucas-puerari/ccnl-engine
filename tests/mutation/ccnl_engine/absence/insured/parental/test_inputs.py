"""A parental leave and the leave taken before it: their checks."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.absence.insured.parental.inputs import (
    ParentalLeaveEvent,
    ParentalLeaveTaken,
)
from ccnl_engine.errors import InvalidInputError

_BORN = date(2025, 6, 1)


def test_a_leave_is_dated_by_its_first_day_and_cut_to_the_month() -> None:
    """The run allocates the leave by the day it starts."""
    leave = ParentalLeaveEvent(
        date(2026, 2, 20), date(2026, 3, 10), _BORN, ParentalLeaveTaken(0, 0, 0)
    )

    assert leave.event_date == date(2026, 2, 20)
    assert leave.within(date(2026, 3, 1), date(2026, 3, 31)) == (
        date(2026, 3, 1),
        date(2026, 3, 10),
    )
    assert leave.within(date(2026, 4, 1), date(2026, 4, 30)) is None


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"ended_on": date(2026, 2, 1)}, "must not precede started_on"),
        ({"child_born_on": date(2026, 3, 2)}, "must not precede child_born_on"),
        ({"taken": 0}, "ParentalLeaveEvent.taken"),
        ({"single_parent": None}, "ParentalLeaveEvent.single_parent"),
        ({"protection_ended_on": "2025-09-01"}, "protection_ended_on"),
        ({"child_born_on": "2025-06-01"}, "ParentalLeaveEvent.child_born_on"),
        ({"parental_base_pay": 1}, "ParentalLeaveEvent.parental_base_pay"),
    ],
)
def test_a_wrong_leave_is_rejected(kwargs: dict[str, object], match: str) -> None:
    """Each field is checked when the event is built."""
    fields: dict[str, object] = {
        "started_on": date(2026, 3, 1),
        "ended_on": date(2026, 3, 31),
        "child_born_on": _BORN,
        "taken": ParentalLeaveTaken(0, 0, 0),
    }
    with pytest.raises(InvalidInputError, match=match) as error:
        ParentalLeaveEvent(**(fields | kwargs))  # type: ignore[arg-type]

    assert error.value.feature == "parental_leave"
    assert (error.value.field or "").startswith("ParentalLeaveEvent.")


@pytest.mark.parametrize("name", ["own_days", "enhanced_days", "shared_days"])
def test_a_counter_is_a_non_negative_int(name: str) -> None:
    """INPS keeps its counters in whole days."""
    with pytest.raises(InvalidInputError, match=f"ParentalLeaveTaken.{name}") as e:
        ParentalLeaveTaken(
            **({"own_days": 0, "enhanced_days": 0, "shared_days": 0} | {name: -1})
        )

    assert e.value.feature == "parental_leave"


def test_a_leave_of_the_birth_day_alone_is_valid() -> None:
    """One day, the day of the birth, is a leave of one day."""
    leave = ParentalLeaveEvent(_BORN, _BORN, _BORN, ParentalLeaveTaken(0, 0, 0))

    assert leave.within(_BORN, _BORN) == (_BORN, _BORN)
