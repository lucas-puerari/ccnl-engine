"""Arithmetic shared by the deductions of art. 12 TUIR.

Every ratio of the formulas is taken to the decimals of the rules, the rest
discarded (art. 12 c. 4), before it multiplies an amount.  A deduction is
due for the months of the year its conditions hold (c. 3) and rounded to the
cent once, after the months and the allocation are applied.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.family import Dependent

__all__ = [
    "MONTHS_IN_YEAR",
    "DependentDeduction",
    "phase_out",
    "prorate",
    "truncated",
]

MONTHS_IN_YEAR = 12
_ZERO = Decimal(0)
_ONE = Decimal(1)
_HUNDRED = Decimal(100)


@dataclass(frozen=True)
class DependentDeduction:
    """Deduction of one dependent for the tax year.

    Attributes:
        dependent: The dependent.
        months: Months of the year the deduction is due.
        annual: Deduction for a full year at the reddito complessivo, before
            the months and the allocation; not rounded.
        amount: ``annual * months / 12 * allocation_pct / 100``, rounded to
            the cent.
    """

    dependent: Dependent
    months: int
    annual: Decimal
    amount: Decimal


def truncated(ratio: Decimal, decimals: int) -> Decimal:
    """Return ``ratio`` taken to ``decimals`` decimals, the rest discarded.

    Returns:
        The ratio rounded towards zero.
    """
    return ratio.quantize(_ONE.scaleb(-decimals), rounding=ROUND_DOWN)


def phase_out(
    amount: Decimal,
    limit: Decimal,
    span: Decimal,
    income: Decimal,
    decimals: int,
) -> Decimal:
    """Return the part of ``amount`` of the ratio ``(limit - income) / span``.

    The deduction is not due when the ratio is zero or less, or one or more
    (art. 12 c. 4); otherwise the ratio is truncated to ``decimals``.

    Returns:
        ``amount`` times the truncated ratio, not rounded.
    """
    ratio = (limit - income) / span
    if ratio <= _ZERO or ratio >= _ONE:
        return _ZERO
    return amount * truncated(ratio, decimals)


def prorate(dependent: Dependent, months: int, annual: Decimal) -> DependentDeduction:
    """Return the deduction of ``dependent`` for ``months`` of the year.

    Returns:
        The deduction, rounded to the cent after the months and allocation.
    """
    amount = money(
        annual
        * Decimal(months)
        / Decimal(MONTHS_IN_YEAR)
        * dependent.allocation_pct
        / _HUNDRED
    )
    return DependentDeduction(dependent, months, annual, amount)
