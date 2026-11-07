"""The months of service counted from an age."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.seniority.age.models import SeniorityAge
from ccnl_engine.seniority.age.rules import _birthday, months_from_age

_RULE = SeniorityAge(age=18, hired_from=date(1986, 6, 1))
_MARCH = date(2026, 3, 1)


def test_a_29_february_turns_the_age_on_1_march() -> None:
    """2008 is a leap year, 2026 is not."""
    assert _birthday(date(2008, 2, 29), 18) == date(2026, 3, 1)


def test_a_29_february_of_a_leap_year_stays() -> None:
    """Born 29 February 2004, twenty on 29 February 2024, a leap year."""
    assert _birthday(date(2004, 2, 29), 20) == date(2024, 2, 29)


def test_another_day_keeps_its_date() -> None:
    """Born 10 May 2003, eighteen on 10 May 2021."""
    assert _birthday(date(2003, 5, 10), 18) == date(2021, 5, 10)


@pytest.mark.parametrize(
    ("rule", "birth", "hired", "months", "expected"),
    [
        (None, date(2003, 5, 10), date(2019, 9, 1), 78, 78),
        (_RULE, None, date(2019, 9, 1), 78, 78),
        (_RULE, date(2003, 5, 10), None, 78, 78),
        (_RULE, date(1970, 5, 10), date(1986, 5, 31), 78, 78),
        (_RULE, date(2000, 1, 1), date(2019, 9, 1), 78, 78),
        (_RULE, date(2003, 5, 10), date(2019, 9, 1), 78, 57),
        (_RULE, date(2008, 5, 10), date(2024, 9, 1), 18, 0),
        (_RULE, date(2008, 3, 1), date(2024, 9, 1), 18, 0),
    ],
)
def test_the_months_count_from_the_birthday_of_the_age(
    rule: SeniorityAge | None,
    birth: date | None,
    hired: date | None,
    months: int,
    expected: int,
) -> None:
    """The rule, the birth and a hire covered by it; then the fewer months."""
    assert months_from_age(months, rule, birth, hired, _MARCH) == expected
