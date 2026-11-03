"""The further daily quota of a holiday falling on a Sunday.

L. 260/1949 art. 5 (Normattiva, text of L. 90/1954, page sha256
dbd670c663744af9...): for the festa nazionale, 25 April and 1 May, the
workers "retribuiti in misura fissa" are owed, "qualora la festività
ricorra nel giorno di domenica, [...] anche una ulteriore retribuzione
corrispondente all'aliquota giornaliera" (4 November stopped being a
holiday with L. 54/1977 art. 1).  A CCNL that pays other holidays on a
Sunday names them (``work_rules.sunday_holidays``), 4 November among them
when it grants its celebration on the first Sunday of November the same
treatment; a CCNL may pay 4 November in another month instead.  The quota
is the monthly pay of a full month (:func:`~.rules.monthly_pay`) over the
daily divisor of the clause or, without one, of the CCNL absences.  A run
of a month with another holiday on a Sunday, 4 November included, in a
CCNL that names none, records the engine limitation of the clause not
sourced.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.compensation.sunday_holiday.rules import (
    STATUTORY,
    divisor,
    monthly_pay,
    sundays,
    unsourced,
    whole_year,
)
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
_KIND = "fixed_allowance_earning"
_RULE = "law/sunday-holiday:l260-1949-art5"
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

    def plus(self, other: SundayHoliday) -> SundayHoliday:
        """Return the two quotas of the run together.

        Returns:
            The items, entries, amounts, decisions and limitations of both,
            taxed as the one that pays (both are the same kind of item).
        """
        return SundayHoliday(
            items=self.items + other.items,
            entries=self.entries + other.entries,
            amount=self.amount + other.amount,
            taxed=self.taxed if self.items else other.taxed,
            decisions=self.decisions + other.decisions,
            limitations=self.limitations | other.limitations,
        )

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


def _posted(
    ctx: RunContext,
    item: tuple[str, Decimal, Decimal, str],
    reason: str,
    inputs: dict[str, Decimal | str],
) -> SundayHoliday:
    """Return the earning, entry and decision of a quota.

    ``item`` is the item id suffix, the quantity, the amount and the source.

    Returns:
        The quota posted as a fixed allowance of the month.
    """
    suffix, quantity, amount, source = item
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.policy_context)
    treatment = _treatment_from_resolution(resolution)
    item_id = f"{suffix}_{ctx.run_id}"
    payment = ctx.contract.tctx.payment
    earning = FixedAllowanceEarning(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=payment,
        quantity=quantity,
        amount=amount,
        source=source,
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
    return SundayHoliday(
        items=(earning,),
        entries=(entry,),
        amount=amount,
        taxed=(treatment.inps, treatment.tfr, treatment.irpef),
        decisions=(_decision(ctx, reason, inputs, amount),),
    )


def _section(clause: SundayHolidayPay | None, law: str) -> str:
    if clause is None:
        return law
    location = clause.provenance.location
    section = None if location is None else location.section
    return section or "the CCNL"


def _paid(
    ctx: RunContext,
    clause: SundayHolidayPay | None,
    days: list[dt.date],
    by: Decimal,
) -> SundayHoliday:
    """Return the earning, entry and decision of ``days`` at the daily quota.

    Returns:
        The quota of the monthly pay of a full month over ``by``, once a day.
    """
    excluded = frozenset() if clause is None else clause.excluded
    monthly = monthly_pay(ctx.regular_chain, excluded)
    amount = money(monthly / by * len(days))
    source = _section(clause, "L. 260/1949 art. 5")
    inputs: dict[str, Decimal | str] = {
        "days": ",".join(d.isoformat() for d in days),
        "divisor": by,
        "monthly": monthly,
    }
    return _posted(
        ctx,
        (
            "sunday_holiday",
            Decimal(len(days)),
            amount,
            f"Festività cadente di domenica: {source}",
        ),
        "ccnl_clause" if clause is not None else "statutory",
        inputs,
    )


def _ex_november_fourth(
    ctx: RunContext, clause: SundayHolidayPay | None, *, public: bool
) -> SundayHoliday:
    """Return the pay of 4 November a CCNL carries in a month of its own.

    Returns:
        Nothing in another month; the share of the monthly pay in its
        month, with the limitation of an employment that does not cover
        the whole year (the CCNL pays it "in ragione annua").
    """
    ex = None if clause is None or public else clause.ex_november_fourth
    if clause is None or ex is None or ctx.request.period_id.month != ex.month:
        return SundayHoliday()
    monthly = monthly_pay(ctx.regular_chain, clause.excluded)
    amount = money(monthly * ex.hours / ex.hourly_divisor)
    location = ex.provenance.location
    section = None if location is None else location.section
    posted = _posted(
        ctx,
        (
            "ex_november_fourth",
            Decimal(1),
            amount,
            f"Ex festività 4 novembre: {section}",
        ),
        "ex_november_fourth",
        {"monthly": monthly, "hours": ex.hours, "hourly_divisor": ex.hourly_divisor},
    )
    if whole_year(ctx):
        return posted
    return replace(posted, limitations=frozenset({CLAUSE_LIMITATION}))


def sunday_holiday(ctx: RunContext) -> SundayHoliday:
    """Return the further quota of the holidays of the month on a Sunday.

    Returns:
        Nothing without such a holiday, or when the CCNL pays none of them
        in the month; the limitation of a holiday the CCNL clause is not
        sourced for (and of every holiday of a public employment, whose
        treatment is not sourced, or of a CCNL without a daily divisor the
        engine applies), with a nil decision when nothing is paid; the
        earning, entry and decision of the paid holidays at the CCNL daily
        quota; with the pay of 4 November of a CCNL that carries it in a
        month of its own.
    """
    rules = ctx.contract.ccnl.work_rules
    clause = None if rules is None else rules.sunday_holidays
    public = ctx.request.sector is EmploymentSector.PUBLIC
    ex = _ex_november_fourth(ctx, clause, public=public)
    found = sundays(ctx)
    paid = STATUTORY if clause is None else frozenset(clause.holidays)
    days = [] if public else [d for code, d, _ in found if code in paid]
    by = divisor(rules)
    # A paid holiday without a daily divisor the engine applies is open too.
    open_clause = bool(found) and (
        public or unsourced(clause, found, unpayable=bool(days) and by is None)
    )
    if days and by is not None:
        result = _paid(ctx, clause, days, by)
    elif open_clause:
        listed = ",".join(d.isoformat() for _, d, _ in found)
        result = SundayHoliday(
            decisions=(_decision(ctx, "not_paid", {"days": listed}, _ZERO),)
        )
    else:
        # No holiday, or all paid apart or not at all.
        return ex
    limitations = frozenset({CLAUSE_LIMITATION} if open_clause else ())
    return replace(result, limitations=limitations).plus(ex)
