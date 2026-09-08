"""Unit tests for OvertimeHours domain model."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours

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
            OvertimeHours(**{field: Decimal(-1)})

    def test_zero_is_valid(self) -> None:
        """Explicit zero does not raise."""
        oh = OvertimeHours(weekday_hours=_ZERO)
        assert oh.weekday_hours == _ZERO
