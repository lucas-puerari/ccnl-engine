"""A change of level, hours or category during the employment, and its timeline.

A worker promoted, or moved from full time to part time, keeps the same
employment relationship: only the terms that price a month change, on a
date.  :class:`EmploymentChange` states such a change; :func:`timeline`
applies the changes of a competence year to the employment in force at
its start and returns the employment in force from each date.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from typing import TYPE_CHECKING

from ccnl_engine.collection.validators import items_of_type, tuple_of
from ccnl_engine.employment.category.models import (
    WorkerCategory,
    parse_worker_category,
)
from ccnl_engine.employment.fact.inputs import WeeklyHours
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import SeniorityPromotion
from ccnl_engine.validators import reject, require_instances, require_str

if TYPE_CHECKING:
    from ccnl_engine.employment.inputs import Employment

__all__ = ["EmploymentChange", "timeline"]

_FEATURE = "employment_change"
_OWNER = "EmploymentChange"


@dataclass(frozen=True)
class EmploymentChange:
    """New terms of the employment from a date: level, weekly hours, category.

    A field left ``None`` keeps the value in force before the change.  The
    change applies from :attr:`effective_on`, the first day of a month: the
    runs of that month and of the months after price it (see
    :class:`~ccnl_engine.CompetenceYearPlan`).

    Attributes:
        effective_on: First day of the new terms.
        level_code: New contractual level, e.g. ``"4"``; ``None`` keeps it.
        weekly_hours: New contracted weekly hours; ``None`` keeps them.  To
            return to full time, state the full-time hours.
        category: New worker category, or its string value; ``None`` keeps
            it.

    Raises:
        InvalidInputError: When ``effective_on`` is not a date, a field is
            not of its type, ``level_code`` is blank, ``category`` names no
            known value, or no field changes.
    """

    effective_on: date
    level_code: str | None = None
    weekly_hours: WeeklyHours | None = None
    category: WorkerCategory | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if isinstance(self.effective_on, datetime) or not isinstance(
            self.effective_on, date
        ):
            reject(
                f"{_OWNER}.effective_on",
                "a date (not a datetime)",
                self.effective_on,
                feature=_FEATURE,
            )
        require_str(
            self.level_code,
            f"{_OWNER}.level_code",
            feature=_FEATURE,
            non_blank=True,
            optional=True,
        )
        require_instances(
            _OWNER,
            (("weekly_hours", self.weekly_hours, WeeklyHours, True),),
            feature=_FEATURE,
        )
        object.__setattr__(self, "category", parse_worker_category(self.category))
        if (self.level_code, self.weekly_hours, self.category) == (None, None, None):
            msg = "an employment change must state a level, weekly hours or category"
            raise InvalidInputError(msg, field=_OWNER, feature=_FEATURE)

    def applied_to(self, employment: Employment) -> Employment:
        """Return ``employment`` with the terms this change states.

        A change of level records it on the seniority as its last
        promotion (:class:`~ccnl_engine.seniority.inputs.SeniorityPromotion`),
        for a CCNL that reprices the earlier increments at the next one.

        Returns:
            A copy of ``employment``, validated again: weekly hours above
            the full-time hours raise ``InvalidInputError``.
        """
        seniority = employment.seniority
        level = self.level_code or employment.level_code
        if seniority is not None and level != employment.level_code:
            promotion = SeniorityPromotion(self.effective_on, employment.level_code)
            seniority = replace(seniority, promotion=promotion)
        return replace(
            employment,
            level_code=level,
            weekly_hours=self.weekly_hours or employment.weekly_hours,
            category=self.category or employment.category,
            seniority=seniority,
        )


def timeline(
    employment: Employment, changes: object, year: int, path: str
) -> tuple[tuple[date, Employment], ...]:
    """Return the employment in force from each change of ``year``.

    Args:
        employment: The employment in force on 1 January of ``year``, or on
            its start when it starts in ``year``.
        changes: The changes, a tuple or a list of :class:`EmploymentChange`.
        year: The competence year.
        path: Field the changes are read from, for the errors.

    Returns:
        ``(effective_on, employment from that day)`` per change, in date
        order.

    The changes are rejected with
    :class:`~ccnl_engine.errors.InvalidInputError` when one is not an
    :class:`EmploymentChange`, the dates are not strictly increasing, a
    change falls outside ``year`` or outside the employment period (on its
    first day included), or a change on a day other than the first of a
    month states weekly hours or keeps the level: only a promotion splits a
    month (:mod:`~ccnl_engine.compensation.change.rules`).
    """
    item = items_of_type(EmploymentChange, feature=_FEATURE)
    validated = tuple_of(changes, path, item, feature=_FEATURE)
    in_force: list[tuple[date, Employment]] = []
    current = employment
    previous: date | None = None
    for i, change in enumerate(validated):
        _check_date(change, previous, current, year, f"{path}[{i}]")
        previous = change.effective_on
        current = change.applied_to(current)
        in_force.append((change.effective_on, current))
    return tuple(in_force)


def _check_date(
    change: EmploymentChange,
    previous: date | None,
    employment: Employment,
    year: int,
    path: str,
) -> None:
    """Reject a change date the plan cannot apply.

    Raises:
        InvalidInputError: On the conditions listed in :func:`timeline`.
    """
    day, problem = change.effective_on, None
    if day.year != year:
        problem = f"must fall in the competence year {year}"
    elif previous is not None and (day.year, day.month) <= (
        previous.year,
        previous.month,
    ):
        problem = "must fall in a later month than the previous change"
    else:
        problem = _outside_employment(day, employment)
    if problem is None and day.day != 1:
        problem = _inside_month(change, employment)
    if problem is not None:
        msg = f"employment change on {day.isoformat()} {problem}"
        raise InvalidInputError(msg, field=f"{path}.effective_on", feature=_FEATURE)


def _inside_month(change: EmploymentChange, employment: Employment) -> str | None:
    """Return why ``change`` cannot fall inside a month, if so.

    Returns:
        The reason, or ``None`` for a promotion recorded on the seniority.
    """
    if change.weekly_hours is not None:
        return "of the weekly hours must fall on the first day of a month"
    if change.level_code in {None, employment.level_code}:
        return "inside a month must change the level (a promotion)"
    if employment.seniority is None:
        return "inside a month needs Employment.seniority, which records it"
    return None


def _outside_employment(day: date, employment: Employment) -> str | None:
    """Return why ``day`` cannot start new terms of ``employment``, if so.

    Returns:
        The reason, or ``None`` when the employment can change on ``day``.
    """
    period = employment.employment_period
    if period is None:
        return None
    if day <= period.started_on or (
        period.ended_on is not None and day > period.ended_on
    ):
        return (
            f"must fall after the start ({period.started_on.isoformat()}) and "
            "within the employment period: state the terms of the first day "
            "on the employment"
        )
    return None
