"""Tests for ValidityPeriod and TimeSeries.

Each inner class groups tests for a single behaviour or validator branch to
satisfy the 100 % branch-coverage requirement.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.contract.domain.validity import (
    SalaryGapError,
    SalaryGapKind,
    TimeSeries,
    ValidityPeriod,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _period(
    valid_from: str,
    valid_until: str | None,
    value: str = "100.00",
) -> ValidityPeriod:
    """Build a ValidityPeriod from ISO-date strings.

    Returns:
        A ValidityPeriod with the given date boundaries and value.
    """
    return ValidityPeriod(
        valid_from=date.fromisoformat(valid_from),
        valid_until=date.fromisoformat(valid_until) if valid_until else None,
        value=Decimal(value),
    )


def _gap_period(
    valid_from: str,
    valid_until: str | None,
    gap_kind: SalaryGapKind,
) -> ValidityPeriod:
    """Build a gap ValidityPeriod (no numeric value) from ISO-date strings.

    Returns:
        A ValidityPeriod with gap_kind set and no value.
    """
    return ValidityPeriod(
        valid_from=date.fromisoformat(valid_from),
        valid_until=date.fromisoformat(valid_until) if valid_until else None,
        gap_kind=gap_kind,
    )


def _series(*periods: ValidityPeriod) -> TimeSeries:
    """Build a TimeSeries from ValidityPeriod objects.

    Returns:
        A TimeSeries containing the given periods.
    """
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


# ---------------------------------------------------------------------------
# ValidityPeriod — gap periods (SalaryGapKind)
# ---------------------------------------------------------------------------


class TestValidityPeriodGap:
    """Gap period construction and XOR invariant."""

    def test_gap_missing_valid(self) -> None:
        """A period with gap_kind='missing' and no value is accepted."""
        p = _gap_period("2024-01-01", "2025-01-01", SalaryGapKind.MISSING)
        assert p.is_gap
        assert p.gap_kind == SalaryGapKind.MISSING
        assert p.value is None

    def test_gap_not_applicable_valid(self) -> None:
        """A period with gap_kind='not_applicable' and no value is accepted."""
        p = _gap_period("2024-01-01", None, SalaryGapKind.NOT_APPLICABLE)
        assert p.is_gap
        assert p.gap_kind == SalaryGapKind.NOT_APPLICABLE

    def test_gap_unknown_valid(self) -> None:
        """A period with gap_kind='unknown' and no value is accepted."""
        p = _gap_period("2024-01-01", None, SalaryGapKind.UNKNOWN)
        assert p.is_gap
        assert p.gap_kind == SalaryGapKind.UNKNOWN

    def test_both_value_and_gap_kind_raises(self) -> None:
        """Supplying both value and gap_kind must raise ValidationError."""
        with pytest.raises(ValidationError, match="exactly one"):
            ValidityPeriod(
                valid_from=date(2024, 1, 1),
                valid_until=None,
                value=Decimal("100.00"),
                gap_kind=SalaryGapKind.MISSING,
            )

    def test_neither_value_nor_gap_kind_raises(self) -> None:
        """Supplying neither value nor gap_kind must raise ValidationError."""
        with pytest.raises(ValidationError, match="exactly one"):
            ValidityPeriod(
                valid_from=date(2024, 1, 1),
                valid_until=None,
            )

    def test_non_gap_is_gap_false(self) -> None:
        """is_gap is False for a regular period with a value."""
        p = _period("2024-01-01", None, "500.00")
        assert not p.is_gap


# ---------------------------------------------------------------------------
# TimeSeries.value_at — gap period behaviour
# ---------------------------------------------------------------------------


class TestTimeSeriesValueAtGap:
    """value_at raises SalaryGapError when the active period is a gap."""

    def test_single_gap_period_raises_salary_gap_error(self) -> None:
        """value_at on a date within a single gap period raises SalaryGapError."""
        p = _gap_period("2024-01-01", None, SalaryGapKind.MISSING)
        ts = _series(p)
        with pytest.raises(SalaryGapError):
            ts.value_at(date(2024, 6, 1))

    def test_gap_error_carries_gap_kind(self) -> None:
        """SalaryGapError.gap_kind equals the period's gap_kind."""
        p = _gap_period("2024-01-01", None, SalaryGapKind.NOT_APPLICABLE)
        ts = _series(p)
        with pytest.raises(SalaryGapError) as exc_info:
            ts.value_at(date(2025, 1, 1))
        assert exc_info.value.gap_kind == SalaryGapKind.NOT_APPLICABLE

    def test_gap_error_is_value_error(self) -> None:
        """SalaryGapError is a subclass of ValueError."""
        p = _gap_period("2024-01-01", None, SalaryGapKind.UNKNOWN)
        ts = _series(p)
        with pytest.raises(ValueError, match="explicit gap"):
            ts.value_at(date(2024, 3, 1))

    def test_gap_in_middle_raises_for_gap_date(self) -> None:
        """value_at on the gap range raises SalaryGapError; flanking periods work."""
        p0 = _period("2023-01-01", "2024-01-01", "1000.00")
        gap = _gap_period("2024-01-01", "2025-01-01", SalaryGapKind.MISSING)
        p1 = _period("2025-01-01", None, "1100.00")
        ts = _series(p0, gap, p1)
        # Before gap: normal value
        assert ts.value_at(date(2023, 6, 1)) == Decimal("1000.00")
        # Inside gap: SalaryGapError
        with pytest.raises(SalaryGapError) as exc_info:
            ts.value_at(date(2024, 6, 1))
        assert exc_info.value.gap_kind == SalaryGapKind.MISSING
        # After gap: normal value
        assert ts.value_at(date(2025, 6, 1)) == Decimal("1100.00")

    def test_period_at_returns_gap_period(self) -> None:
        """period_at returns a gap period and its is_gap flag is True."""
        gap = _gap_period("2024-01-01", None, SalaryGapKind.NOT_APPLICABLE)
        ts = _series(gap)
        p = ts.period_at(date(2024, 6, 1))
        assert p is not None
        assert p.is_gap
        assert p.gap_kind == SalaryGapKind.NOT_APPLICABLE
