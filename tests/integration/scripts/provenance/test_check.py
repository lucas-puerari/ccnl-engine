"""The schema and evidence gates of the provenance check."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.provenance.check import check_evidence, check_rules, update_baseline
from scripts.provenance.evidence import (
    ENGINE_LIMITATIONS,
    Snapshot,
    load_baseline,
    snapshot,
    write_baseline,
)
from scripts.provenance.rules import inventory

if TYPE_CHECKING:
    import pytest

_SCRIPT = Path(__file__).parents[4] / "scripts" / "provenance" / "check.py"
_RECORD: dict[str, object] = {
    "status": "derived",
    "location": {
        "source_document": {"url": "https://www.cnel.it/ccnl-x.pdf"},
        "section": "Art. 1",
    },
}


def _knowledge(root: Path, level: dict[str, object]) -> Path:
    """Write a knowledge tree holding one CCNL with ``level``.

    Returns:
        The knowledge directory.
    """
    ccnl_dir = root / "contract" / "agreement"
    ccnl_dir.mkdir(parents=True)
    payload = {
        "levels": [level],
        "parameters": {"accrual_rule": {"provenance": _RECORD}},
    }
    (ccnl_dir / "x.json").write_text(json.dumps(payload), encoding="utf-8")
    for group in ("tax", "inps", "surtax"):
        (root / group / "data").mkdir(parents=True)
    return root


def _level(provenance: dict[str, object] | None) -> dict[str, object]:
    return {
        "code": "A",
        "provenance": provenance,
        "base_salary": {"periods": [{"valid_from": "2026-01-01", "value": "1000"}]},
    }


def test_rule_without_provenance_fails_the_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A salary period with no record, own or inherited, fails."""
    assert not check_rules(_knowledge(tmp_path, _level(None)))
    err = capsys.readouterr().err
    assert "contract/agreement/x.json: levels[A].base_salary[2026-01-01]" in err
    assert "no provenance record" in err


def test_missing_status_passes_but_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A ``missing`` record is allowed and surfaced in the output."""
    assert check_rules(_knowledge(tmp_path, _level({"status": "missing"})))
    out = capsys.readouterr().out
    assert "missing: 1" in out
    assert "missing source: contract/agreement/x.json: levels[A].base_salary" in out


def test_derived_record_passes(tmp_path: Path) -> None:
    """A rule with a located record passes."""
    root = _knowledge(tmp_path, _level(_RECORD))
    assert check_rules(root)
    assert [rule.status for rule in inventory(root)] == ["derived", "derived"]


def test_uncited_derived_record_fails_the_schema_gate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A ``derived`` record without a url is labelled stronger than it is."""
    uncited: dict[str, object] = {"status": "derived", "location": {"section": "1"}}
    assert not check_rules(_knowledge(tmp_path, _level(uncited)))
    err = capsys.readouterr().err
    assert (
        "contract/agreement/x.json: levels[0].provenance: derived: no citation "
        "(http(s) url and section or page)"
    ) in err


def test_bundle_passes_in_rules_mode() -> None:
    """The bundled data has a record for every payable rule."""
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--rules"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Payable rules checked:" in result.stdout


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _evidence_tree(root: Path, status: str = "assumed") -> Path:
    """Write a knowledge tree with one rule of ``status`` and no limitation.

    Returns:
        The knowledge directory.
    """
    _knowledge(root, _level({"status": status}))
    (root / "limitation").mkdir(parents=True)
    (root / ENGINE_LIMITATIONS).write_text('{"limitations": []}', encoding="utf-8")
    return root


_EMPTY = Snapshot(weak_rules={}, open_limitations={})


def test_verified_rule_without_evidence_fails_the_schema_gate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A ``verified`` record must name its reviewer, location and hash."""
    assert not check_rules(_knowledge(tmp_path, _level({"status": "verified"})))
    err = capsys.readouterr().err
    assert "record(s) without the evidence they claim" in err
    assert "verified without location.source_document.sha256" in err


def test_evidence_gate_passes_on_the_baseline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A bundle equal to its baseline passes and prints the report."""
    root = _evidence_tree(tmp_path / "k")
    baseline = tmp_path / "baseline.json"
    write_baseline(snapshot(root), baseline)
    assert check_evidence(root, baseline)
    out = capsys.readouterr().out
    assert "Rules per capability" in out
    assert "Weak rules: 1; open limitations: 0" in out


def test_evidence_gate_fails_on_a_new_weak_rule(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An ``assumed`` rule the baseline does not list fails."""
    root = _evidence_tree(tmp_path / "k")
    baseline = tmp_path / "baseline.json"
    write_baseline(_EMPTY, baseline)
    assert not check_evidence(root, baseline)
    err = capsys.readouterr().err
    assert "levels[A].base_salary[2026-01-01]: new assumed rule" in err
    assert "--update-baseline --allow-growth" in err


def test_evidence_gate_fails_on_a_stale_entry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A rule sourced since the baseline must leave it."""
    root = _evidence_tree(tmp_path / "k")
    baseline = tmp_path / "baseline.json"
    write_baseline(snapshot(root), baseline)
    _evidence_tree(tmp_path / "fixed", status="derived")
    assert not check_evidence(tmp_path / "fixed", baseline)
    err = capsys.readouterr().err
    assert "no longer assumed" in err
    assert "Run --update-baseline to shrink the baseline." in err


def test_evidence_gate_fails_without_a_baseline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unreadable baseline is an error, never a pass."""
    root = _evidence_tree(tmp_path / "k")
    assert not check_evidence(root, tmp_path / "absent.json")
    assert "cannot read baseline" in capsys.readouterr().err


def test_update_refuses_growth_unless_allowed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Growing the baseline needs ``--allow-growth``; shrinking does not."""
    root = _evidence_tree(tmp_path / "k")
    baseline = tmp_path / "baseline.json"
    write_baseline(_EMPTY, baseline)
    assert not update_baseline(root, baseline)
    assert "Refusing to grow the baseline" in capsys.readouterr().err
    assert load_baseline(baseline) == _EMPTY
    assert update_baseline(root, baseline, allow_growth=True)
    assert load_baseline(baseline) == snapshot(root)
    fixed = _evidence_tree(tmp_path / "fixed", status="derived")
    assert update_baseline(fixed, baseline)
    assert load_baseline(baseline) == snapshot(fixed)


def test_update_needs_growth_to_create_the_baseline(tmp_path: Path) -> None:
    """Without a baseline every entry is growth."""
    root = _evidence_tree(tmp_path / "k")
    baseline = tmp_path / "baseline.json"
    assert not update_baseline(root, baseline)
    assert not baseline.exists()


def test_bundle_passes_both_gates_from_the_command_line(tmp_path: Path) -> None:
    """Schema and evidence gates pass on the bundle; the baseline rewrites."""
    for mode in ("--schema", "--evidence"):
        result = _run(mode)
        assert result.returncode == 0, result.stderr
    baseline = tmp_path / "baseline.json"
    result = _run("--update-baseline", "--allow-growth", "--baseline", str(baseline))
    assert result.returncode == 0, result.stderr
    assert load_baseline(baseline) == load_baseline(_SCRIPT.with_name("baseline.json"))


def test_allow_growth_requires_update_baseline() -> None:
    """``--allow-growth`` alone is a usage error."""
    result = _run("--evidence", "--allow-growth")
    assert result.returncode == 2
    assert "--allow-growth requires --update-baseline" in result.stderr
