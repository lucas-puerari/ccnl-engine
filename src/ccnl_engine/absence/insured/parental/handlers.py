"""Handler of a parental leave: deduction and INPS indemnity.

The run deducts the days of leave of its month at the CCNL daily quota as
an unpaid absence: out of the INPS and TFR bases, since art. 2120 c. 3
c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the
wage integration.  It pays back the INPS indemnity of each day at its
rate (art. 34 D.Lgs. 151/2001), on the pay of the month before the leave
(art. 23), advanced by the employer and posted as ``maternity_item``.  The
bundle holds no CCNL treatment of the leave: the run pays the statutory
amounts only.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.base.rules import leave_base
from ccnl_engine.absence.insured.handlers import (
    _decision,
    _no_quota,
    _not_modelled,
    _span,
)
from ccnl_engine.absence.insured.parental.rules import (
    allocate,
    indemnity,
    run_daily_base,
)
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveEvent
    from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

__all__ = [
    "PARENTAL",
    "PARENTAL_BASE_LIMITATION",
    "PARENTAL_BASE_UNKNOWN",
    "PARENTAL_EXTRA_MONTH_LIMITATION",
    "PARENTAL_INCOME_LIMITATION",
    "PARENTAL_SPLIT_LIMITATION",
    "PROTECTION_END_UNKNOWN",
    "_handle_parental_leave",
]

#: Capability of a parental leave.
PARENTAL = "parental_leave"
#: INPS pays a parental indemnity and the leave states no base.
PARENTAL_BASE_UNKNOWN = "parental_base_pay_unknown"
#: Parental leave paid on the pay of the run: the base of art. 23 is not computed.
PARENTAL_BASE_LIMITATION = "parental_daily_base"
#: Days beyond the indemnified months: the income condition is not modelled.
PARENTAL_INCOME_LIMITATION = "parental_income_condition"
#: A counter ends inside a calendar month not of thirty days.
PARENTAL_SPLIT_LIMITATION = "parental_month_split"
#: The extra months of the leave are accrued in full at the employer's charge.
PARENTAL_EXTRA_MONTH_LIMITATION = "parental_extra_month_share"
#: The unstated end of the protected leave could give more enhanced months.
PROTECTION_END_UNKNOWN = "parental_protection_end_unknown"
_DEDUCTION = "absence_deduction"


def _cohort_issue() -> CalculationIssue:
    return CalculationIssue(
        code=PROTECTION_END_UNKNOWN,
        message=(
            "the months INPS pays at 80% depend on the day the last maternity "
            "or paternity leave of the couple ended "
            "(ParentalLeaveEvent.protection_ended_on), which the leave does not "
            "state; the days are paid on the months the birth day gives"
        ),
        status=CalculationStatus.PROVISIONAL,
        capability=PARENTAL,
        fact="protection_ended_on",
    )


def _handle_parental_leave(
    event: ParentalLeaveEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days of the parental leave in the month of the run.

    Returns:
        The items, entries, base deltas, decision, issues and limitations of
        the leave.
    """
    terms = ctx.insured
    span = _span(event, terms, PARENTAL)
    if terms is None or terms.pay is None:
        return _no_quota(PARENTAL)
    rates = terms.rates.parental
    days = allocate(event, rates)
    base = leave_base(
        event.parental_base_pay,
        terms,
        event.started_on,
        capability=PARENTAL,
        field="ParentalLeaveEvent.parental_base_pay",
        code=PARENTAL_BASE_UNKNOWN,
        limitation=PARENTAL_BASE_LIMITATION,
    )
    daily = base.rmgg
    if daily is None:
        daily = run_daily_base(terms.pay, rates.daily_divisor)
    units, deduction = terms.pay.deducted(*span)
    in_span = [day for day in days.rates if span[0] <= day <= span[1]]
    pay = InsuredPay(units, deduction, indemnity(days, *span, daily), len(in_span))
    effect = post_lines(
        (
            ("abs", -pay.deduction, _DEDUCTION, pay.units),
            ("inps", pay.indemnity, "maternity_item", Decimal(pay.days)),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(PARENTAL, terms, span, pay, modelled=False, advanced=True)
    ]
    effect.issues = [_not_modelled(PARENTAL), *base.issues]
    if days.cohort_unknown:
        effect.issues.append(_cohort_issue())
    limitations = [*base.limitations, PARENTAL_EXTRA_MONTH_LIMITATION]
    if any(days.rates[day] is None for day in in_span):
        limitations.append(PARENTAL_INCOME_LIMITATION)
    if days.split.intersection(in_span):
        limitations.append(PARENTAL_SPLIT_LIMITATION)
    effect.limitations = tuple(limitations)
    return effect
