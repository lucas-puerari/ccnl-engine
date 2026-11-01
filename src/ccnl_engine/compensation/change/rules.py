"""A change of level inside the month of a run: the pay of each stretch.

A worker promoted on a day other than the first of a month is paid the
level before for the days before the promotion and the new level from it
(Commercio and Terziario art. 118, DMO art. 102: "Il lavoratore promosso a
livello superiore ha diritto alla retribuzione contrattuale del nuovo
livello").  No text read says how the month is split: the engine shares the
monthly pay of the run between the two levels by the payable days of the
CCNL daily quota (its unpaid-absence rule) on each side of the promotion,
so the two stretches always make one month of the employed days.  The
chain of the run is the chain of each level times its share, component by
component, and the path is reported as the engine limitation
:data:`MID_MONTH_CHANGE`.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, NoReturn

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.proration.rules import payable_days
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.period.requests import PeriodCalculationRequest

__all__ = ["MID_MONTH_CHANGE", "MonthChange", "blended", "month_change"]

#: Engine limitation of a run that splits its month between two levels.
MID_MONTH_CHANGE = "mid_month_level_change"
_FEATURE = "employment_change"
_PAYING = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_ONE = Decimal(1)


@dataclass(frozen=True)
class MonthChange:
    """The level before a promotion inside the month and the share after it.

    Attributes:
        from_level: Level code before the promotion.
        share: Payable days from the promotion over the payable days the
            employment covers in the month.
    """

    from_level: str
    share: Decimal


def month_change(
    request: PeriodCalculationRequest, ccnl: CCNL, run_kind: RunKind
) -> MonthChange | None:
    """Return the promotion inside the month of a run that pays it, if any.

    The month is rejected (``InvalidInputError``) when the CCNL sets no
    daily quota whose payable days are defined, pays a category by the
    hour, or the employment covers no payable day of the month.

    Returns:
        The level before and the share of the days from the promotion;
        ``None`` for an extra-month run or a promotion on the first day of
        a month or outside the month.
    """
    seniority = request.seniority
    promotion = None if seniority is None else seniority.promotion
    month = request.period_id
    if (
        promotion is None
        or run_kind not in _PAYING
        or (promotion.effective_on.year, promotion.effective_on.month)
        != (month.year, month.month)
        or promotion.effective_on.day == 1
    ):
        return None
    method = _method(ccnl)
    first, last = _span(request)
    total = payable_days(method, first, last)
    after = payable_days(method, max(first, promotion.effective_on), last)
    if not total:
        _reject("the employment covers no payable day of the month")
    return MonthChange(promotion.from_level, Decimal(after) / Decimal(total))


def _method(ccnl: CCNL) -> DailyDivisorMethod:
    rules = None if ccnl.work_rules is None else ccnl.work_rules.absence_rules
    method = None if rules is None else rules.daily_divisor_method
    if ccnl.parameters.hourly_pay is not None:
        _reject("a CCNL that pays a category by the hour has one monthly total")
    if method is None or method is DailyDivisorMethod.BY_25:
        _reject("the CCNL sets no daily quota whose payable days split the month")
    return method


def _span(request: PeriodCalculationRequest) -> tuple[date, date]:
    month = request.period_id
    first = date(month.year, month.month, 1)
    last = first + timedelta(days=calendar.monthrange(month.year, month.month)[1] - 1)
    period = request.employment_period
    span = None if period is None else period.span_in_month(month.year, month.month)
    return (first, last) if span is None else span


def _reject(reason: str) -> NoReturn:
    msg = f"a change of level inside the month of the run cannot be paid: {reason}"
    raise InvalidInputError(msg, field="SeniorityFact.promotion", feature=_FEATURE)


def blended(
    before: MonthlyPayChain, after: MonthlyPayChain, share: Decimal
) -> MonthlyPayChain:
    """Return the chain of a month paid at ``before`` and then at ``after``.

    Each component is the one of ``before`` times ``1 - share`` plus the one
    of ``after`` times ``share``, rounded to the cent apart; an allowance of
    one level only counts zero on the other.

    Returns:
        The chain of the month, reporting :data:`MID_MONTH_CHANGE`.
    """
    rest = _ONE - share
    old = {a.code: (a, v) for a, v in before.allowances}
    new = {a.code: (a, v) for a, v in after.allowances}
    allowances = tuple(
        (
            (new.get(code) or old[code])[0],
            money(old.get(code, (None, Decimal(0)))[1] * rest)
            + money(new.get(code, (None, Decimal(0)))[1] * share),
        )
        for code in {**old, **new}
    )
    return MonthlyPayChain(
        base=money(before.base * rest) + money(after.base * share),
        seniority=money(before.seniority * rest) + money(after.seniority * share),
        allowances=allowances,
        limitations=(*after.limitations, MID_MONTH_CHANGE),
        seniority_excluded_from=after.seniority_excluded_from,
    )
