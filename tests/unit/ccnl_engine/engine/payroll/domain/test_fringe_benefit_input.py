"""Unit tests for FringeBenefitInput domain model."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import FringeBenefitInput

_ZERO = Decimal(0)


class TestFringeBenefitInput:
    """Validation and default behaviour of FringeBenefitInput."""

    def test_defaults(self) -> None:
        """Default annual_amount is zero and has_dependent_children is False."""
        fb = FringeBenefitInput()
        assert fb.annual_amount == _ZERO
        assert fb.has_dependent_children is False

    def test_explicit_amount(self) -> None:
        """Explicit annual_amount is stored as-is."""
        fb = FringeBenefitInput(annual_amount=Decimal(1200))
        assert fb.annual_amount == Decimal(1200)

    def test_with_dependent_children(self) -> None:
        """has_dependent_children flag is stored correctly."""
        fb = FringeBenefitInput(annual_amount=Decimal(500), has_dependent_children=True)
        assert fb.has_dependent_children is True

    def test_negative_amount_raises(self) -> None:
        """Negative annual_amount raises ValueError."""
        with pytest.raises(ValueError, match="annual_amount must be >= 0"):
            FringeBenefitInput(annual_amount=Decimal(-1))
