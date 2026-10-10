"""Tests for engine.rounding — RoundingPolicy and money()."""

from dataclasses import FrozenInstanceError
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.payroll.amount.policies_rounding import (
    MONETARY,
    RoundingPolicy,
    contribution_base,
    money,
)


class TestRoundingPolicy:
    """Unit tests for RoundingPolicy."""

    def test_apply_delegates_quantize(self) -> None:
        """apply() rounds to the declared precision using the declared mode."""
        policy = RoundingPolicy(
            precision=Decimal("0.01"), mode=ROUND_HALF_UP, stage="monetary"
        )
        assert policy.apply(Decimal("2.345")) == Decimal("2.35")

    def test_str_returns_mode_and_precision(self) -> None:
        """str() returns '{mode} {precision}' — the trace descriptor format."""
        policy = RoundingPolicy(
            precision=Decimal("0.01"), mode=ROUND_HALF_UP, stage="monetary"
        )
        assert str(policy) == "ROUND_HALF_UP 0.01"

    def test_monetary_constant_descriptor(self) -> None:
        """MONETARY stringifies to the exact descriptor used in fiscal traces.

        This assertion is a frozen contract: if precision or mode changes, the
        trace rounding field changes too, and this test fails loudly.
        """
        assert str(MONETARY) == "ROUND_HALF_UP 0.01"

    def test_monetary_is_frozen(self) -> None:
        """MONETARY is a frozen dataclass — mutation raises FrozenInstanceError."""
        with pytest.raises(FrozenInstanceError):
            MONETARY.precision = Decimal("0.001")  # type: ignore[misc]


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


@pytest.mark.parametrize(
    ("amount", "base"),
    [
        (Decimal("2005.67"), Decimal("2006.00")),
        (Decimal("1667.47"), Decimal("1667.00")),
        (Decimal("2052.50"), Decimal("2053.00")),
        (Decimal("2052.49"), Decimal("2052.00")),
    ],
)
def test_contribution_base_rounds_to_the_whole_euro(
    amount: Decimal, base: Decimal
) -> None:
    """INPS circ. 208/2001: up to 49 cents down, from 50 cents up.

    The observed payslips p04 (2,005.67 -> 2,006) and p05 (1,667.47 ->
    1,667) print the base so.
    """
    assert contribution_base(amount) == base


def test_contribution_base_of_the_public_sector_keeps_the_cents() -> None:
    """The Gestione Dipendenti Pubblici keeps the cents (NoiPA payslip p07)."""
    assert contribution_base(Decimal("2002.87"), whole_euro=False) == Decimal("2002.87")
