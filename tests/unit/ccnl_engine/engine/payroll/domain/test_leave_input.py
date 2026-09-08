"""Unit tests for LeaveInput domain model."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import LeaveInput

_ZERO = Decimal(0)


class TestLeaveInput:
    """Validation and default behaviour of LeaveInput."""

    def test_defaults_to_zero(self) -> None:
        """Default taken_days is zero."""
        li = LeaveInput()
        assert li.taken_days == _ZERO

    def test_explicit_value(self) -> None:
        """Explicit taken_days is stored as-is."""
        li = LeaveInput(taken_days=Decimal(5))
        assert li.taken_days == Decimal(5)

    def test_zero_is_valid(self) -> None:
        """Zero taken_days is a valid value."""
        li = LeaveInput(taken_days=_ZERO)
        assert li.taken_days == _ZERO

    def test_negative_raises(self) -> None:
        """Negative taken_days raises ValueError."""
        with pytest.raises(ValueError, match="taken_days must be >= 0"):
            LeaveInput(taken_days=Decimal(-1))
