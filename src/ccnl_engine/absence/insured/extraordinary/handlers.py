"""Handler of an extraordinary leave: deduction and INPS indemnity.

The run deducts the days of leave of its month at the CCNL daily quota as
an unpaid absence: out of the INPS and TFR bases (art. 42 c. 5-quinquies
D.Lgs. 151/2001: the leave accrues no TFR; the days are covered by
figurative contributions).  It pays back the INPS indemnity of each
calendar day, posted as ``maternity_item``: the last monthly pay of fixed
and continuous items times the monthly payments of a year over 365, at
most the daily maximum of the year (c. 5-ter).  Which divisor INPS applies
to the worker's own pay no source states: the run records the open engine
limitation ``extraordinary_leave_daily_base``.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.handlers import _decision, _no_quota, _span
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.extraordinary.inputs import (
        ExtraordinaryLeaveEvent,
    )
    from ccnl_engine.absence.insured.models import ExtraordinaryLeaveRates
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = [
    "CEILING_UNKNOWN",
    "EXTRAORDINARY",
    "EXTRAORDINARY_BASE_LIMITATION",
    "LAST_PAY_UNKNOWN",
    "_handle_extraordinary_leave",
]

#: Capability of an extraordinary leave.
EXTRAORDINARY = "extraordinary_leave"
#: The leave states no last pay: the indemnity is on the pay of the run.
LAST_PAY_UNKNOWN = "extraordinary_last_pay_unknown"
#: The bundle lists no daily maximum for the year of a day of leave.
CEILING_UNKNOWN = "extraordinary_leave_ceiling_unknown"
#: The daily divisor of the worker's own pay is not settled by a source.
EXTRAORDINARY_BASE_LIMITATION = "extraordinary_leave_daily_base"
_DEDUCTION = "absence_deduction"
_MONTHS = 12
_YEAR_DAYS = Decimal(365)
_DAY = timedelta(days=1)


def _issue(code: str, message: str, fact: str | None = None) -> CalculationIssue:
    return CalculationIssue(
        code=code,
        message=message,
        status=CalculationStatus.PROVISIONAL,
        capability=EXTRAORDINARY,
        fact=fact,
        cause=IssueCause.RULE,
    )


def _indemnity(
    first: date, last: date, daily: Decimal, rates: ExtraordinaryLeaveRates
) -> tuple[Decimal, set[int]]:
    """Return the indemnity of the days ``first``-``last`` and the unknown years.

    Returns:
        The sum of each day's indemnity, at most its year's maximum, rounded
        to the cent; and the years of the days without a known maximum.
    """
    total, unknown = Decimal(0), set()
    day = first
    while day <= last:
        ceiling = rates.ceiling(day.year)
        if ceiling is None:
            unknown.add(day.year)
        total += daily if ceiling is None else min(daily, ceiling)
        day += _DAY
    return money(total), unknown


def _handle_extraordinary_leave(
    event: ExtraordinaryLeaveEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days of the extraordinary leave in the month of the run.

    Returns:
        The items, entries, base deltas, decision, issues and limitation of
        the leave.
    """
    terms = ctx.insured
    span = _span(event, terms, EXTRAORDINARY)
    if terms is None or terms.pay is None:
        return _no_quota(EXTRAORDINARY)
    issues: list[CalculationIssue] = []
    last_pay = event.last_fixed_pay
    if last_pay is None:
        last_pay = terms.pay.monthly
        issues.append(
            _issue(
                LAST_PAY_UNKNOWN,
                "INPS pays the extraordinary leave on the last pay of fixed and "
                "continuous items (ExtraordinaryLeaveEvent.last_fixed_pay), "
                "which the leave does not state; the indemnity is computed on "
                "the monthly pay of the run meanwhile",
                "last_fixed_pay",
            )
        )
    daily = last_pay * (_MONTHS + terms.pay.extra_months) / _YEAR_DAYS
    amount, unknown = _indemnity(*span, daily, terms.rates.extraordinary_leave)
    if unknown:
        years = ", ".join(str(y) for y in sorted(unknown))
        issues.append(
            _issue(
                CEILING_UNKNOWN,
                f"the bundle lists no daily maximum of the indemnity for {years}: "
                "the days are paid uncapped",
            )
        )
    units, deduction = terms.pay.deducted(*span)
    days = (span[1] - span[0]).days + 1
    pay = InsuredPay(units, deduction, amount, days)
    effect = post_lines(
        (
            ("abs", -pay.deduction, _DEDUCTION, pay.units),
            ("inps", pay.indemnity, "maternity_item", Decimal(pay.days)),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(EXTRAORDINARY, terms, span, pay, modelled=True, advanced=True)
    ]
    effect.issues = issues
    effect.limitations = (EXTRAORDINARY_BASE_LIMITATION,)
    return effect
