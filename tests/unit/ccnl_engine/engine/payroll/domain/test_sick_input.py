"""Unit tests for SickInput domain model."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import SickInput

_ZERO = Decimal(0)


class TestSickInput:
    """Validation and default behaviour of SickInput."""

    def test_defaults_to_zero(self) -> None:
        """Default sick_days is zero."""
        si = SickInput()
        assert si.sick_days == _ZERO

    def test_explicit_value(self) -> None:
        """Explicit sick_days is stored as-is."""
        si = SickInput(sick_days=Decimal(5))
        assert si.sick_days == Decimal(5)

    def test_zero_is_valid(self) -> None:
        """Zero sick_days is a valid value."""
        si = SickInput(sick_days=_ZERO)
        assert si.sick_days == _ZERO

    def test_negative_raises(self) -> None:
        """Negative sick_days raises ValueError."""
        with pytest.raises(ValueError, match="sick_days must be >= 0"):
            SickInput(sick_days=Decimal(-1))
