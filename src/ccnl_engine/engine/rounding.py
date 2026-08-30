"""Monetary rounding utilities.

All computed monetary values must pass through :func:`money` before being
stored in a :class:`~ccnl_engine.engine.result.ComputationResult`. This
guarantees deterministic two-decimal-place results using the ROUND_HALF_UP
convention required by Italian accounting standards.
"""

from decimal import ROUND_HALF_UP, Decimal

_CENT = Decimal("0.01")


def money(x: Decimal) -> Decimal:
    """Round *x* to two decimal places (ROUND_HALF_UP).

    Args:
        x: Any :class:`~decimal.Decimal` value.

    Returns:
        *x* rounded to the nearest cent, ties broken upward.
    """
    return x.quantize(_CENT, rounding=ROUND_HALF_UP)
