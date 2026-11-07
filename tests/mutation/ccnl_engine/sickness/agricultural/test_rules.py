"""The days a year INPS pays an operaio agricolo a tempo determinato."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.agricultural.inputs import AgriculturalDays
from ccnl_engine.sickness.agricultural.rules import (
    AgriculturalLimit,
    agricultural_limit,
)
from ccnl_engine.sickness.indemnity.models import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)

_INPS = InpsSickPayRates(
    carenza_days=3,
    bands=[SickPayBand(day_from=4, day_to=180, rate=Decimal("0.50"))],
    annual_max_days=180,
    coverage=(SickPayCoverage(covered=True, source="test: every worker"),),
)


@pytest.mark.parametrize(
    ("previous", "current", "days"),
    [
        (51, 0, 51),
        (120, 0, 120),
        (200, 0, 180),
        (50, 51, 30),
        (51, 51, 51),
        (50, 50, 0),
        (0, 0, 0),
    ],
)
def test_the_days_of_the_elenchi(previous: int, current: int, days: int) -> None:
    """51 of the year before: theirs, at most 180; else 51 now: 30."""
    found = agricultural_limit(AgriculturalDays(previous, current), _INPS)

    assert found == AgriculturalLimit(days, 3)
    assert found is not None
    assert found.direct_after == 0


def test_no_days_stated_no_limit() -> None:
    """The fact left out keeps the year maximum."""
    assert agricultural_limit(None, _INPS) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [("previous_year", -1), ("current_year", 367), ("previous_year", "51")],
)
def test_the_days_are_counts_of_a_year(field: str, value: object) -> None:
    """An int in [0, 366]."""
    counts: dict[str, object] = {"previous_year": 51, "current_year": 0}
    counts[field] = value
    with pytest.raises(InvalidInputError) as error:
        AgriculturalDays(**counts)  # type: ignore[arg-type]

    assert error.value.field == f"AgriculturalDays.{field}"
