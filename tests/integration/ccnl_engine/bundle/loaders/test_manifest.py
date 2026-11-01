"""The knowledge manifest indexes every resource of the bundle once."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ccnl_engine.bundle.loaders import (
    MANIFEST,
    read_resource,
    resource_dir,
    resources,
)

_KNOWLEDGE = Path(__file__).parents[5] / "src" / "ccnl_engine" / "knowledge"
_ENTRIES = json.loads((_KNOWLEDGE / MANIFEST).read_text("utf-8"))["resources"]


def test_every_json_file_is_listed_once_and_exists() -> None:
    """The manifest and the bundle hold the same files, each once."""
    on_disk = {
        p.relative_to(_KNOWLEDGE).as_posix()
        for p in _KNOWLEDGE.rglob("*.json")
        if p.name != MANIFEST
    }
    listed = [entry["path"] for entry in _ENTRIES]
    assert len(listed) == len(set(listed))
    assert set(listed) == on_disk
    ids = [entry["dataset_id"] for entry in _ENTRIES]
    assert len(ids) == len(set(ids))


def _integrity_gaps(entry: dict[str, object]) -> list[str]:
    """Return what an entry lacks.

    Returns:
        The names of the missing hash or notes of absent metadata.
    """
    has_ruleset = all(
        entry[field] is not None
        for field in ("ruleset_id", "ruleset_version", "source_type")
    )
    checks = {
        "source_hash": len(str(entry["source_hash"])) == 64,
        "schema_note": entry["schema_version"] is not None
        or bool(entry.get("schema_note")),
        "ruleset_note": has_ruleset or bool(entry.get("ruleset_note")),
        "source_note": entry["source_type"] is not None
        or bool(entry.get("source_note")),
        "validity_note": entry["valid_from"] is not None
        or bool(entry.get("validity_note")),
    }
    return [name for name, ok in checks.items() if not ok]


def test_every_entry_has_integrity_and_explains_optional_metadata() -> None:
    """Every resource has a hash; absent metadata is explicitly explained."""
    wrong = {e["path"]: gaps for e in _ENTRIES if (gaps := _integrity_gaps(e))}
    assert wrong == {}


def test_the_path_states_the_dataset_year_and_scope() -> None:
    """``domain/dataset/year/scope.json``: no dimension repeated or hidden."""
    wrong = []
    for entry in _ENTRIES:
        path = str(entry["path"])
        expected = "/".join(
            str(part)
            for part in (entry["dataset"], entry["year"], entry["scope"])
            if part is not None
        )
        if (path, entry["dataset_id"], entry["wheel_resource"]) != (
            f"{expected}.json",
            expected,
            f"{path}.gz",
        ):
            wrong.append(path)
    assert wrong == []


def test_a_dataset_lists_its_resources_in_path_order() -> None:
    """The loaders find every resource of a dataset through the manifest."""
    agreements = resources("agreement")
    assert len(agreements) == 134
    assert [r.path for r in agreements] == sorted(r.path for r in agreements)
    assert agreements[0].name == agreements[0].path.rsplit("/", 1)[-1]
    years = {r.year for r in resources("sector")}
    assert years == {2026, 2027}


def test_a_listed_resource_reads_from_its_directory() -> None:
    """The text of a listed resource is the file the path names."""
    path = "pay_item/italy.json"
    assert json.loads(read_resource(path)) == json.loads(
        (_KNOWLEDGE / path).read_text("utf-8")
    )
    assert resource_dir(path).name == "pay_item"


def test_an_unlisted_path_is_not_read() -> None:
    """A file the manifest does not list is never read, even if present."""
    with pytest.raises(FileNotFoundError, match="lists no resource"):
        read_resource("agreement/../../manifest.json")
