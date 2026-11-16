"""The rule of the minimum INPS base: daily and hourly minimum, day counts."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.contribution.minimum_base.models import MinimumBaseRule
from ccnl_engine.employment.category.models import WorkerCategory

#: Circ. INPS 6/2026 par. 1 (58.13 a day) and par. 4 (58.13 x 6/40 = 8.72).
_RULE = {
    "daily": "58.13",
    "week_days": 6,
    "monthly_days": 26,
    "hourly": [{"full_time_weekly_hours": "40", "amount": "8.72"}],
}


def test_holds_the_amounts_as_published() -> None:
    """The daily minimum and the hourly one of a 40-hour week, as printed."""
    rule = MinimumBaseRule.model_validate(_RULE)

    assert (rule.daily, rule.week_days, rule.monthly_days) == (Decimal("58.13"), 6, 26)
    assert rule.hourly_for(Decimal(40)) == Decimal("8.72")


def test_has_no_hourly_minimum_for_an_unpublished_week() -> None:
    """INPS publishes no hourly minimum of a 38-hour week."""
    assert MinimumBaseRule.model_validate(_RULE).hourly_for(Decimal(38)) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("daily", "0"),
        ("week_days", 7),
        ("monthly_days", 23),
        ("monthly_days", 31),
        (
            "hourly",
            [
                {"full_time_weekly_hours": "40", "amount": "8.72"},
                {"full_time_weekly_hours": "40", "amount": "8.73"},
            ],
        ),
    ],
)
def test_rejects_an_impossible_rule(field: str, value: object) -> None:
    """A zero minimum, a seven-day week, a bad month, a repeated week.

    A month holds four to five normal weeks; one hourly minimum per week.
    """
    with pytest.raises(ValidationError):
        MinimumBaseRule.model_validate(_RULE | {field: value})


def test_accepts_a_sector_without_a_monthly_day_count() -> None:
    """The Gestione pubblica: 36 hours on five days, no sourced month."""
    rule = MinimumBaseRule.model_validate({
        "daily": "58.13",
        "week_days": 5,
        "monthly_days": None,
        "hourly": [{"full_time_weekly_hours": "36", "amount": "8.07"}],
    })

    assert rule.monthly_days is None
    assert rule.hourly_for(Decimal(36)) == Decimal("8.07")


#: Tabella A of circ. 6/2026 allegato 1, Agricoltura: dirigente 128.65,
#: impiegato 67.84, operaio 51.70; circ. 43/2026 par. 5: the part time of
#: the operai takes 58.13 x 6/39 = 8.94.
_AGRICULTURE = _RULE | {
    "daily_by_category": {
        "dirigente": "128.65",
        "impiegato": "67.84",
        "operaio": "51.70",
    },
    "hourly_categories": ["operaio"],
}


def test_category_minimum_overrides_the_daily_minimum() -> None:
    """A qualifica of Tabella A takes its own amount; the others 58.13."""
    rule = MinimumBaseRule.model_validate(_AGRICULTURE)

    assert rule.daily_for(WorkerCategory.IMPIEGATO) == Decimal("67.84")
    assert rule.daily_for(WorkerCategory.DIRIGENTE) == Decimal("128.65")
    assert rule.daily_for(WorkerCategory.OPERAIO) == Decimal("51.70")
    assert rule.daily_for(WorkerCategory.QUADRO) == Decimal("58.13")
    assert rule.daily_for(None) == Decimal("58.13")


def test_published_hourly_minimum_is_of_the_general_minimum() -> None:
    """8.72 is 58.13 x 6/40: a qualifica of its own takes it only when listed."""
    rule = MinimumBaseRule.model_validate(_AGRICULTURE)

    assert rule.publishes_hourly_for(None)
    assert rule.publishes_hourly_for(WorkerCategory.QUADRO)
    assert rule.publishes_hourly_for(WorkerCategory.OPERAIO)
    assert not rule.publishes_hourly_for(WorkerCategory.IMPIEGATO)


@pytest.mark.parametrize(
    ("by_category", "lowers"),
    [
        ({"dirigente": "160.77"}, False),
        ({"dirigente": "128.65", "operaio": "51.70"}, True),
        ({}, False),
    ],
    ids=["industria", "agricoltura", "none"],
)
def test_a_lower_category_minimum_needs_the_category(
    by_category: dict[str, str], lowers: bool
) -> None:
    """Only a category below 58.13 makes the general minimum overstate."""
    rule = MinimumBaseRule.model_validate(_RULE | {"daily_by_category": by_category})

    assert rule.lowers_by_category is lowers


def test_rejects_an_hourly_category_without_a_minimum() -> None:
    """An hourly category is one with a daily minimum of its own."""
    with pytest.raises(ValidationError, match="hourly categories need"):
        MinimumBaseRule.model_validate(_RULE | {"hourly_categories": ["operaio"]})
