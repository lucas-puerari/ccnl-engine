"""Overtime band collision detection in TimeSupplements."""

from __future__ import annotations

import pytest

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import (
    ProvenanceStatus,
    RuleProvenance,
)
from ccnl_engine.working_time.models import (
    OvertimeBand,
    SupplementBand,
    SupplementWork,
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
                overtime_bands=(band_a, band_b),
            )

    def test_supplement_band_collision_raises(self) -> None:
        """Two bands of one work and role for the same levels raise ValueError."""
        provenance = RuleProvenance(status=ProvenanceStatus.MISSING)
        bands = tuple(
            SupplementBand(
                code=code,
                description=code,
                work=SupplementWork.NIGHT,
                rate=_time_series("0.15"),
                hours_paid_apart=False,
                provenance=provenance,
            )
            for code in ("A", "B")
        )
        with pytest.raises(ValueError, match="Ambiguous SupplementBand collisions"):
            TimeSupplements(supplement_bands=bands)
