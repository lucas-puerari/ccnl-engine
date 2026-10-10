"""Whether a worker owes the contractual contribution of the CCNL.

The length of a fixed term (CNCE vademecum on Prevedi: "superiore a tre
mesi"), the contract of a worker not enrolled voluntarily (Previambiente
art. 65 c. 11: "dipendenti a tempo indeterminato, anche apprendisti") and
the calendar days worked in the month.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from ccnl_engine.payroll.contribution.inputs_pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.employment.inputs import FixedTerm
from ccnl_engine.payroll.event.facade import AbsenceEvent, SicknessEpisode

if TYPE_CHECKING:
    from ccnl_engine.contract.fund.models import (
        ContractualFundContribution,
    )
    from ccnl_engine.payroll.period.services_run_context import RunContext

__all__ = ["contributing", "not_permanent", "short_fixed_term", "worked_days"]

_DAY = timedelta(days=1)


def contributing(enrolment: object) -> bool:
    """Return whether the worker contributes to the fund voluntarily.

    A worker who confers the TFR alone adheres without contributing:
    Previambiente art. 65 c. 12 owes the contractual contribution of c. 11
    "anche [...] ai lavoratori che aderiscono al Fondo a seguito di
    conferimento, ancorché in forma tacita, del solo TFR".

    Returns:
        True for an enrolment with an employee rate above zero.
    """
    return isinstance(enrolment, PensionFundEnrolment) and not enrolment.tfr_only


def not_permanent(spec: ContractualFundContribution, ctx: RunContext) -> bool:
    """Return whether a fixed term not enrolled owes nothing under the clause.

    Returns:
        True when the clause covers the permanent contracts alone, the
        worker has a fixed term and is not enrolled voluntarily.
    """
    request = ctx.request
    return (
        spec.permanent_only
        and isinstance(request.contract_type, FixedTerm)
        and not contributing(request.pension_fund)
    )


def short_fixed_term(spec: ContractualFundContribution, ctx: RunContext) -> bool:
    """Return whether a fixed term too short for the clause owes nothing.

    A worker enrolled voluntarily owes it whatever the length; a fixed term
    without a stated end has not ended (``EmploymentPeriod.ended_on``).

    Returns:
        True when the fixed term lasts no more than the minimum months.
    """
    request = ctx.request
    period = request.employment_period
    if (
        spec.minimum_fixed_term_months is None
        or not isinstance(request.contract_type, FixedTerm)
        or isinstance(request.pension_fund, PensionFundEnrolment)
        or period is None
        or period.ended_on is None
    ):
        return False
    start = period.started_on
    year, month = divmod(start.month - 1 + spec.minimum_fixed_term_months, 12)
    first = date(start.year + year, month + 1, 1)
    month_end = date(first.year + first.month // 12, first.month % 12 + 1, 1) - _DAY
    # "superiore a tre mesi": the end must reach the same day three months on.
    return period.ended_on < first.replace(day=min(start.day, month_end.day))


def worked_days(ctx: RunContext) -> int:
    """Return the calendar days worked in the month of the run.

    The days of employment in the month, less the sick days and the days of
    an absence without any pay (CNCE vademecum: "non si considerano utili
    [...] le giornate di assenza per malattia [...] e aspettativa non
    retribuita").

    Returns:
        The number of days.
    """
    month = ctx.request.period_id
    first = date(month.year, month.month, 1)
    last = date(month.year + month.month // 12, month.month % 12 + 1, 1) - _DAY
    span = ctx.proration.span or (first, last)
    days = {span[0] + _DAY * n for n in range((span[1] - span[0]).days + 1)}
    for event in ctx.request.events:
        if isinstance(event, SicknessEpisode):
            count = (event.ended_on - event.started_on).days + 1
            days -= {event.started_on + _DAY * n for n in range(count)}
        elif isinstance(event, AbsenceEvent) and event.no_pay_due:
            days -= set(event.days)
    return len(days)
