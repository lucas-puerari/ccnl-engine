"""The days of a permit to assist a disabled person: their checks."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
from ccnl_engine.errors import InvalidInputError

_MARCH = (date(2026, 3, 1), date(2026, 3, 31))


def test_the_permits_are_dated_by_their_first_day_and_cut_to_the_month() -> None:
    """The run pays the days of its month."""
    permits = DisabilityPermitEvent((date(2026, 3, 30), date(2026, 4, 2)))

    assert permits.event_date == date(2026, 3, 30)
    assert permits.within(*_MARCH) == (date(2026, 3, 30), date(2026, 3, 30))
    assert permits.within(date(2026, 5, 1), date(2026, 5, 31)) is None


@pytest.mark.parametrize(
    ("days", "match"),
    [
        ((), "non-empty tuple"),
        ([date(2026, 3, 2)], "non-empty tuple"),
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
