"""TFR fund of the employment at 31 December: the base of the revaluation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.payroll.employment.inputs_fact import FEATURE
from ccnl_engine.validation import (
    reject,
    require_decimal,
    require_int,
)

__all__ = ["TfrFundBalance"]

_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class TfrFundBalance:
    """TFR the worker has accrued with the employer at 31 December of a year.

    The fund at 31 December of ``year``, after the revaluation of that date
    and net of the substitute tax charged to it, less the advances paid:
    the TFR the next year revalues (art. 2120 c. 4 c.c.: the quota accrued
    in the year is excluded).  It includes the part paid to the Fondo
    Tesoreria INPS, whose share the Fondo pays out under art. 2120 c.c.
    (DM 30 gennaio 2007 art. 2 c. 1), and excludes the TFR paid to a
    complementary pension fund.

    Attributes:
        year: Year at whose 31 December the balance is struck.
        amount: Balance in EUR, non-negative, with at most two decimals.

    Raises:
        InvalidInputError: When ``year`` is not an int from 1900 or
            ``amount`` is not a non-negative Decimal in cents.
    """

    year: int
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.year, "TfrFundBalance.year", feature=FEATURE, minimum=1900)
        path = "TfrFundBalance.amount"
        require_decimal(self.amount, path, feature=FEATURE, minimum=Decimal(0))
        if self.amount != self.amount.quantize(_CENT):
            reject(
                path,
                "an amount with at most two decimals",
                self.amount,
                feature=FEATURE,
            )
