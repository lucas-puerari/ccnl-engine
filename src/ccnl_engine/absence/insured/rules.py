"""Pay of the days of a maternity leave or a work injury in one month.

The days the worker is away are deducted from the monthly pay at the CCNL
daily quota, as an unpaid absence or a sick day is (they leave the INPS
base; the TFR base keeps them, art. 2120 c. 3 c.c.).  What is paid back:

- maternity: the INPS indemnity, 80% of the pay of the month before over
  thirty plus the daily rateo of the extra months, for every calendar day
  (D.Lgs. 151/2001 artt. 22-23), and the CCNL top-up of the days within its
  limit;
- work injury: the injury day is paid in full and never deducted; the
  three days after it at the CCNL waiting-period rate (60% by law); from
  the fourth day the INAIL indemnity, 60% of the daily base to the
  ninetieth day and 75% after it (D.P.R. 1124/1965 artt. 68, 73, 116-117),
  and the CCNL top-up.

A top-up on the net pay grosses the insurer share, free of contributions,
up by the worker's INPS rate before the employer tops it up, as a sick day
on a net basis is.  The pay of the month before is the monthly pay of the
run (its variable pay is not known).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.proration.rules import payable_days
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.sickness.base.rules import daily_base

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.models import (
        InjuryRates,
        InjuryRules,
        MaternityRates,
        MaternityRules,
    )
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.sickness.base.inputs import InpsSicknessBase
    from ccnl_engine.sickness.term.rules import DailyQuota

__all__ = ["InsuredPay", "MonthPay", "injury_pay", "maternity_pay"]

_ZERO = Decimal(0)
_ONE = Decimal(1)
_MONTHS = 12


@dataclass(frozen=True)
class MonthPay:
    """The pay the days of a month are measured against.

    Attributes:
        chain: Pay chain of a fully employed month.
        quota: Daily quota of the CCNL the days are deducted with.
        extra_months: Months paid beyond the twelve (13th, 14th).
        employee_rate: The worker's INPS rate, for a net top-up.
    """

    chain: MonthlyPayChain
    quota: DailyQuota
    extra_months: int
    employee_rate: Decimal

    @property
    def monthly(self) -> Decimal:
        """Monthly pay: base salary, seniority and cash allowances."""
        chain = self.chain
        return chain.base + chain.seniority + chain.allowances_total

    def deducted(self, first: date, last: date) -> tuple[Decimal, Decimal]:
        """Return the payable units of ``first``-``last`` and their pay.

        A whole calendar month is the divisor: the monthly pay is deducted
        in full whatever the working days of the month.

        Returns:
            ``(units, pay)``: the CCNL payable days (hours for an hourly
            quota), never more than the divisor, and the quota of the chain
            for them, rounded once.
        """
        if last < first:
            return _ZERO, _ZERO
        divisor = self.quota.divisor
        per_day = self.quota.daily_hours or _ONE
        days = Decimal(payable_days(self.quota.method, first, last))
        month_end = calendar.monthrange(last.year, last.month)[1]
        whole = first.day == 1 and last.day == month_end and first.month == last.month
        units = divisor if whole else min(days * per_day, divisor)
        part = self.chain.prorated(units, divisor)
        return units, part.base + part.seniority + part.allowances_total

    def grossed(self, insurer: Decimal, *, net_basis: bool) -> Decimal:
        """Return the insurer share as the gross pay it stands for.

        Returns:
            ``insurer`` grossed up by the worker's INPS rate on a net basis,
            itself otherwise.
        """
        if not net_basis:
            return insurer
        return insurer / (_ONE - self.employee_rate)


@dataclass(frozen=True)
class InsuredPay:
    """Amounts of an insured absence in the month.

    Attributes:
        units: CCNL payable units deducted.
        deduction: Pay of those units, deducted.
        indemnity: The insurer share (INPS or INAIL).
        days: Calendar days the insurer pays.
        integration: Employer top-up of the insurer share.
        carenza: Employer pay of the waiting period (injury only).
        carenza_units: Payable units of the waiting period.
    """

    units: Decimal
    deduction: Decimal
    indemnity: Decimal
    days: int
    integration: Decimal = _ZERO
    carenza: Decimal = _ZERO
    carenza_units: Decimal = _ZERO


def _days(first: date, last: date) -> int:
    return max((last - first).days + 1, 0)


def maternity_pay(
    first: date,
    last: date,
    leave_started_on: date,
    pay: MonthPay,
    rates: MaternityRates,
    rules: MaternityRules | None,
    rmgg: Decimal | None = None,
) -> InsuredPay:
    """Return the deduction, the INPS indemnity and the top-up of the month.

    Args:
        first: First day of the leave in the month.
        last: Last day of the leave in the month.
        leave_started_on: First day of the leave, for the top-up limit.
        pay: The pay of the month.
        rates: The INPS indemnity.
        rules: The CCNL top-up, ``None`` for none.
        rmgg: Daily base of the month before the leave (art. 23 D.Lgs.
            151/2001); ``None`` takes the monthly pay of the run instead.

    Returns:
        The amounts, each rounded to the cent.
    """
    units, deduction = pay.deducted(first, last)
    days = _days(first, last)
    monthly = pay.monthly
    divisor = Decimal(rates.daily_divisor)
    if rmgg is None:
        daily = monthly / divisor + monthly * pay.extra_months / (_MONTHS * divisor)
    else:
        daily = rmgg
    indemnity = money(rates.indemnity_rate * daily * days)
    integration = _ZERO
    if rules is not None and days:
        end = leave_started_on + timedelta(days=rules.integration_days - 1)
        covered = _days(first, min(last, end))
        if covered:
            share = Decimal(covered) / Decimal(days)
            target = rules.integration_rate * deduction * share
            insurer = pay.grossed(indemnity * share, net_basis=rules.net_basis)
            integration = money(max(target - insurer, _ZERO))
    return InsuredPay(units, deduction, indemnity, days, integration)


def injury_pay(
    first: date,
    last: date,
    injury_on: date,
    pay: MonthPay,
    hourly_divisor: Decimal,
    weekly_hours: Decimal,
    rates: InjuryRates,
    rules: InjuryRules | None,
) -> InsuredPay:
    """Return the deduction, the waiting period, the INAIL share and the top-up.

    Args:
        first: First day of the inability in the month (the injury day
            when it falls in it).
        last: Last day of the inability in the month.
        injury_on: Day of the injury.
        pay: The pay of the month.
        hourly_divisor: CCNL monthly hours, for the hourly earnings.
        weekly_hours: Normal weekly hours, for the daily base.
        rates: The statutory measures.
        rules: The CCNL treatment, ``None`` for the statutory one.

    Returns:
        The amounts, each rounded to the cent.
    """
    after = max(first, injury_on + timedelta(days=1))
    units, deduction = pay.deducted(after, last)
    waiting_end = injury_on + timedelta(days=rates.carenza_days)
    carenza_units, carenza_pay = pay.deducted(after, min(last, waiting_end))
    carenza_rate = rates.carenza_rate
    if rules is not None and rules.carenza_rate is not None:
        carenza_rate = max(rules.carenza_rate, carenza_rate)
    carenza = money(carenza_rate * carenza_pay)
    indemnified_from = max(after, waiting_end + timedelta(days=1))
    daily = pay.monthly / hourly_divisor * weekly_hours / Decimal(rates.weekly_days)
    indemnity = _ZERO
    day = indemnified_from
    while day <= last:
        indemnity += rates.rate_on((day - injury_on).days) * daily
        day += timedelta(days=1)
    indemnity = money(indemnity)
    days = _days(indemnified_from, last)
    integration = _ZERO
    if rules is not None and rules.integration_rate is not None and days:
        target = rules.integration_rate * (deduction - carenza_pay)
        insurer = pay.grossed(indemnity, net_basis=rules.net_basis)
        integration = money(max(target - insurer, _ZERO))
    return InsuredPay(
        units,
        deduction,
        indemnity,
        days,
        integration,
        carenza,
        carenza_units,
    )


def maternity_daily_base(
    base: InpsSicknessBase | None,
    category: WorkerCategory | None,
    monthly_payments: Decimal | None,
) -> tuple[Decimal | None, bool]:
    """Return the maternity daily base and whether the engine can compute one.

    Art. 23 c. 4 D.Lgs. 151/2001: the pay of the month before the leave
    over 30, with the daily rateo of the 13th and of the other payments
    (c. 2), as the sickness base of an impiegato.  The base of an operaia
    (c. 5) and of a month not worked in full is not computed.

    Returns:
        ``(rmgg, computable)``: the base, ``None`` without one; whether a
        stated base would give one.
    """
    computable = (
        category is not None
        and category is not WorkerCategory.OPERAIO
        and monthly_payments is not None
        and (base is None or base.paid_days is None)
    )
    if not computable or base is None or monthly_payments is None:
        return None, computable
    return daily_base(base, category, monthly_payments), True
