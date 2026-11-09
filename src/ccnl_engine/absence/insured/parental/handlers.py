"""Handler of a parental leave: deduction and INPS indemnity.

The run deducts the days of leave of its month at the CCNL daily quota as
an unpaid absence: out of the INPS and TFR bases, since art. 2120 c. 3
c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the
wage integration.  It pays back the INPS indemnity of each day at its
rate (art. 34 D.Lgs. 151/2001), on the pay of the month before the leave
(art. 23), advanced by the employer and posted as ``maternity_item``.
A configured CCNL rule supplements eligible days up to its cap. Where the
maternity rule explicitly covers parental leave in the sixth month of absence,
its target also applies to days in the thirty-day window after compulsory leave.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.base.rules import leave_base, run_daily_base
from ccnl_engine.absence.insured.handlers import (
    _decision,
    _no_quota,
    _not_modelled,
    _span,
)
from ccnl_engine.absence.insured.parental.holiday import (
    covered_parental_holidays,
    parental_holiday_extra,
    parental_holiday_units,
)
from ccnl_engine.absence.insured.parental.rules import allocate, indemnity
from ccnl_engine.absence.insured.parental.top_up import (
    sixth_month_days,
    sixth_month_integration,
)
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.absence.insured.models import ParentalTopUp
    from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveEvent
    from ccnl_engine.absence.insured.parental.rules import ParentalDays
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


def _top_up_days(
    event: ParentalLeaveEvent,
    days: ParentalDays,
    span: tuple[date, date],
    rules: ParentalTopUp | None,
    standard_rate: Decimal,
) -> list[date]:
    """Select qualifying days, counting previous months of this event.

    Returns:
        Days within the run's span that remain under the cap.
    """
    if rules is None or event.topped_up_days_before is None:
        return []
    if rules.only_standard_rate and event.single_parent:
        return []
    eligible = [
        day
        for day, rate in days.rates.items()
        if day <= span[1]
        and (rules.valid_from is None or day >= rules.valid_from)
        and rate is not None
        and (not rules.only_standard_rate or rate == standard_rate)
    ]
    remaining = max(0, rules.max_days - event.topped_up_days_before)
    return [day for day in eligible[:remaining] if day >= span[0]]


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
    rules = None if terms.rules is None else terms.rules.parental
    maternity = None if terms.rules is None else terms.rules.maternity
    sixth = (
        maternity if maternity is not None and maternity.parental_sixth_month else None
    )
    sixth_days, missing_sixth_end = sixth_month_days(event, in_span, sixth)
    missing_counter = rules is not None and event.topped_up_days_before is None
    eligible = _top_up_days(event, days, span, rules, rates.indemnity_rate)
    integration = (
        money(
            sum(
                (
                    max(Decimal(0), rules.rate * daily - (days.rates[day] or 0) * daily)
                    for day in eligible
                ),
                Decimal(0),
            )
        )
        if rules is not None
        else Decimal(0)
    )
    integration += sixth_month_integration(sixth_days, days.rates, daily, sixth)
    holiday = getattr(maternity, "parental_holiday", None)
    has_rule = rules is not None or sixth is not None or holiday is not None
    holiday_days = covered_parental_holidays(
        holiday,
        *span,
        None if terms.employer is None else terms.employer.patron_saint_day,
    )
    integration += parental_holiday_extra(
        holiday,
        *span,
        terms.pay,
        daily,
        days.rates,
        eligible,
        getattr(rules, "rate", Decimal(0)),
        sixth_days,
        getattr(sixth, "next_integration_rate", Decimal(0)),
        holiday_days,
    )
    pay = InsuredPay(
        units, deduction, indemnity(days, *span, daily), len(in_span), integration
    )
    effect = post_lines(
        (
            ("abs", -pay.deduction, _DEDUCTION, pay.units),
            ("inps", pay.indemnity, "maternity_item", Decimal(pay.days)),
            (
                "intg",
                pay.integration,
                "absence_integration_item",
                Decimal(
                    len(eligible)
                    + len(sixth_days)
                    + parental_holiday_units(holiday_days, in_span, days.rates)
                ),
            ),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(
            PARENTAL,
            terms,
            span,
            pay,
            modelled=has_rule and not missing_counter and not missing_sixth_end,
            advanced=True,
        )
    ]
    effect.issues = [
        *([] if has_rule else [_not_modelled(PARENTAL)]),
        *base.issues,
    ]
    effect.issues.extend(
        _fact_issues(missing_counter, missing_sixth_end, days.cohort_unknown)
    )
    effect.limitations = _parental_limitations(base.limitations, days, in_span)
    return effect


def _parental_limitations(
    base: tuple[str, ...], days: ParentalDays, in_span: list[date]
) -> tuple[str, ...]:
    """Keep the base and parental leave limitations on the covered days.

    Returns:
        Limitations of the run's portion of the parental leave.
    """
    limitations = [*base, PARENTAL_EXTRA_MONTH_LIMITATION]
    if any(days.rates[day] is None for day in in_span):
        limitations.append(PARENTAL_INCOME_LIMITATION)
    if days.split.intersection(in_span):
        limitations.append(PARENTAL_SPLIT_LIMITATION)
    return tuple(limitations)


def _fact_issues(
    missing_counter: bool, missing_sixth_end: bool, cohort_unknown: bool
) -> list[CalculationIssue]:
    """Report the absent facts needed to determine parental integration.

    Returns:
        Issues for an unknown supplement history or protected leave end.
    """
    issues: list[CalculationIssue] = []
    if missing_counter:
        issues.append(
            CalculationIssue(
                code="parental_top_up_history_unknown",
                message=(
                    "ParentalLeaveEvent.topped_up_days_before is required to cap "
                    "the CCNL supplement across runs; no top-up is posted"
                ),
                status=CalculationStatus.INCOMPLETE,
                capability=PARENTAL,
                fact="topped_up_days_before",
                cause=IssueCause.FACT,
            )
        )
    if missing_sixth_end:
        issues.append(
            CalculationIssue(
                code="parental_sixth_month_end_unknown",
                message=(
                    "ParentalLeaveEvent.protection_ended_on is required to determine "
                    "whether this leave falls in the sixth month of maternity absence"
                ),
                status=CalculationStatus.INCOMPLETE,
                capability=PARENTAL,
                fact="protection_ended_on",
                cause=IssueCause.FACT,
            )
        )
    if cohort_unknown:
        issues.append(_cohort_issue())
    return issues
