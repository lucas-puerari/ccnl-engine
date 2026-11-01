"""Validation of a change of the employment and of the timeline of a year."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal

import pytest

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.change.inputs import EmploymentChange, timeline
from ccnl_engine.employment.fact.inputs import WeeklyHours
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import SeniorityPromotion
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

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
        ((date(2026, 3, 15),), "needs Employment.seniority"),
        ((date(2027, 1, 1),), "competence year"),
        ((date(2026, 5, 1), date(2026, 3, 1)), "later month"),
        ((date(2026, 3, 1), date(2026, 3, 20)), "later month"),
        ((date(2026, 11, 1),), "within the employment period"),
    ],
)
def test_a_change_the_plan_cannot_apply_is_rejected(
    days: tuple[date, ...], reason: str
) -> None:
    """Mid-month without seniority, another year, two in a month, after the end."""
    changes = [EmploymentChange(d, level_code=f"{3 - i}") for i, d in enumerate(days)]

    with pytest.raises(InvalidInputError, match=reason):
        timeline(_EMPLOYMENT, changes, 2026, "p")


_SENIOR = replace(_EMPLOYMENT, seniority=new_hire(2025))


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        (
            EmploymentChange(date(2026, 3, 15), weekly_hours=WeeklyHours(Decimal(20))),
            "weekly hours must fall on the first day",
        ),
        (
            EmploymentChange(
                date(2026, 3, 15), level_code="3", weekly_hours=WeeklyHours(Decimal(20))
            ),
            "weekly hours must fall on the first day",
        ),
        (EmploymentChange(date(2026, 3, 15), level_code="4"), "must change the level"),
        (
            EmploymentChange(date(2026, 3, 15), category=WorkerCategory.IMPIEGATO),
            "must change the level",
        ),
    ],
)
def test_only_a_promotion_falls_inside_a_month(
    change: EmploymentChange, reason: str
) -> None:
    """Hours, the same level or a category alone change from the first day."""
    with pytest.raises(InvalidInputError, match=reason):
        timeline(_SENIOR, [change], 2026, "p")


def test_a_promotion_inside_a_month_is_recorded_on_the_seniority() -> None:
    """The level before and the day of the promotion split its month."""
    ((day, employment),) = timeline(
        _SENIOR, [EmploymentChange(date(2026, 3, 16), level_code="3")], 2026, "p"
    )
    assert employment.seniority is not None
    assert (day, employment.level_code, employment.seniority.promotion) == (
        date(2026, 3, 16),
        "3",
        SeniorityPromotion(date(2026, 3, 16), "4"),
    )


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
