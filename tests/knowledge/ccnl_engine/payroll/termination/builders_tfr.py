"""TFR facts for tests whose subject is not the TFR fund or its destination.

A December run revalues the TFR fund at 31 December of the year before and
every run that accrues TFR outside a pension fund needs to know whether it
goes to the Fondo Tesoreria INPS: without either fact the result has a
``missing_fact`` blocker.  Tests about another capability state a worker
hired in the year, with no fund to revalue, whose TFR accrues in the company.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.inputs import TfrFundBalance

__all__ = ["no_tfr_fund"]


def no_tfr_fund(year: int = 2026) -> TfrFundBalance:
    """Return an empty TFR fund at 31 December of the year before ``year``.

    Returns:
        A zero balance struck at 31 December of ``year - 1``.
    """
    return TfrFundBalance(year - 1, Decimal("0.00"))
