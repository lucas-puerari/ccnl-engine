"""The rule of the minimum INPS base: daily and hourly minimum, day counts."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.tax.contribution.models_minimum_base import MinimumBaseRule

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
