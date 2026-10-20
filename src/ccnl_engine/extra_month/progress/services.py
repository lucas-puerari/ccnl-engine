"""Ratei of the extra months accrued by the end of a run's month.

A payslip prints the ratei maturati of the tredicesima and quattordicesima:
the months of the current accrual window the employment has accrued by the
end of the month of the run, counted by the CCNL month rule as the
extra-month run would count them
(:func:`~ccnl_engine.extra_month.services.run_accrual`).
The absences of the earlier runs that suspend accrual are not in the
request: their months count as accrued.
"""

from __future__ import annotations

import calendar
from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.calendar.services import standard_calendar
from ccnl_engine.employment.fact.inputs import EmploymentPeriod
from ccnl_engine.extra_month.models import ExtraMonthAccrual
from ccnl_engine.extra_month.progress.models import ExtraMonthProgress
from ccnl_engine.extra_month.qualification.services import month_accrual_rule
from ccnl_engine.extra_month.services import run_schedule
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

__all__ = ["run_extra_month_progress"]

_PAYING = frozenset({RunKind.REGULAR, RunKind.TERMINATION})


def run_extra_month_progress(ctx: RunContext) -> tuple[ExtraMonthProgress, ...]:
    """Return the ratei maturati of each extra month of the CCNL.

    Returns:
        One entry per extra month, in payment order, for a regular or a
        termination run; nothing for any other run.
    """
    request = ctx.request
    run = request.run
    if run is None or run.run_kind not in _PAYING:
        return ()
    ccnl = ctx.contract.ccnl
    year, month = run.year, run.month
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    period = request.employment_period
    started = date.min if period is None else period.started_on
    ended = month_end if period is None or period.ended_on is None else period.ended_on
    to_date = EmploymentPeriod(started, min(ended, month_end))
    standard = standard_calendar(ccnl, year, ctx.contract.tctx.competence)
    rule = month_accrual_rule(ccnl)
    progress = []
    for extra in standard.extra_months:
        payment_year = year if month <= extra.payment_month else year + 1
        schedule = run_schedule(extra.kind, extra.payment_month, extra.max_fraction)
        accrual = ExtraMonthAccrual.of(
            schedule, payment_year, to_date, rule=rule, pattern=request.work_pattern
        )
        progress.append(
            ExtraMonthProgress(
                kind=extra.kind,
                payment_year=payment_year,
                months=accrual.accrued,
                fraction=accrual.fraction,
            )
        )
    return tuple(progress)
