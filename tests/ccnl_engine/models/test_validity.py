"""Tests for ValidityPeriod and TimeSeries.

Each inner class groups tests for a single behaviour or validator branch to
satisfy the 100 % branch-coverage requirement.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.models.validity import TimeSeries, ValidityPeriod

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _period(
    valid_from: str,
    valid_until: str | None,
    value: str = "100.00",
) -> ValidityPeriod:
    """Build a ValidityPeriod from ISO-date strings."""
    return ValidityPeriod(
        valid_from=date.fromisoformat(valid_from),
        valid_until=date.fromisoformat(valid_until) if valid_until else None,
        value=Decimal(value),
    )


def _series(*periods: ValidityPeriod) -> TimeSeries:
    """Build a TimeSeries from ValidityPeriod objects."""
    return TimeSeries(periods=list(periods))


# ---------------------------------------------------------------------------
# ValidityPeriod
# ---------------------------------------------------------------------------


class TestValidityPeriod:
    """Unit tests for ValidityPeriod validators."""

    def test_open_ended_accepted(self) -> None:
        """valid_until=None is accepted (open-ended period)."""
        vp = _period("2025-01-01", None, "500.00")
        assert vp.valid_until is None
        assert vp.value == Decimal("500.00")

    def test_closed_valid_accepted(self) -> None:
        """valid_until strictly after valid_from is accepted."""
        vp = _period("2025-01-01", "2026-01-01", "200.00")
        assert vp.valid_until == date(2026, 1, 1)

    def test_same_day_raises(self) -> None:
        """valid_until == valid_from must raise ValidationError."""
        with pytest.raises(ValidationError):
            _period("2025-06-01", "2025-06-01")

    def test_reversed_dates_raises(self) -> None:
        """valid_until < valid_from must raise ValidationError."""
        with pytest.raises(ValidationError):
            _period("2025-06-01", "2025-01-01")


# ---------------------------------------------------------------------------
# TimeSeries — construction validators
# ---------------------------------------------------------------------------


class TestTimeSeriesValidators:
    """Unit tests for TimeSeries model validators."""

    def test_empty_list_raises(self) -> None:
        """An empty period list must raise ValidationError."""
        with pytest.raises(ValidationError):
            TimeSeries(periods=[])

    def test_non_last_open_ended_raises(self) -> None:
        """A non-last period with valid_until=None must raise ValidationError."""
        p0 = _period("2024-01-01", None)
        p1 = _period("2025-01-01", None)
        with pytest.raises(ValidationError):
            TimeSeries(periods=[p0, p1])

    def test_gap_raises(self) -> None:
        """A gap between consecutive periods must raise ValidationError."""
        p0 = _period("2024-01-01", "2024-06-01")
        p1 = _period("2025-01-01", None)  # gap: 2024-06-01 → 2025-01-01
        with pytest.raises(ValidationError):
            TimeSeries(periods=[p0, p1])

    def test_closed_last_period_raises(self) -> None:
        """Last period with valid_until not None must raise ValidationError."""
        p0 = _period("2024-01-01", "2025-01-01")
        with pytest.raises(ValidationError):
            TimeSeries(periods=[p0])

    def test_single_period_valid(self) -> None:
        """A single open-ended period is a valid TimeSeries."""
        ts = _series(_period("2025-01-01", None, "1000.00"))
        assert len(ts.periods) == 1

    def test_two_periods_valid(self) -> None:
        """Two contiguous periods with an open-ended last period are valid."""
        p0 = _period("2024-01-01", "2025-01-01")
        p1 = _period("2025-01-01", None, "120.00")
        ts = _series(p0, p1)
        assert len(ts.periods) == 2


# ---------------------------------------------------------------------------
# TimeSeries.value_at
# ---------------------------------------------------------------------------


class TestTimeSeriesValueAt:
    """Unit tests for TimeSeries.value_at — covers every branch."""

    def test_before_start_raises(self) -> None:
        """value_at raises ValueError for a day before the first period."""
        ts = _series(_period("2025-01-01", None))
        with pytest.raises(ValueError, match="series starts"):
            ts.value_at(date(2024, 12, 31))

    def test_single_period_on_start(self) -> None:
        """value_at returns the value on the first day of the only period."""
        ts = _series(_period("2025-01-01", None, "100.00"))
        assert ts.value_at(date(2025, 1, 1)) == Decimal("100.00")

    def test_single_period_well_inside(self) -> None:
        """value_at returns the value for a date well within the only period."""
        ts = _series(_period("2025-01-01", None, "100.00"))
        assert ts.value_at(date(2030, 6, 15)) == Decimal("100.00")

    def test_first_of_two_periods(self) -> None:
        """value_at returns p0's value when day is within p0 (not None branch)."""
        p0 = _period("2024-01-01", "2025-01-01", "100.00")
        p1 = _period("2025-01-01", None, "120.00")
        ts = _series(p0, p1)
        assert ts.value_at(date(2024, 6, 15)) == Decimal("100.00")

    def test_second_of_two_periods(self) -> None:
        """value_at skips p0 (day >= valid_until) and returns p1's value.

        Exercises: p0 condition False on inner check, then p1 valid_until=None.
        """
        p0 = _period("2024-01-01", "2025-01-01", "100.00")
        p1 = _period("2025-01-01", None, "120.00")
        ts = _series(p0, p1)
        assert ts.value_at(date(2025, 6, 15)) == Decimal("120.00")

    def test_boundary_belongs_to_second_period(self) -> None:
        """valid_until is exclusive: the boundary date belongs to the next period."""
        p0 = _period("2024-01-01", "2025-01-01", "100.00")
        p1 = _period("2025-01-01", None, "120.00")
        ts = _series(p0, p1)
        assert ts.value_at(date(2025, 1, 1)) == Decimal("120.00")

    def test_before_start_of_two_periods_raises(self) -> None:
        """value_at raises ValueError when day is before the first of two periods."""
        p0 = _period("2024-01-01", "2025-01-01", "100.00")
        p1 = _period("2025-01-01", None, "120.00")
        ts = _series(p0, p1)
        with pytest.raises(ValueError, match="series starts"):
            ts.value_at(date(2023, 12, 31))
