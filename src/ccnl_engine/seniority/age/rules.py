"""The months of service a CCNL counts for the increments, from an age.

A worker hired young under a CCNL that counts the increments only from an
age (:class:`~ccnl_engine.seniority.age.models.SeniorityAge`) accrues them
from the birthday of that age: the run counts the months completed since
then, never more than its recognised seniority.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource

if TYPE_CHECKING:
    from ccnl_engine.seniority.age.models import SeniorityAge

__all__ = ["months_from_age"]


def _birthday(birth: date, age: int) -> date:
    """Return the day ``birth`` turns ``age``.

    Returns:
        The same day ``age`` years later, 1 March for a 29 February.
    """
    year = birth.year + age
    if (birth.month, birth.day) == (2, 29):
        try:
            return date(year, 2, 29)
        except ValueError:
            return date(year, 3, 1)
    return date(year, birth.month, birth.day)


def months_from_age(
    months: int,
    rule: SeniorityAge | None,
    birth: date | None,
    hired_on: date | None,
    competence: date,
) -> int:
    """Return the months of service the increments of the run count.

    Returns:
        ``months``, or the months completed by ``competence`` since the
        worker turned the age of ``rule`` when the rule covers the hire
        and that birthday is later than the hire, whichever is fewer.
    """
    if rule is None or birth is None or hired_on is None or hired_on < rule.hired_from:
        return months
    adult = _birthday(birth, rule.age)
    if adult <= hired_on:
        return months
    if adult > competence:
        return 0
    since = SeniorityFact.since(adult, SenioritySource.EMPLOYER_RECORDS)
    return min(months, since.months_in_month(competence.year, competence.month))
