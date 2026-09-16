"""Unit tests for OvertimeHours and WeeklyOvertimeHours domain models."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import (
    OvertimeHours,
    WeeklyOvertimeHours,
)

_ZERO = Decimal(0)


class TestOvertimeHoursDefaults:
    """OvertimeHours defaults to all-zero fields."""

    def test_defaults_are_zero(self) -> None:
        """All hour fields default to zero."""
        oh = OvertimeHours()
        assert oh.weekday_hours == _ZERO
        assert oh.night_hours == _ZERO
        assert oh.holiday_hours == _ZERO
        assert oh.supplementare_hours == _ZERO

    def test_partial_construction(self) -> None:
        """Only specified fields are non-zero."""
        oh = OvertimeHours(night_hours=Decimal(3))
        assert oh.weekday_hours == _ZERO
        assert oh.night_hours == Decimal(3)


class TestOvertimeHoursValidation:
    """OvertimeHours rejects negative hour values."""

    @pytest.mark.parametrize(
        "field",
        ["weekday_hours", "night_hours", "holiday_hours", "supplementare_hours"],
    )
    def test_negative_raises(self, field: str) -> None:
        """Negative values raise ValueError for all hour fields."""
        with pytest.raises(ValueError, match=f"{field} must be >= 0"):
            OvertimeHours(**{field: Decimal(-1)})  # type: ignore[arg-type]

    def test_zero_is_valid(self) -> None:
        """Explicit zero does not raise."""
        oh = OvertimeHours(weekday_hours=_ZERO)
        assert oh.weekday_hours == _ZERO


class TestWeeklyOvertimeHoursValidation:
    """WeeklyOvertimeHours rejects negative hour values."""

    @pytest.mark.parametrize(
        "field",
        [
            "weekday_hours",
            "night_hours",
            "holiday_hours",
            "night_holiday_hours",
            "supplementare_hours",
        ],
    )
    def test_negative_raises(self, field: str) -> None:
        """Negative values raise ValueError for all WeeklyOvertimeHours fields."""
        with pytest.raises(ValueError, match=f"{field} must be >= 0"):
            WeeklyOvertimeHours(**{field: Decimal(-1)})

    def test_zero_is_valid(self) -> None:
        """All-zero WeeklyOvertimeHours is valid."""
        w = WeeklyOvertimeHours()
        assert w.weekday_hours == _ZERO


class TestOvertimeHoursWeeksConsistency:
    """OvertimeHours validates that monthly totals match sum of weekly values."""

    def test_from_weeks_derives_totals(self) -> None:
        """from_weeks sets months totals equal to the sum of weekly values."""
        weeks = (
            WeeklyOvertimeHours(weekday_hours=Decimal(3)),
            WeeklyOvertimeHours(weekday_hours=Decimal(5)),
        )
        oh = OvertimeHours.from_weeks(weeks)
        assert oh.weekday_hours == Decimal(8)
        assert oh.weeks == weeks

    def test_mismatch_raises(self) -> None:
        """Mismatched monthly total vs weekly sum raises ValueError."""
        week = WeeklyOvertimeHours(weekday_hours=Decimal(4))
        with pytest.raises(ValueError, match="weekday_hours monthly total"):
            OvertimeHours(
                weekday_hours=Decimal(10),  # wrong: sum of weeks = 4
                weeks=(week,),
            )

    def test_matching_consistency_is_valid(self) -> None:
        """Matching monthly total and weekly sum does not raise."""
        week = WeeklyOvertimeHours(weekday_hours=Decimal(4))
        oh = OvertimeHours(weekday_hours=Decimal(4), weeks=(week,))
        assert oh.weekday_hours == Decimal(4)
        assert len(oh.weeks) == 1
