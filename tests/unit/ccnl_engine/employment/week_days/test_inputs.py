"""The working days of the full-time week, five or six."""

from __future__ import annotations

import pytest

from ccnl_engine.employment.inputs import Employment
from ccnl_engine.employment.week_days.inputs import check_week_days
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import Permanent


@pytest.mark.parametrize("value", [None, 5, 6])
def test_five_six_or_none_is_accepted(value: int | None) -> None:
    """The weeks a CCNL sets a daily divisor for."""
    assert check_week_days(value) == value


@pytest.mark.parametrize("value", [4, 7, 0, True, "5", 5.0])
def test_any_other_value_is_rejected(value: object) -> None:
    """Neither another number of days nor another type."""
    with pytest.raises(InvalidInputError, match="5 or 6") as error:
        check_week_days(value)
    assert error.value.field == "Employment.full_time_week_days"


def test_the_employment_checks_the_week() -> None:
    """``Employment`` rejects a seven-day week and keeps a six-day one."""
    with pytest.raises(InvalidInputError, match="full_time_week_days"):
        Employment(
            "pulizia-artigianato-confartigianato",
            "3",
            Permanent(),
            full_time_week_days=7,
        )

    employment = Employment(
        "pulizia-artigianato-confartigianato", "3", Permanent(), full_time_week_days=6
    )
    assert employment.full_time_week_days == 6
