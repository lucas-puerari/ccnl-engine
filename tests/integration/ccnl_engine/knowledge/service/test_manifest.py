"""The knowledge manifest indexes every resource of the bundle once."""

from __future__ import annotations

import importlib.resources
import json
import operator
from pathlib import Path

import pytest

from ccnl_engine.knowledge.service.manifest import (
    MANIFEST,
    read_resource,
    resource_dir,
    resources,
)

_KNOWLEDGE = Path(str(importlib.resources.files("ccnl_engine.knowledge")))
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


@pytest.mark.parametrize("entry", _ENTRIES, ids=operator.itemgetter("path"))
def test_the_path_states_the_dataset_year_and_scope(entry: dict[str, object]) -> None:
    """``domain/dataset/year/scope.json``: no dimension repeated or hidden."""
    path = str(entry["path"])
    expected = "/".join(
        str(part)
        for part in (entry["dataset"], entry["year"], entry["scope"])
        if part is not None
    )
    assert path == f"{expected}.json"
    assert entry["dataset_id"] == expected
    assert entry["wheel_resource"] == f"{path}.gz"
    assert entry["valid_from"] is not None or entry.get("validity_note")


def test_a_dataset_lists_its_resources_in_path_order() -> None:
    """The loaders find every resource of a dataset through the manifest."""
    agreements = resources("contract/agreement")
    assert len(agreements) == 126
    assert [r.path for r in agreements] == sorted(r.path for r in agreements)
    assert agreements[0].name == agreements[0].path.rsplit("/", 1)[-1]
    years = {r.year for r in resources("taxation/annual")}
    assert years == {2026, 2027}


def test_a_listed_resource_reads_from_its_directory() -> None:
    """The text of a listed resource is the file the path names."""
    path = "policy/italy.json"
    assert json.loads(read_resource(path)) == json.loads(
        (_KNOWLEDGE / path).read_text("utf-8")
    )
    assert resource_dir(path).name == "policy"


def test_an_unlisted_path_is_not_read() -> None:
    """A file the manifest does not list is never read, even if present."""
    with pytest.raises(FileNotFoundError, match="lists no resource"):
        read_resource("contract/agreement/../../manifest.json")
