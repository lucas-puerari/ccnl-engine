"""Unit tests for BonusInput domain model."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import BonusInput

_ZERO = Decimal(0)


class TestBonusInput:
    """Validation and default behaviour of BonusInput."""

    def test_defaults(self) -> None:
        """Default annual_amount is zero and eligible_for_pdr is False."""
        bi = BonusInput()
        assert bi.annual_amount == _ZERO
        assert bi.eligible_for_pdr is False

    def test_explicit_amount(self) -> None:
        """Explicit annual_amount is stored as-is."""
        bi = BonusInput(annual_amount=Decimal(2000))
        assert bi.annual_amount == Decimal(2000)

    def test_eligible_for_pdr_flag(self) -> None:
        """eligible_for_pdr flag is stored correctly."""
        bi = BonusInput(annual_amount=Decimal(2000), eligible_for_pdr=True)
        assert bi.eligible_for_pdr is True

    def test_negative_amount_raises(self) -> None:
        """Negative annual_amount raises ValueError."""
        with pytest.raises(ValueError, match="annual_amount must be >= 0"):
            BonusInput(annual_amount=Decimal(-100))
