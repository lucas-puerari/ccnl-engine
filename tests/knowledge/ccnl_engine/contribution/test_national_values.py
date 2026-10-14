"""Check the INPS values every sector file of a year takes from one circular.

The massimale, the thresholds of the additional 1% IVS and the daily and
hourly minimum base are national: INPS circ. 6/2026 sets them for every
sector.  A sector file that drifts from the others carries a typo or a stale
year.  The ruleset of each file covers its own calendar year, and so does
every extraction window a record of the file declares.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from scripts.provenance.rules import KNOWLEDGE_DIR

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

_CONTRIBUTION = KNOWLEDGE_DIR / "contribution"
_FILES = sorted(_CONTRIBUTION.glob("*/*.json"))
_YEARS = sorted({path.parent.name for path in _FILES})
#: Hours of the full-time week of the hourly minimum, by sector.
_PUBLIC_WEEK = "36"
_PRIVATE_WEEK = "40"


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _national(inps: dict[str, Any]) -> dict[str, object]:
    additional = inps["employee_additional"]
    minimum = inps["minimum_base"]
    return {
        "ceiling": inps["ceiling"],
        "additional_rate": additional["rate"],
        "annual_threshold": additional["annual_threshold"],
        "monthly_threshold": additional["monthly_threshold"],
        "daily_minimum": minimum["daily"],
    }


def _records(node: object) -> Iterator[dict[str, Any]]:
    """Yield every provenance record nested in ``node``.

    Yields:
        Each record, depth first.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key.endswith("provenance") and isinstance(value, dict):
                yield value
            else:
                yield from _records(value)
    elif isinstance(node, list):
        for item in node:
            yield from _records(item)


def test_every_year_has_eight_sectors() -> None:
    """Each year ships the same eight sector files."""
    sectors = {
        year: {p.stem for p in _FILES if p.parent.name == year} for year in _YEARS
    }
    assert _YEARS == ["2026", "2027"]
    assert sectors["2026"] == sectors["2027"]
    assert len(sectors["2026"]) == 8


@pytest.mark.parametrize("year", _YEARS)
def test_national_values_agree_across_sectors(year: str) -> None:
    """Every sector with the standard model reads the same national values."""
    values = {
        path.stem: _national(inps)
        for path in _FILES
        if path.parent.name == year and (inps := _load(path).get("inps")) is not None
    }
    assert len(values) == 7
    assert len({json.dumps(v, sort_keys=True) for v in values.values()}) == 1


@pytest.mark.parametrize("year", _YEARS)
def test_hourly_minimum_follows_the_week_of_the_sector(year: str) -> None:
    """The hourly minimum is the daily one over the full-time week of par. 4."""
    for path in _FILES:
        inps = _load(path).get("inps")
        if path.parent.name != year or inps is None:
            continue
        public = path.stem == "pubblica-amministrazione"
        (hourly,) = inps["minimum_base"]["hourly"]
        assert hourly["full_time_weekly_hours"] == (
            _PUBLIC_WEEK if public else _PRIVATE_WEEK
        ), path.name


@pytest.mark.parametrize("path", _FILES, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_windows_cover_the_year_of_the_file(path: Path) -> None:
    """The ruleset and every extraction window stay inside the file's year."""
    data = _load(path)
    year = path.parent.name
    ruleset = data["ruleset"]
    assert data["year"] == int(year)
    assert data["sector"] == path.stem
    assert ruleset["id"] == f"inps/{year}/{path.stem}"
    assert (ruleset["effective_from"], ruleset["effective_until"]) == (
        f"{year}-01-01",
        f"{year}-12-31",
    )
    for record in _records(data):
        extraction = record.get("extraction") or {}
        start = extraction.get("effective_from")
        end = extraction.get("effective_until")
        assert start is None or start >= f"{year}-01-01", path.name
        assert end is None or end <= f"{year}-12-31", path.name


def test_provisional_year_is_never_verified() -> None:
    """The 2027 files are estimates: no record claims a verified value."""
    for path in _FILES:
        if path.parent.name != "2027":
            continue
        data = _load(path)
        assert data["ruleset"]["source_type"] == "estimated", path.name
        statuses = {record["status"] for record in _records(data)}
        assert statuses <= {"assumed", "missing"}, path.name
