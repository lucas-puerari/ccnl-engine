"""Unit tests for WelfareInput domain model."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import WelfareInput

_ZERO = Decimal(0)


class TestWelfareInput:
    """Validation and default behaviour of WelfareInput."""

    def test_defaults_to_zero(self) -> None:
        """Default annual_amount is zero."""
        wi = WelfareInput()
        assert wi.annual_amount == _ZERO

    def test_explicit_value(self) -> None:
        """Explicit annual_amount is stored as-is."""
        wi = WelfareInput(annual_amount=Decimal(600))
        assert wi.annual_amount == Decimal(600)

    def test_zero_is_valid(self) -> None:
        """Zero annual_amount is a valid value."""
        wi = WelfareInput(annual_amount=_ZERO)
        assert wi.annual_amount == _ZERO

    def test_negative_raises(self) -> None:
        """Negative annual_amount raises ValueError."""
        with pytest.raises(ValueError, match="annual_amount must be >= 0"):
            WelfareInput(annual_amount=Decimal("-0.01"))
