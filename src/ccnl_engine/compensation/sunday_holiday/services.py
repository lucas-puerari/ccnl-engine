"""The further daily quota of a holiday falling on a Sunday.

L. 260/1949 art. 5 (Normattiva, text of L. 90/1954, page sha256
dbd670c663744af9...): for the festa nazionale, 25 April and 1 May, the
workers "retribuiti in misura fissa" are owed, "qualora la festività
ricorra nel giorno di domenica, [...] anche una ulteriore retribuzione
corrispondente all'aliquota giornaliera" (4 November stopped being a
holiday with L. 54/1977 art. 1).  A CCNL that pays other holidays on a
Sunday names them (``work_rules.sunday_holidays``).  The quota is the
monthly pay of a full month (minimo, seniority, the allowances and the
individual elements of the chain) over the daily divisor of the clause or,
without one, of the CCNL absences.  A run of a month
with another holiday on a Sunday, in a CCNL that names none, records the
engine limitation of the clause not sourced.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.pay_item.facade import FixedAllowanceEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import (
    _make_entry,
    _require_resolution,
    _treatment_from_resolution,
)
from ccnl_engine.regime.models import EmploymentSector

if TYPE_CHECKING:
    from ccnl_engine.agreement.coverage.models import CCNLWorkRules
    from ccnl_engine.compensation.sunday_holiday.models import SundayHolidayPay
    from ccnl_engine.event.total.handlers import _EventTotals
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext

__all__ = ["CAPABILITY", "CLAUSE_LIMITATION", "SundayHoliday", "sunday_holiday"]

#: Capability of the holiday falling on a Sunday.
CAPABILITY = "sunday_holiday"
#: Engine limitation of a holiday on a Sunday the CCNL clause is not sourced for.
CLAUSE_LIMITATION = "sunday_holiday_ccnl_clause"
#: The festa nazionale, 25 April and 1 May (L. 260/1949 art. 5).
STATUTORY = frozenset({"04-25", "05-01", "06-02"})
_KIND = "fixed_allowance_earning"
_RULE = "law/sunday-holiday:l260-1949-art5"
_SUNDAY = 6
_DIVISORS = {
    DailyDivisorMethod.BY_22: Decimal(22),
    DailyDivisorMethod.BY_25: Decimal(25),
    DailyDivisorMethod.BY_26: Decimal(26),
    DailyDivisorMethod.BY_30: Decimal(30),
}
_ZERO = Decimal(0)


@dataclass(frozen=True)
class SundayHoliday:
    """The further quota of the run and what it adds to the totals."""

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    amount: Decimal = _ZERO
    taxed: tuple[bool, bool, bool] = (False, False, False)
    decisions: tuple[CalculationDecision, ...] = ()
    limitations: frozenset[str] = frozenset()

    def added_to(self, totals: _EventTotals) -> _EventTotals:
        """Return ``totals`` with the quota in its bases and its decision.

        Returns:
            A copy of ``totals``.
        """
        inps, tfr, irpef = (self.amount if t else _ZERO for t in self.taxed)
        return replace(
            totals,
            inps_base=totals.inps_base + inps,
            tfr_base=totals.tfr_base + tfr,
            irpef_base=totals.irpef_base + irpef,
            decisions=totals.decisions + self.decisions,
            limitations=totals.limitations | self.limitations,
        )


def _employed(ctx: RunContext, day: dt.date) -> bool:
    period = ctx.request.employment_period
    if period is None:
        return True
    return period.started_on <= day and (
        period.ended_on is None or day <= period.ended_on
    )


def _sundays(ctx: RunContext) -> list[tuple[str, dt.date, bool]]:
    """Return the national holidays of the month that fall on a Sunday.

    Returns:
        Each day code, date and whether the holiday is a recent one (with a
        ``valid_from``, as 4 October from 2026), within the employment.
    """
    year, month = ctx.request.period_id.year, ctx.request.period_id.month
    found = []
    for holiday in ctx.repo.load_national_holidays().holidays:
        day = holiday.on(year)
        if day is None or (day.month, day.weekday()) != (month, _SUNDAY):
            continue
        if _employed(ctx, day):
            found.append((holiday.day, day, holiday.valid_from is not None))
    return found


def _decision(
    ctx: RunContext, reason: str, inputs: dict[str, Decimal | str], amount: Decimal
) -> CalculationDecision:
    return CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code=reason,
        rule=_RULE,
        rule_version=str(ctx.fiscal_year),
        inputs=inputs,
        amount=amount,
    )


def _divisor(rules: CCNLWorkRules | None) -> Decimal | None:
    clause = None if rules is None else rules.sunday_holidays
    if clause is not None and clause.divisor is not None:
        return clause.divisor
    absence = None if rules is None else rules.absence_rules
    if absence is None:
        return _DIVISORS[DailyDivisorMethod.BY_26]
    return _DIVISORS.get(absence.daily_divisor_method)


def _paid(
    ctx: RunContext,
    clause: SundayHolidayPay | None,
    days: list[dt.date],
    divisor: Decimal,
) -> SundayHoliday:
    """Return the earning, entry and decision of ``days`` at the daily quota.

    Returns:
        The quota of the monthly pay of a full month over ``divisor``, once
        a day.
    """
    chain = ctx.regular_chain
    monthly = money(chain.base + chain.seniority + chain.allowances_total)
    amount = money(monthly / divisor * len(days))
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"sunday_holiday_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    location = None if clause is None else clause.provenance.location
    section = None if location is None else location.section
    source = section or ("the CCNL" if clause is not None else "L. 260/1949 art. 5")
    item = FixedAllowanceEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=Decimal(len(days)),
        amount=amount,
        source=f"Festività cadente di domenica: {source}",
    )
    entry = _make_entry(
        item_id,
        item_id,
        _KIND,
        ctx.cp,
        payment,
        AccountKind.CASH_EARNINGS,
        amount,
        policy_id=resolution.policy_id,
    )
    inputs: dict[str, Decimal | str] = {
        "days": ",".join(d.isoformat() for d in days),
        "divisor": divisor,
        "monthly": monthly,
    }
    reason = "ccnl_clause" if clause is not None else "statutory"
    return SundayHoliday(
        items=(item,),
        entries=(entry,),
        amount=amount,
        taxed=(treatment.inps, treatment.tfr, treatment.irpef),
        decisions=(_decision(ctx, reason, inputs, amount),),
    )


def sunday_holiday(ctx: RunContext) -> SundayHoliday:
    """Return the further quota of the holidays of the month on a Sunday.

    Returns:
        Nothing without such a holiday; the limitation of a holiday the
        CCNL clause is not sourced for (and of every holiday of a public
        employment, whose treatment is not sourced, or of a CCNL without a
        daily divisor the engine applies), with a nil decision
        when nothing is paid; the earning, entry and decision of the paid
        holidays at the CCNL daily quota.
    """
    sundays = _sundays(ctx)
    if not sundays:
        return SundayHoliday()
    rules = ctx.contract.ccnl.work_rules
    clause = None if rules is None else rules.sunday_holidays
    paid = STATUTORY if clause is None else frozenset(clause.holidays)
    public = ctx.request.sector is EmploymentSector.PUBLIC
    days = [d for code, d, _ in sundays if code in paid and not public]
    # A holiday the clause leaves out is open without a clause, or when the
    # holiday is more recent than the CCNL texts (4 October from 2026).
    # A paid holiday without a daily divisor the engine applies is open too.
    divisor = _divisor(rules)
    open_clause = (
        public
        or (bool(days) and divisor is None)
        or any(c not in paid and (clause is None or recent) for c, _, recent in sundays)
    )
    limitations = frozenset({CLAUSE_LIMITATION} if open_clause else ())
    if not days or divisor is None:
        listed = ",".join(d.isoformat() for _, d, _ in sundays)
        unpaid = _decision(ctx, "not_paid", {"days": listed}, _ZERO)
        result = SundayHoliday(decisions=(unpaid,))
    else:
        result = _paid(ctx, clause, days, divisor)
    return replace(result, limitations=limitations)
