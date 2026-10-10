"""The manifest builder derives every entry from the bundle files."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from scripts.knowledge.manifest import build, main

if TYPE_CHECKING:
    from pathlib import Path


def _write(root: Path, path: str, data: object) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data), encoding="utf-8")


def test_entries_follow_the_path_and_the_ruleset(tmp_path: Path) -> None:
    """Dataset, year and scope from the path; identity and validity from the file."""
    _write(
        tmp_path,
        "contract/agreement/x.json",
        {
            "ruleset": {"id": "ccnl/x", "version": "1", "effective_from": "2024-01-01"},
            "verification": {"owner": "someone"},
        },
    )
    _write(tmp_path, "social_security/contribution/2026/industria.json", {})
    _write(tmp_path, "surtax/municipal/2026.json", [])
    _write(tmp_path, "limitation/engine.json", {"limitations": []})

    entries = {e["path"]: e for e in build(tmp_path)["resources"]}

    agreement = entries["contract/agreement/x.json"]
    assert (agreement["dataset"], agreement["year"], agreement["scope"]) == (
        "contract/agreement",
        None,
        "x",
    )
    assert (agreement["ruleset_id"], agreement["owner"]) == ("ccnl/x", "someone")
    assert agreement["valid_from"] == "2024-01-01"
    rates = entries["social_security/contribution/2026/industria.json"]
    assert (rates["year"], rates["scope"], rates["valid_to"]) == (
        2026,
        "industria",
        "2026-12-31",
    )
    assert entries["surtax/municipal/2026.json"]["scope"] is None
    assert "validity_note" in entries["limitation/engine.json"]


def test_a_path_outside_every_dataset_is_rejected(tmp_path: Path) -> None:
    """A resource the manifest cannot classify fails the build."""
    _write(tmp_path, "unknown/thing.json", {})
    with pytest.raises(ValueError, match="no dataset"):
        build(tmp_path)


def test_check_fails_on_drift_and_passes_once_written(tmp_path: Path) -> None:
    """``--check`` compares the committed manifest with the bundle."""
    _write(tmp_path, "policy/italy.json", {})
    assert main(["--check"], root=tmp_path) == 1
    assert main([], root=tmp_path) == 0
    assert main(["--check"], root=tmp_path) == 0
