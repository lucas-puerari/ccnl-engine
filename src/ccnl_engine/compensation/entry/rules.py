"""The level a hire on the entry pay of its CCNL is paid at."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.compensation.ladder.rules import level_below
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.models import Level

__all__ = ["entry_level"]

_FIELD = "Permanent.entry_pay"


def entry_level(
    ccnl: CCNL, level: Level, chosen: bool, hired_on: date | None, as_of: date
) -> Level:
    """Return the level the month of a permanent hire is paid at.

    A hire on the entry pay is paid the levels below of the period the
    months from the hire reach, never below the lowest level; past the last
    period, at the level.

    Returns:
        ``level`` itself without the entry pay or past its periods, else
        the lower level of the period.

    Raises:
        InvalidInputError: When the entry pay is chosen on a CCNL without
            one, at a level it excludes, or without the hire date.
    """
    if not chosen:
        return level
    rule = ccnl.entry_pay
    problem = None
    if rule is None:
        problem = f"{ccnl.meta.ccnl_id} has no entry pay"
    elif level.code in rule.excluded_levels:
        problem = f"the entry pay of {ccnl.meta.ccnl_id} excludes level {level.code}"
    elif hired_on is None:
        problem = "the entry pay needs Employment.employment_period"
    if problem is not None or rule is None or hired_on is None:
        raise InvalidInputError(str(problem), field=_FIELD, feature="base_salary")
    since = SeniorityFact.since(hired_on, SenioritySource.EMPLOYER_RECORDS)
    months = since.months_in_month(as_of.year, as_of.month)
    period = next(
        (
            p
            for p in rule.periods
            if p.months_from <= months
            and (p.months_until is None or months < p.months_until)
        ),
        None,
    )
    if period is None:
        return level
    return level_below(ccnl.levels, level, period.levels_below, clamp=True)
