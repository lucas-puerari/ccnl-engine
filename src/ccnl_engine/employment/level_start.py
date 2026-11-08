"""Validate the stated date of entry into an employment level."""

from calendar import monthrange
from datetime import date

from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.errors import InvalidInputError


def check_level_start(
    started_on: date | None,
    period: EmploymentPeriod | None,
    run_month: tuple[int, int] | None = None,
) -> None:
    """Check employment start and, when supplied, the competence month.

    Raises:
        InvalidInputError: If level entry precedes hire or follows the run month.
    """
    if started_on is None:
        return
    if period is not None and started_on < period.started_on:
        msg = "Employment.level_started_on precedes employment start"
        raise InvalidInputError(
            msg, field="Employment.level_started_on", feature="employment_facts"
        )
    if run_month is not None:
        year, month = run_month
        last_day = date(year, month, monthrange(year, month)[1])
        if started_on > last_day:
            msg = "Employment.level_started_on is after the run month"
            raise InvalidInputError(
                msg, field="Employment.level_started_on", feature="employment_facts"
            )
