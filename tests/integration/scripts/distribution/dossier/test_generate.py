"""The validation dossier of a release: its evidence, for its own commit."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from scripts.distribution.dossier.generate import (
    DossierError,
    build,
    main,
    mutation,
    render,
)
from scripts.quality.mutation.check import RECORD, source_paths

if TYPE_CHECKING:
    from pathlib import Path


def _head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def _record(**changes: object) -> dict[str, Any]:
    record: dict[str, Any] = json.loads(RECORD.read_text(encoding="utf-8"))
    record["commit"] = _head()
    record.update(changes)
    return record


def test_a_campaign_of_another_commit_is_refused() -> None:
    """The score must measure the code the release publishes."""
    with pytest.raises(DossierError, match="not of"):
        mutation(_record(commit="0" * 40), _head())


def test_a_campaign_of_another_perimeter_is_refused() -> None:
    """A record missing a module of the perimeter vouches for less."""
    with pytest.raises(DossierError, match="perimeter"):
        mutation(_record(perimeter=list(source_paths())[1:]), _head())


def test_the_dossier_gathers_every_section() -> None:
    """Identity, gates, mutation, evidence, differences, cases, sign-off."""
    dossier = build({"gates": "success"}, _record(), _head())

    assert dossier["identity"]["commit"] == _head()
    assert len(dossier["identity"]["uv_lock_sha256"]) == 64
    assert dossier["mutation"]["perimeter"] == list(source_paths())
    coverage = dossier["evidence"]["production_coverage"]
    assert coverage["metalmeccanico-federmeccanica"]["base_salary"] == (
        "provider output"
    )
    assert coverage["metalmeccanico-federmeccanica"]["net"] == "hand oracle"
    assert dossier["sign_off"]["human_signed_off"] == []
    assert dossier["gold_cases"]["verified_reference_cases"]
    page = render(dossier)
    assert page.startswith("# Validation dossier")
    assert "| `metalmeccanico-federmeccanica` | provider output |" in page


def test_the_script_writes_both_files_and_fails_on_a_failed_gate(
    tmp_path: Path,
) -> None:
    """Written in any case for the record; exit 1 unless every gate passed."""
    record = tmp_path / "score.json"
    record.write_text(json.dumps(_record()), encoding="utf-8")
    args = ["--mutation", str(record), "--out", str(tmp_path / "out")]

    assert main(["--gate", "gates=success", *args]) == 0
    assert (tmp_path / "out" / "dossier.json").exists()
    assert (tmp_path / "out" / "dossier.md").exists()
    assert main(["--gate", "gates=failure", *args]) == 1
    assert main(["--gate", "gates", *args]) == 1


def test_evidence_of_another_commit_writes_nothing(tmp_path: Path) -> None:
    """A refused campaign leaves no dossier to attach."""
    record = tmp_path / "score.json"
    record.write_text(json.dumps(_record(commit="0" * 40)), encoding="utf-8")

    assert main(["--mutation", str(record), "--out", str(tmp_path / "out")]) == 1
    assert not (tmp_path / "out").exists()
