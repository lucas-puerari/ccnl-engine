"""National holidays: fixed days, Easter Monday and the first year a day holds."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.calendar.holiday.models import NationalHolidays, easter_sunday

_PROV = {
    "status": "derived",
    "location": {
        "section": "Art. 2",
        "source_document": {
            "document_id": "legge-260-1949",
            "title": "L. 260/1949",
            "kind": "legge",
        },
    },
}


def _list(*holidays: dict[str, Any]) -> NationalHolidays:
    return NationalHolidays.model_validate({"schema_version": 1, "holidays": holidays})


def _day(day: str, valid_from: str | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {"day": day, "name": day, "provenance": _PROV}
    if valid_from is not None:
        entry["valid_from"] = valid_from
    return entry


@pytest.mark.parametrize(
    ("year", "sunday"),
    [(2024, date(2024, 3, 31)), (2026, date(2026, 4, 5)), (2027, date(2027, 3, 28))],
)
def test_easter_sunday(year: int, sunday: date) -> None:
    """The Gregorian Easter of known years."""
    assert easter_sunday(year) == sunday


def test_a_year_holds_its_fixed_days_and_easter_monday() -> None:
    """A fixed day and the Monday after Easter."""
    holidays = _list(_day("04-25"), _day("easter_monday"))

    assert holidays.in_year(2026) == {date(2026, 4, 25), date(2026, 4, 6)}
    assert holidays.is_holiday(date(2026, 4, 6))
    assert not holidays.is_holiday(date(2026, 4, 7))


def test_a_day_holds_from_its_first_date() -> None:
    """4 October is a holiday from 2026 (L. 151/2025)."""
    holidays = _list(_day("10-04", "2026-01-01"))

    assert holidays.in_year(2025) == frozenset()
    assert holidays.in_year(2026) == {date(2026, 10, 4)}


@pytest.mark.parametrize(
    ("days", "match"),
    [
        ((_day("13-01"),), "neither MM-DD"),
        ((_day("01-01"), _day("01-01")), "list a day twice"),
        ((), "at least 1"),
    ],
)
def test_a_malformed_list_is_rejected(
    days: tuple[dict[str, Any], ...], match: str
) -> None:
    """Days are well formed and unique, and the list is not empty."""
    with pytest.raises(ValidationError, match=match):
        _list(*days)
