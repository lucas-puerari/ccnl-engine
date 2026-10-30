"""Check that each year file of the bundle covers exactly its calendar year.

A ruleset left open-ended overlaps the file of the next year, so which one
governs a date would depend on the loader rather than on the data.  Every
file keyed by a year declares the first and last day of that year, and its
ruleset id names the year.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

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
        "irpef",
        "sector",
        "severance",
        "surtax",
        "tax_credit",
        "variable_pay",
    }


def _covers_its_year(path: Path) -> bool:
    year = _year_of(path)
    ruleset = json.loads(path.read_text(encoding="utf-8"))["ruleset"]
    window = (ruleset["effective_from"], ruleset["effective_until"])
    return window == (f"{year}-01-01", f"{year}-12-31") and year in ruleset["id"]


def test_ruleset_covers_exactly_its_year() -> None:
    """Each yearly ruleset runs from 1 January to 31 December of its year."""
    wrong = [
        str(path.relative_to(KNOWLEDGE_DIR))
        for path in _YEAR_FILES
        if not _covers_its_year(path)
    ]
    assert wrong == []
