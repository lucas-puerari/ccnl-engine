"""Separate worked and paid-holiday hours in a run paid by the hour."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.compensation.element.types import MonthlyPayChain


@dataclass(frozen=True)
class HourlyBasis:
    """Hours a run pays by the hour and what the monthly pay is divided by.

    Attributes:
        hours: Ordinary hours worked in the month, ``None`` when the run
            does not state them.
        divisor: Hourly divisor of the CCNL; for a part-time worker times
            the part-time ratio, since the chain is already reduced by it:
            the hours worked carry the part time.
        holiday_hours: Paid holiday hours, counted separately from work.
            They do not enter the contribution based on hours actually worked.
            ``None`` when the caller has not stated eligible holidays.
    """

    hours: Decimal | None
    divisor: Decimal
    holiday_hours: Decimal | None = None

    def apply(self, chain: MonthlyPayChain) -> MonthlyPayChain:
        """Return the chain paid on the hours worked.

        Returns:
            Every component times ``hours / divisor``, rounded once; a zero
            chain without the hours. Paid holiday hours are added separately
            to the hours worked before applying the divisor.
        """
        if self.hours is None:
            return chain.scaled(Decimal(0))
        return chain.prorated(
            self.hours + (self.holiday_hours or Decimal(0)), self.divisor
        )
