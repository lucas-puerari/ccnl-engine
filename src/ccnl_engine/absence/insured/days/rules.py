"""The deduction of separate days of leave from the monthly pay."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.rules import MonthPay

__all__ = ["deducted_days"]

_ZERO = Decimal(0)


def deducted_days(pay: MonthPay, days: tuple[date, ...]) -> tuple[Decimal, Decimal]:
    """Return the payable units of ``days`` and their pay.

    Each day is deducted at the CCNL daily quota (a day the CCNL does not
    pay, such as a Sunday, is none), never more than the divisor.

    Returns:
        ``(units, pay)``: the units and the quota of the chain for them,
        rounded once.
    """
    units = sum((pay.deducted(day, day)[0] for day in days), _ZERO)
    units = min(units, pay.quota.divisor)
    part = pay.chain.prorated(units, pay.quota.divisor)
    return units, part.base + part.seniority + part.allowances_total
