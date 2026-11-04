"""The holidays of the month on a Sunday, the daily divisor and the monthly pay.

L. 54/1977 art. 1 c. 2 moves the celebration of 4 November, no longer a
holiday, to the first Sunday of November: a CCNL that grants it the
treatment of a holiday on a Sunday pays it on that Sunday, which the
holidays of the month list under the day code ``11-04``.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.calendar.holiday.models import easter_sunday
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.agreement.coverage.models import CCNLWorkRules
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.sunday_holiday.models import SundayHolidayPay
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "EASTER",
    "FOURTH_NOVEMBER",
    "STATUTORY",
    "divisor",
    "employed",
    "monthly_pay",
    "sundays",
    "unsourced",
    "whole_year",
]

#: Day code of 4 November, celebrated on the first Sunday of November.
FOURTH_NOVEMBER = "11-04"
#: Day code of Easter Sunday, a holiday of some CCNLs only.
EASTER = "easter"
#: The festa nazionale, 25 April and 1 May (L. 260/1949 art. 5).
STATUTORY = frozenset({"04-25", "05-01", "06-02"})
_NOVEMBER = 11
_SUNDAY = 6
_ZERO = Decimal(0)
_DIVISORS = {
    DailyDivisorMethod.BY_22: Decimal(22),
    DailyDivisorMethod.BY_25: Decimal(25),
    DailyDivisorMethod.BY_26: Decimal(26),
    DailyDivisorMethod.BY_30: Decimal(30),
}


def employed(ctx: RunContext, day: dt.date) -> bool:
    """Return whether the employment covers ``day``.

    Returns:
        True without an employment period, or within it.
    """
    period = ctx.request.employment_period
    if period is None:
        return True
    return period.started_on <= day and (
        period.ended_on is None or day <= period.ended_on
    )


def _first_sunday_of_november(year: int) -> dt.date:
    first = dt.date(year, _NOVEMBER, 1)
    return first + dt.timedelta(days=(_SUNDAY - first.weekday()) % 7)


def sundays(ctx: RunContext) -> list[tuple[str, dt.date, bool]]:
    """Return the national holidays of the month that fall on a Sunday.

    Returns:
        Each day code, date and whether the holiday is a recent one (with a
        ``valid_from``, as 4 October from 2026), within the employment; in
        November, also 4 November on the first Sunday of the month; Easter
        Sunday (``easter``), no holiday with civil effects, only when the
        CCNL clause names it.
    """
    year, month = ctx.request.period_id.year, ctx.request.period_id.month
    found = []
    for holiday in ctx.repo.load_national_holidays().holidays:
        day = holiday.on(year)
        if day is None or (day.month, day.weekday()) != (month, _SUNDAY):
            continue
        if employed(ctx, day):
            found.append((holiday.day, day, holiday.valid_from is not None))
    if month == _NOVEMBER:
        day = _first_sunday_of_november(year)
        if employed(ctx, day):
            found.append((FOURTH_NOVEMBER, day, False))
    rules = ctx.contract.ccnl.work_rules
    clause = None if rules is None else rules.sunday_holidays
    easter = easter_sunday(year)
    if (
        clause is not None
        and EASTER in clause.holidays
        and easter.month == month
        and employed(ctx, easter)
    ):
        found.append((EASTER, easter, False))
    return found


def divisor(rules: CCNLWorkRules | None) -> Decimal | None:
    """Return the divisor of the daily quota.

    Returns:
        The divisor of the clause, else of the CCNL absences (26 without
        absence rules); ``None`` for an absence method with no divisor.
    """
    clause = None if rules is None else rules.sunday_holidays
    if clause is not None and clause.divisor is not None:
        return clause.divisor
    absence = None if rules is None else rules.absence_rules
    if absence is None:
        return _DIVISORS[DailyDivisorMethod.BY_26]
    return _DIVISORS.get(absence.daily_divisor_method)


def monthly_pay(chain: MonthlyPayChain, excluded: frozenset[str]) -> Decimal:
    """Return the monthly pay of a full month the quota divides.

    Returns:
        The minimo, the seniority and the cash allowances (individual
        elements included) but the ``excluded`` codes.
    """
    allowances = (
        v for a, v in chain.allowances if not a.in_kind and a.code not in excluded
    )
    return money(chain.base + chain.seniority + sum(allowances, _ZERO))


def whole_year(ctx: RunContext) -> bool:
    """Return whether the employment covers the whole year of the run.

    Returns:
        True without an employment period, or with one from 1 January to
        31 December or beyond.
    """
    period = ctx.request.employment_period
    year = ctx.request.period_id.year
    return period is None or (
        period.started_on <= dt.date(year, 1, 1)
        and (period.ended_on is None or period.ended_on >= dt.date(year, 12, 31))
    )


def unsourced(
    clause: SundayHolidayPay | None,
    found: list[tuple[str, dt.date, bool]],
    *,
    unpayable: bool = False,
) -> bool:
    """Return whether a holiday of the month has no sourced treatment.

    A holiday the clause leaves out is open without a clause, or when the
    holiday is more recent than the CCNL texts (4 October from 2026); 4
    November is covered by a clause that pays it in another month.

    Returns:
        True when one holiday is open, or ``unpayable`` (a paid holiday the
        engine has no daily divisor for).
    """
    if unpayable:
        return True
    if clause is None:
        return any(c not in STATUTORY for c, _, _ in found)
    covered = set(clause.holidays)
    if clause.ex_november_fourth is not None:
        covered.add(FOURTH_NOVEMBER)
    return any(c not in covered and recent for c, _, recent in found)
