"""Construction checks of a period calculation request.

A regular run outside the employment is described here, so that the
request raises ``InvalidInputError`` at construction instead of a silent
result deep in the calculation.  Field types are checked with
:mod:`ccnl_engine.validation`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["employment_gap"]


def employment_gap(
    period_id: PeriodId,
    run: PayrollRun | None,
    employment: EmploymentPeriod | None,
) -> str | None:
    """Describe a regular run for a month without a day of employment.

    Args:
        period_id: Competence month of the run.
        run: The run, ``None`` for the regular run of the month.
        employment: Employment period, ``None`` when not tracked.

    Returns:
        A message when the run is regular and ``employment`` has no day in
        its month, otherwise ``None``.
    """
    regular = run is None or run.run_kind is RunKind.REGULAR
    if (
        employment is None
        or not regular
        or employment.overlaps_month(period_id.year, period_id.month)
    ):
        return None
    return (
        f"regular run {period_id.year}-{period_id.month:02d} is outside the "
        f"employment ({employment.started_on} to {employment.ended_on})"
    )
