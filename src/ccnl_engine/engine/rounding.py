"""Monetary rounding utilities."""

from decimal import ROUND_HALF_UP, Decimal

_CENT = Decimal("0.01")


def money(x: Decimal) -> Decimal:
    """Round x to two decimal places using ROUND_HALF_UP."""
    return x.quantize(_CENT, rounding=ROUND_HALF_UP)
