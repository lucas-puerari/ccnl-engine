"""Tests for apprenticeship track models.

Each class targets a specific validator branch to satisfy 100 % branch coverage.
"""

from decimal import Decimal

import pytest
from pydantic import TypeAdapter, ValidationError

from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipTrack,
    ApprenticeshipUnderClassification,
)

_ta: TypeAdapter[ApprenticeshipTrack] = TypeAdapter(ApprenticeshipTrack)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pct_period(
    months_from: int,
    months_until: int | None,
    pct: str = "0.80",
) -> dict[str, object]:
    return {"months_from": months_from, "months_until": months_until, "percentage": pct}


def _uc_period(
    months_from: int,
    months_until: int | None,
    levels_below: int = 1,
) -> dict[str, object]:
    return {
        "months_from": months_from,
        "months_until": months_until,
        "levels_below": levels_below,
    }


def _pct_track(*periods: dict[str, object]) -> dict[str, object]:
    return {
        "type": "percentage",
        "name": "standard",
        "destination_levels": ["4"],
        "periods": list(periods),
    }


def _uc_track(*periods: dict[str, object]) -> dict[str, object]:
    return {
        "type": "under_classification",
        "name": "standard",
        "destination_levels": ["4"],
        "periods": list(periods),
    }


# ---------------------------------------------------------------------------
# Period validators
# ---------------------------------------------------------------------------


class TestPeriodValidators:
    """Bounds, percentage range and extra-key rejection on single periods."""

    def test_open_ended_accepted(self) -> None:
        """months_until=None is always accepted."""
        track = _ta.validate_python(_pct_track(_pct_period(0, None)))
        assert isinstance(track, ApprenticeshipPercentage)
        assert track.periods[0].months_until is None

    @pytest.mark.parametrize("until", [6, 5])
    def test_months_until_not_after_from_raises(self, until: int) -> None:
        """months_until <= months_from must raise (both period types)."""
        with pytest.raises(ValidationError, match="strictly greater"):
            _ta.validate_python(
                _pct_track(_pct_period(6, until), _pct_period(until, None))
            )
        with pytest.raises(ValidationError, match="strictly greater"):
            _ta.validate_python(
                _uc_track(_uc_period(6, until), _uc_period(until, None))
            )

    @pytest.mark.parametrize("pct", ["0", "-0.1", "1.01"])
    def test_percentage_out_of_range_raises(self, pct: str) -> None:
        """Percentage must be in (0, 1]."""
        with pytest.raises(ValidationError, match=r"percentage must be in \(0, 1\]"):
            _ta.validate_python(_pct_track(_pct_period(0, None, pct)))

    def test_percentage_one_accepted(self) -> None:
        """100% (no wage reduction) is a legitimate percentage."""
        track = _ta.validate_python(_pct_track(_pct_period(0, None, "1.00")))
        assert isinstance(track, ApprenticeshipPercentage)
        assert track.periods[0].percentage == Decimal("1.00")

    def test_negative_months_from_raises(self) -> None:
        """months_from must be >= 0."""
        with pytest.raises(ValidationError):
            _ta.validate_python(_pct_track(_pct_period(-1, None)))

    def test_extra_key_raises(self) -> None:
        """Unknown keys (e.g. legacy pay_level_code) are rejected."""
        with pytest.raises(ValidationError, match="Extra inputs"):
            _ta.validate_python(
                _uc_track({**_uc_period(0, None), "pay_level_code": "3"})
            )


# ---------------------------------------------------------------------------
# Period sequence validator (shared by both track types)
# ---------------------------------------------------------------------------


class TestPeriodSequence:
    """Contiguity, start at zero and open-ended last period."""

    def test_empty_periods_raises(self) -> None:
        """An empty periods list must raise."""
        with pytest.raises(ValidationError, match="must not be empty"):
            _ta.validate_python(_pct_track())
        with pytest.raises(ValidationError, match="must not be empty"):
            _ta.validate_python(_uc_track())

    def test_first_period_not_at_zero_raises(self) -> None:
        """The first period must start at months_from=0."""
        with pytest.raises(ValidationError, match="must start at months_from=0"):
            _ta.validate_python(_pct_track(_pct_period(6, None)))

    def test_non_last_open_ended_raises(self) -> None:
        """An intermediate open-ended period must raise."""
        with pytest.raises(ValidationError, match="only the last period"):
            _ta.validate_python(_pct_track(_pct_period(0, None), _pct_period(12, None)))

    def test_gap_raises(self) -> None:
        """A gap between consecutive periods must raise."""
        with pytest.raises(ValidationError, match="gap between period"):
            _ta.validate_python(_uc_track(_uc_period(0, 12), _uc_period(18, None)))

    def test_closed_last_period_raises(self) -> None:
        """The last period must be open-ended."""
        with pytest.raises(ValidationError, match="must be open-ended"):
            _ta.validate_python(_uc_track(_uc_period(0, 12), _uc_period(12, 24)))

    def test_two_contiguous_periods_valid(self) -> None:
        """Two contiguous periods with an open-ended last are valid."""
        track = _ta.validate_python(
            _uc_track(_uc_period(0, 12, 2), _uc_period(12, None, 1))
        )
        assert isinstance(track, ApprenticeshipUnderClassification)
        assert [p.levels_below for p in track.periods] == [2, 1]
        assert track.periods[0].midpoint_to_destination is False


# ---------------------------------------------------------------------------
# Destination levels
# ---------------------------------------------------------------------------


class TestDestinationLevels:
    """destination_levels must be non-empty and unique."""

    def test_empty_raises(self) -> None:
        """An empty destination_levels list must raise."""
        track = _pct_track(_pct_period(0, None))
        track["destination_levels"] = []
        with pytest.raises(
            ValidationError, match="destination_levels must not be empty"
        ):
            _ta.validate_python(track)

    def test_duplicate_raises(self) -> None:
        """Duplicate destination levels must raise."""
        track = _uc_track(_uc_period(0, None))
        track["destination_levels"] = ["4", "4"]
        with pytest.raises(ValidationError, match="destination_levels must be unique"):
            _ta.validate_python(track)

    def test_multiple_destinations_valid(self) -> None:
        """A track may serve several destination levels."""
        track = _pct_track(_pct_period(0, None))
        track["destination_levels"] = ["3", "4"]
        parsed = _ta.validate_python(track)
        assert parsed.destination_levels == ["3", "4"]
