"""Take the base salary of the hire cohort of the worker."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.run.types import PeriodId
    from ccnl_engine.seniority.inputs import SeniorityFact

__all__ = ["hire_date", "with_hire_cohort"]


def with_hire_cohort(
    ccnl: CCNL,
    period: EmploymentPeriod | None,
    seniority: SeniorityFact | None,
    period_id: PeriodId,
) -> CCNL:
    """Return ``ccnl`` with the base salaries of the worker's hire cohort.

    A level whose ``base_salary_by_cohort`` holds a cohort hired by a date
    on or after the hire date pays that cohort's salary (the earliest one);
    a level with ``class_tables`` pays the class of the worker's service
    in the table of the cohort, and the CCNL increments are then not paid.

    Returns:
        ``ccnl`` unchanged without a hire date or a cohort table, else a
        copy whose levels carry the cohort salaries.
    """
    hired_on = hire_date(period, seniority)
    if hired_on is None or not any(
        lv.base_salary_by_cohort or lv.class_tables for lv in ccnl.levels
    ):
        return ccnl
    months = (
        None
        if seniority is None
        else seniority.months_in_month(period_id.year, period_id.month)
    )
    levels = [_cohort_level(level, hired_on, months) for level in ccnl.levels]
    update: dict[str, object] = {"levels": tuple(levels)}
    if months is not None and any(lv.class_tables for lv in ccnl.levels):
        increments = ccnl.parameters.seniority_increments.model_copy(
            update={"maximum_count": 0, "amount_by_level": {}}
        )
        update["parameters"] = ccnl.parameters.model_copy(
            update={"seniority_increments": increments}
        )
    return ccnl.model_copy(update=update)


def _cohort_level(level: Level, hired_on: date, months: int | None) -> Level:
    """Return ``level`` with the salary of the worker's cohort and class.

    Returns:
        The level paid the class of ``months`` in the first class table of
        a cohort that holds ``hired_on``, else the cohort salary, else the
        level unchanged.
    """
    tables = sorted(
        (
            t
            for t in level.class_tables
            if t.hired_until is None or hired_on <= t.hired_until
        ),
        key=lambda t: (t.hired_until is None, t.hired_until or hired_on),
    )
    if tables and months is not None:
        return level.model_copy(update={"base_salary": tables[0].salary(months)})
    cohorts = sorted(
        (c for c in level.base_salary_by_cohort if hired_on <= c.hired_until),
        key=lambda c: c.hired_until,
    )
    if cohorts:
        return level.model_copy(update={"base_salary": cohorts[0].base_salary})
    return level


def hire_date(
    period: EmploymentPeriod | None, seniority: SeniorityFact | None
) -> date | None:
    """Return the hire date: stated, else the start of the stated seniority.

    Returns:
        ``EmploymentPeriod.started_on``, else the first day of the month
        ``SeniorityFact.months`` before its ``as_of``; ``None`` without either.
    """
    if period is not None:
        return period.started_on
    if seniority is None:
        return None
    months = seniority.as_of.year * 12 + seniority.as_of.month - 1 - seniority.months
    return date(months // 12, months % 12 + 1, 1)
