"""Check that each year file of the bundle covers exactly its calendar year.

A ruleset left open-ended overlaps the file of the next year, so which one
governs a date would depend on the loader rather than on the data.  Every
file keyed by a year declares the first and last day of that year, and its
ruleset id names the year.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from scripts.provenance.rules import KNOWLEDGE_DIR

if TYPE_CHECKING:
    from pathlib import Path

#: Year files that carry a ruleset: every one but the capability registries.
_YEAR_FILES = sorted(
    path
    for path in {
        *KNOWLEDGE_DIR.glob("*/20[0-9][0-9]/*.json"),
        *KNOWLEDGE_DIR.glob("**/20[0-9][0-9].json"),
    }
    if "ruleset" in json.loads(path.read_text(encoding="utf-8"))
)


def _year_of(path: Path) -> str:
    return path.stem if path.stem.isdigit() else path.parent.name


def test_every_kind_of_year_file_is_checked() -> None:
    """The glob finds the year files of every dataset."""
    datasets = {path.relative_to(KNOWLEDGE_DIR).parts[0] for path in _YEAR_FILES}

    assert datasets == {
        "contribution",
        "family",
        "sector",
        "severance",
        "surtax",
        "tax_credit",
        "variable_pay",
    }


@pytest.mark.parametrize(
    "path", _YEAR_FILES, ids=lambda p: str(p.relative_to(KNOWLEDGE_DIR))
)
def test_ruleset_covers_exactly_its_year(path: Path) -> None:
    """The ruleset runs from 1 January to 31 December of the file's year."""
    year = _year_of(path)
    ruleset = json.loads(path.read_text(encoding="utf-8"))["ruleset"]

    assert (ruleset["effective_from"], ruleset["effective_until"]) == (
        f"{year}-01-01",
        f"{year}-12-31",
    )
    assert year in ruleset["id"]
