"""Tests for engine.rounding — money() function."""

from decimal import Decimal

from ccnl_engine.engine.rounding import money


class TestMoney:
    """Unit tests for the money() rounding function."""

    def test_round_half_up_midpoint(self) -> None:
        """A .5-cent value rounds up (ROUND_HALF_UP)."""
        assert money(Decimal("2.345")) == Decimal("2.35")

    def test_round_down_below_midpoint(self) -> None:
        """A value below .5 cent rounds down."""
        assert money(Decimal("2.344")) == Decimal("2.34")

    def test_exact_cents_unchanged(self) -> None:
        """A value already at two decimal places is returned unchanged."""
        assert money(Decimal("100.00")) == Decimal("100.00")

    def test_zero(self) -> None:
        """Zero rounds to zero."""
        assert money(Decimal(0)) == Decimal("0.00")

    def test_negative_value(self) -> None:
        """ROUND_HALF_UP rounds the half digit away from zero for negatives."""
        assert money(Decimal("-1.005")) == Decimal("-1.01")
