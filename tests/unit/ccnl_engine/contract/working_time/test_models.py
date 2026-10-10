"""Overtime band collision detection in TimeSupplements."""

from __future__ import annotations

import pytest

from ccnl_engine.contract.identity.rules_validity import TimeSeries
from ccnl_engine.contract.working_time.models import (
    OvertimeBand,
    TimeSupplementKind,
    TimeSupplements,
    WorkKind,
)
from tests.unit.ccnl_engine.builders import _series


def _time_series(value: str) -> TimeSeries:
    """Build a single-period TimeSeries for the given value.

    Returns:
        A :class:`TimeSeries` valid from 2020-01-01 with no end date.
    """
    return TimeSeries.model_validate(_series(value))


class TestMiscCoverageGaps:
    """Overtime band validation in the working time model."""

    def test_overtime_band_collision_raises(self) -> None:
        """Two unconditional bands for the same WorkKind raise ValueError."""
        band_a = OvertimeBand(
            code="A",
            description="Band A",
            kind=TimeSupplementKind.PERCENTAGE,
            rate=_time_series("0.25"),
            applies_to_kinds=(WorkKind.WEEKDAY,),
        )
        band_b = OvertimeBand(
            code="B",
            description="Band B",
            kind=TimeSupplementKind.PERCENTAGE,
            rate=_time_series("0.30"),
            applies_to_kinds=(WorkKind.WEEKDAY,),
        )
        with pytest.raises(ValueError, match="Ambiguous OvertimeBand collisions"):
            TimeSupplements(
                hourly_base_method="minimo_tabellare",
                overtime_bands=(band_a, band_b),
            )
