"""The hours of an insured permit or rest: their checks."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.errors import InvalidInputError


@pytest.mark.parametrize(
    ("day", "hours", "field"),
    [
        (date(2026, 3, 2), Decimal(0), "LeaveHours.hours"),
        (date(2026, 3, 2), Decimal(25), "LeaveHours.hours"),
        (date(2026, 3, 2), 4, "LeaveHours.hours"),
        ("2026-03-02", Decimal(4), "LeaveHours.day"),
    ],
)
def test_hours_are_dated_above_zero_and_within_a_day(
    day: date, hours: Decimal, field: str
) -> None:
    """A date and at most 24 hours, as a Decimal."""
    with pytest.raises(InvalidInputError, match=field) as error:
        LeaveHours(day, hours)

    assert (error.value.field, error.value.feature) == (field, "insured_absence_hours")
