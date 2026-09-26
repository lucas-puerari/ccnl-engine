"""The provenance check fails on a payable rule without a provenance record."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.ci.check_provenance import check_rules
from scripts.ci.payable_rules import inventory

if TYPE_CHECKING:
    import pytest

_SCRIPT = Path(__file__).parents[4] / "scripts" / "ci" / "check_provenance.py"
_RECORD: dict[str, object] = {"status": "derived", "location": {"section": "Art. 1"}}


def _knowledge(root: Path, level: dict[str, object]) -> Path:
    """Write a knowledge tree holding one CCNL with ``level``.

    Returns:
        The knowledge directory.
    """
    ccnl_dir = root / "ccnl" / "data"
    ccnl_dir.mkdir(parents=True)
    payload = {"levels": [level], "parameters": {}}
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
    assert "ccnl/data/x.json: levels[A].base_salary[2026-01-01]" in err
    assert "no provenance record" in err


def test_missing_status_passes_but_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A ``missing`` record is allowed and surfaced in the output."""
    assert check_rules(_knowledge(tmp_path, _level({"status": "missing"})))
    out = capsys.readouterr().out
    assert "missing: 1" in out
    assert "missing source: ccnl/data/x.json: levels[A].base_salary" in out


def test_derived_record_passes(tmp_path: Path) -> None:
    """A rule with a located record passes."""
    root = _knowledge(tmp_path, _level(_RECORD))
    assert check_rules(root)
    assert [rule.status for rule in inventory(root)] == ["derived"]


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
