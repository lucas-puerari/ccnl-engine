"""Validation of a change of the employment and of the timeline of a year."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.change.inputs import EmploymentChange, timeline
from ccnl_engine.employment.fact.inputs import EmploymentPeriod, WeeklyHours
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.errors import InvalidInputError

_EMPLOYMENT = Employment(
    ccnl_id="commercio-confcommercio",
    level_code="4",
    contract_type=Permanent(),
    employment_period=EmploymentPeriod(date(2025, 1, 1), date(2026, 9, 30)),
    weekly_hours=WeeklyHours(Decimal(40)),
    full_time_weekly_hours=WeeklyHours(Decimal(40)),
)


def test_a_change_applies_only_what_it_states() -> None:
    """A level change keeps the hours and the category."""
    changed = EmploymentChange(date(2026, 3, 1), level_code="3").applied_to(_EMPLOYMENT)

    assert (changed.level_code, changed.weekly_hours) == ("3", _EMPLOYMENT.weekly_hours)


def test_a_category_is_parsed() -> None:
    """The string value of a category is accepted."""
    change = EmploymentChange(date(2026, 3, 1), category="quadro")  # type: ignore[arg-type]

    assert change.category is WorkerCategory.QUADRO


@pytest.mark.parametrize(
    "fields",
    [
        {"effective_on": datetime(2026, 3, 1), "level_code": "3"},  # noqa: DTZ001
        {"effective_on": date(2026, 3, 1), "level_code": " "},
        {"effective_on": date(2026, 3, 1), "weekly_hours": 20},
        {"effective_on": date(2026, 3, 1)},
    ],
)
def test_an_invalid_change_is_rejected(fields: dict[str, object]) -> None:
    """A datetime, a blank level, raw hours or nothing to change fail."""
    with pytest.raises(InvalidInputError):
        EmploymentChange(**fields)  # type: ignore[arg-type]


def test_the_timeline_dates_each_employment() -> None:
    """Each change carries the employment after the changes before it."""
    changes = [
        EmploymentChange(date(2026, 3, 1), level_code="3"),
        EmploymentChange(date(2026, 7, 1), weekly_hours=WeeklyHours(Decimal(20))),
    ]

    (first, second) = timeline(_EMPLOYMENT, changes, 2026, "p")

    assert first[0] == date(2026, 3, 1)
    assert (second[1].level_code, second[1].weekly_hours) == (
        "3",
        WeeklyHours(Decimal(20)),
    )


@pytest.mark.parametrize(
    ("days", "reason"),
    [
        ((date(2026, 3, 15),), "first day of a month"),
        ((date(2027, 1, 1),), "competence year"),
        ((date(2026, 5, 1), date(2026, 3, 1)), "later month"),
        ((date(2026, 11, 1),), "within the employment period"),
    ],
)
def test_a_change_the_plan_cannot_apply_is_rejected(
    days: tuple[date, ...], reason: str
) -> None:
    """Mid-month, another year, out of order or after the end."""
    changes = [EmploymentChange(d, level_code="3") for d in days]

    with pytest.raises(InvalidInputError, match=reason):
        timeline(_EMPLOYMENT, changes, 2026, "p")


def test_a_change_on_the_hire_day_is_rejected() -> None:
    """The terms of the first day belong on the employment itself."""
    hired = Employment(
        ccnl_id="commercio-confcommercio",
        level_code="4",
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(date(2026, 3, 1), None),
    )

    with pytest.raises(InvalidInputError, match="after the start"):
        timeline(hired, [EmploymentChange(date(2026, 3, 1), level_code="3")], 2026, "p")


def test_an_employment_without_period_takes_any_month() -> None:
    """No period: any first of a month of the year."""
    untracked = Employment(
        ccnl_id="commercio-confcommercio", level_code="4", contract_type=Permanent()
    )

    assert timeline(
        untracked, [EmploymentChange(date(2026, 2, 1), level_code="3")], 2026, "p"
    )
