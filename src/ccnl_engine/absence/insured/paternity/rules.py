"""The INPS indemnity of the days of a compulsory paternity leave."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.base.rules import run_daily_base
from ccnl_engine.absence.insured.days.rules import deducted_days
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.models import PaternityRates
    from ccnl_engine.absence.insured.rules import MonthPay

__all__ = ["paternity_pay"]


def paternity_pay(
    days: tuple[date, ...],
    pay: MonthPay,
    rates: PaternityRates,
    rmgg: Decimal | None = None,
) -> InsuredPay:
    """Return the deduction and the INPS indemnity of the paternity days.

    Args:
        days: The days of leave in the month.
        pay: The pay of the month.
        rates: The INPS indemnity.
        rmgg: Daily base of the month before the leave (art. 23);
            ``None`` takes the monthly pay of the run instead.

    Returns:
        The amounts, each rounded to the cent; no CCNL top-up, the
        indemnity is already the whole pay.
    """
    units, deduction = deducted_days(pay, days)
    daily = run_daily_base(pay, rates.daily_divisor) if rmgg is None else rmgg
    indemnity = money(rates.indemnity_rate * daily * len(days))
    return InsuredPay(units, deduction, indemnity, len(days))
