"""Unit tests for AbsenceDays domain model."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.supplements import AbsenceDays

_ZERO = Decimal(0)


class TestAbsenceDaysDefaults:
    """AbsenceDays defaults to all-zero fields."""

    def test_defaults_are_zero(self) -> None:
        """unpaid_days defaults to zero."""
        ad = AbsenceDays()
        assert ad.unpaid_days == _ZERO

    def test_explicit_value(self) -> None:
        """Explicit unpaid_days is stored."""
        ad = AbsenceDays(unpaid_days=Decimal(3))
        assert ad.unpaid_days == Decimal(3)


class TestAbsenceDaysValidation:
    """AbsenceDays rejects negative values."""

    def test_negative_raises(self) -> None:
        """Negative unpaid_days raises ValueError."""
        with pytest.raises(ValueError, match="unpaid_days must be >= 0"):
            AbsenceDays(unpaid_days=Decimal(-1))

    def test_zero_is_valid(self) -> None:
        """Explicit zero does not raise."""
        ad = AbsenceDays(unpaid_days=_ZERO)
        assert ad.unpaid_days == _ZERO
