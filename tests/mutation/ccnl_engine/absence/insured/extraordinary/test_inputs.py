"""An extraordinary leave: its days and its checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.extraordinary.inputs import ExtraordinaryLeaveEvent
from ccnl_engine.errors import InvalidInputError


def test_a_leave_is_dated_by_its_first_day_and_cut_to_the_month() -> None:
    """The run pays the days of its month."""
    leave = ExtraordinaryLeaveEvent(date(2026, 2, 20), date(2026, 3, 10))

    assert leave.event_date == date(2026, 2, 20)
    assert leave.within(date(2026, 3, 1), date(2026, 3, 31)) == (
        date(2026, 3, 1),
        date(2026, 3, 10),
    )
    assert leave.within(date(2026, 4, 1), date(2026, 4, 30)) is None
    assert ExtraordinaryLeaveEvent(date(2026, 3, 2), date(2026, 3, 2)).within(
        date(2026, 3, 2), date(2026, 3, 2)
    ) == (date(2026, 3, 2), date(2026, 3, 2))


@pytest.mark.parametrize(
    ("kwargs", "match", "field"),
    [
        ({"ended_on": date(2026, 2, 1)}, "must not precede", "ended_on"),
        ({"started_on": "2026-03-01"}, "started_on", "started_on"),
        ({"last_fixed_pay": Decimal(0)}, "last_fixed_pay", "last_fixed_pay"),
        ({"last_fixed_pay": 2000}, "last_fixed_pay", "last_fixed_pay"),
    ],
)
def test_a_wrong_leave_is_rejected(
    kwargs: dict[str, object], match: str, field: str
) -> None:
    """Each field is checked when the event is built."""
    fields: dict[str, object] = {
        "started_on": date(2026, 3, 1),
        "ended_on": date(2026, 3, 31),
    }
    with pytest.raises(InvalidInputError, match=match) as error:
        ExtraordinaryLeaveEvent(**(fields | kwargs))  # type: ignore[arg-type]

    assert (error.value.field, error.value.feature) == (
        f"ExtraordinaryLeaveEvent.{field}",
        "extraordinary_leave",
    )
