"""The statutory gate fails from 1 December on the next year's assumed data."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from scripts.provenance.rules import PayableRule
from scripts.provenance.statutory import check
from scripts.provenance.statutory.check import DATASETS, gaps, main

if TYPE_CHECKING:
    from pathlib import Path


def _tree(root: Path, year: int) -> None:
    for dataset in DATASETS:
        (root / dataset).mkdir(parents=True)
        (root / dataset / f"{year}.json").write_text("{}", encoding="utf-8")


def test_a_year_without_files_or_with_assumed_rules_has_gaps(tmp_path: Path) -> None:
    """A missing dataset and an assumed rule each name what blocks January."""
    _tree(tmp_path, 2027)
    (tmp_path / "sector" / "2027.json").unlink()
    rules = (
        PayableRule("contribution/2027.json", "inps", ("inps_employee",), "assumed"),
        PayableRule(
            "contribution/2027.json", "apprentice", ("inps_employee",), "verified"
        ),
        PayableRule("contribution/2026.json", "inps", ("inps_employee",), "assumed"),
    )
    assert gaps(2027, rules, tmp_path) == [
        "sector: no file for 2027",
        "contribution/2027.json: 1 assumed or missing rules",
    ]


def test_a_sourced_year_has_no_gap(tmp_path: Path) -> None:
    """Every dataset has its file and no rule is weak."""
    _tree(tmp_path, 2027)
    assert gaps(2027, (), tmp_path) == []


def test_the_gate_waits_for_december() -> None:
    """In November nothing fails; on 1 December the gaps of next year do."""
    with patch.object(check, "gaps", return_value=["sector: no file for 2027"]):
        assert main(["--today", "2026-11-30"]) == 0
        assert main(["--today", "2026-12-01"]) == 1
    with patch.object(check, "gaps", return_value=[]):
        assert main(["--today", "2026-12-15"]) == 0
