"""Position of a run toward the additional 1% IVS of its competence year.

The 1% follows competence, like the INPS base it is charged on: the runs of
one competence month share the monthly threshold, and the year is settled
by the runs of competence December and of the month the employment ends
(INPS msg. 5327/2015 par. 2.3; circ. 156/2025 par. 5); see
:mod:`~ccnl_engine.payroll.service.additional_ivs`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.additional_ivs import AdditionalIvsPosition

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.run import PayrollRunId

__all__ = ["additional_ivs_position"]

_DECEMBER = 12


def _ends_in(period: EmploymentPeriod | None, run_id: PayrollRunId) -> bool:
    """Return whether the employment ends in the month of ``run_id``.

    Returns:
        ``True`` when its last day falls in the competence month of the run.
    """
    ended_on = None if period is None else period.ended_on
    return ended_on is not None and (ended_on.year, ended_on.month) == (
        run_id.year,
        run_id.month,
    )


def additional_ivs_position(ctx: RunContext) -> AdditionalIvsPosition:
    """Return where the run of ``ctx`` stands toward the additional 1% IVS.

    Returns:
        The base this employment already declared for the run's competence
        month, the 1% already withheld on its competence year by every
        employment, and whether the run settles the year: a run of
        competence December, of the month the employment ends, or a
        termination run.
    """
    run_id = ctx.payment.run_id
    base = ctx.opening.accrual.inps_base(run_id.year)
    settles = (
        run_id.month == _DECEMBER
        or run_id.kind is RunKind.TERMINATION
        or _ends_in(ctx.request.employment_period, run_id)
    )
    return AdditionalIvsPosition(
        month_base=base.base_of_month(run_id.month),
        withheld=base.additional_ivs_withheld,
        settles=settles,
    )
