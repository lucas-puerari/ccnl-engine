"""Handler of an extraordinary leave: deduction and INPS indemnity.

The run deducts the days of leave of its month at the CCNL daily quota as
an unpaid absence: out of the INPS and TFR bases (art. 42 c. 5-quinquies
D.Lgs. 151/2001: the leave accrues no TFR; the days are covered by
figurative contributions).  It pays back the INPS indemnity of each
calendar day, posted as ``maternity_item``: the last monthly pay of fixed
and continuous items times the monthly payments of a year over the days of
the year of the day, at most the daily maximum of the year (c. 5-ter).
INPS circ. 64/2001 par. 4: the pay of the month "comprensiva della quota
parte di tredicesima mensilità [...] va moltiplicata per 12 e divisa per
365 giorni (366 se le assenze cadono in un anno bisestile)".  A vertical
part time divides the pay of the month by its paid days, rest days
included, which the request does not state: such a run records the open
engine limitation ``extraordinary_leave_daily_base``.
"""

from __future__ import annotations

from calendar import isleap
from dataclasses import replace
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
#: The paid days of a vertical part time, its daily divisor, are not stated.
EXTRAORDINARY_BASE_LIMITATION = "extraordinary_leave_daily_base"
_DEDUCTION = "absence_deduction"
_MONTHS = 12
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
    first: date, last: date, yearly: Decimal, rates: ExtraordinaryLeaveRates
) -> tuple[Decimal, set[int]]:
    """Return the indemnity of the days ``first``-``last`` and the unknown years.

    Args:
        first: First day of leave of the run.
        last: Last day of leave of the run.
        yearly: The last pay times the monthly payments of a year.
        rates: The statutory maximum of each year.

    Returns:
        The sum of each day's indemnity, ``yearly`` over the days of its
        year and at most its year's maximum, rounded to the cent; and the
        years of the days without a known maximum.
    """
    total, unknown = Decimal(0), set()
    day = first
    while day <= last:
        daily = yearly / (366 if isleap(day.year) else 365)
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
    yearly = last_pay * (_MONTHS + terms.pay.extra_months)
    amount, unknown = _indemnity(*span, yearly, terms.rates.extraordinary_leave)
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
    decision = _decision(EXTRAORDINARY, terms, span, pay, modelled=True, advanced=True)
    if issues:
        provisional = CalculationStatus.PROVISIONAL
        decision = replace(decision, status=provisional, reason_code=issues[0].code)
    effect.decisions = [decision]
    effect.issues = issues
    effect.limitations = (EXTRAORDINARY_BASE_LIMITATION,) if terms.vertical else ()
    return effect
