"""The national holidays are read from the bundle."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.calendar.holiday import loaders
from ccnl_engine.errors import DataIntegrityError

if TYPE_CHECKING:
    from collections.abc import Iterator


def test_the_bundled_holidays_of_2026() -> None:
    """L. 260/1949 as amended: twelve days in 2026, 4 October included."""
    days = loaders.load_national_holidays().in_year(2026)

    assert sorted(days) == [
        date(2026, 1, 1),
        date(2026, 1, 6),
        date(2026, 4, 6),
        date(2026, 4, 25),
        date(2026, 5, 1),
        date(2026, 6, 2),
        date(2026, 8, 15),
        date(2026, 10, 4),
        date(2026, 11, 1),
        date(2026, 12, 8),
        date(2026, 12, 25),
        date(2026, 12, 26),
    ]


def test_the_holidays_between_two_days_across_a_new_year() -> None:
    """Christmas to Epiphany: 25 and 26 December, 1 and 6 January."""
    days = loaders.load_national_holidays().between(
        date(2026, 12, 20), date(2027, 1, 6)
    )

    assert sorted(days) == [
        date(2026, 12, 25),
        date(2026, 12, 26),
        date(2027, 1, 1),
        date(2027, 1, 6),
    ]


@pytest.fixture
def _fresh_cache() -> Iterator[None]:
    loaders.load_national_holidays.cache_clear()
    yield
    loaders.load_national_holidays.cache_clear()


@pytest.mark.usefixtures("_fresh_cache")
def test_a_malformed_list_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A file that is not a valid list is a data integrity error."""
    monkeypatch.setattr(loaders, "read_resource", lambda _path: "{}")

    with pytest.raises(DataIntegrityError, match="not a valid list"):
        loaders.load_national_holidays()
