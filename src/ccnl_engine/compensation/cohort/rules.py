"""Take the base salary of the hire cohort of the worker."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.period.inputs import EmploymentPeriod
    from ccnl_engine.seniority.inputs import SeniorityFact

__all__ = ["hire_date", "with_hire_cohort"]


def with_hire_cohort(ccnl: CCNL, hired_on: date | None) -> CCNL:
    """Return ``ccnl`` with the base salaries of the worker's hire cohort.

    A level whose ``base_salary_by_cohort`` holds a cohort hired by a date
    on or after ``hired_on`` pays that cohort's salary (the earliest one).

    Returns:
        ``ccnl`` unchanged without a hire date or a cohort table, else a
        copy whose levels carry the cohort salaries.
    """
    if hired_on is None or not any(lv.base_salary_by_cohort for lv in ccnl.levels):
        return ccnl
    levels = []
    for level in ccnl.levels:
        cohorts = sorted(
            (c for c in level.base_salary_by_cohort if hired_on <= c.hired_until),
            key=lambda c: c.hired_until,
        )
        levels.append(
            level.model_copy(update={"base_salary": cohorts[0].base_salary})
            if cohorts
            else level
        )
    return ccnl.model_copy(update={"levels": tuple(levels)})


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
