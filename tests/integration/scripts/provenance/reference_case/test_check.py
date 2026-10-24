"""The reference cases of each CCNL and the evidence a production CCNL needs."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.provenance.reference_case.check import (
    CaseEvidence,
    index,
    production_errors,
    verified_count_errors,
)
from scripts.provenance.rules import KNOWLEDGE_DIR

_SCRIPT = Path(__file__).parents[5] / "scripts" / "provenance" / "check.py"
_CASE: dict[str, object] = {
    "verification": "source_linked",
    "axes": ["base_salary"],
    "source": {"document": "CCNL", "section": "Art. 1"},
    "inputs": {"ccnl_id": "x"},
    "expected": {"base_salary": "1000.00"},
}


def _cases(root: Path, **cases: dict[str, object]) -> Path:
    """Write the reference cases ``cases`` under ``root``.

    Returns:
        The directory of the cases.
    """
    folder = root / "reference_case"
    folder.mkdir()
    for name, case in cases.items():
        (folder / f"{name}.json").write_text(json.dumps(case), encoding="utf-8")
    return folder


def _knowledge(root: Path, **tiers: str) -> Path:
    """Write one CCNL file per ``tiers`` entry, with that readiness.

    Returns:
        The knowledge directory.
    """
    folder = root / "agreement"
    folder.mkdir(parents=True)
    for ccnl_id, tier in tiers.items():
        payload = {"verification": {"readiness": tier}}
        (folder / f"{ccnl_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    (folder / "untiered.json").write_text("{}", encoding="utf-8")
    return root


def test_the_index_maps_each_ccnl_to_its_valid_cases(tmp_path: Path) -> None:
    """An invalid case, or one with no CCNL, is no evidence."""
    folder = _cases(
        tmp_path,
        a=_CASE,
        b=_CASE | {"axes": []},
        c=_CASE | {"inputs": {}},
        d=_CASE | {"inputs": {"ccnl_id": "y"}},
        e=_CASE
        | {
            "inputs": {"ccnl_id": "y"},
            "axes": [],
            "elements": ["fixed_allowances"],
            "expected": {"fixed_allowances": "200.00"},
        },
    )

    assert index(folder) == {
        "x": (CaseEvidence("a.json", "source_linked", ("base_salary",)),),
        "y": (
            CaseEvidence("d.json", "source_linked", ("base_salary",)),
            CaseEvidence("e.json", "source_linked", (), ("fixed_allowances",)),
        ),
    }


_VERIFIED: dict[str, object] = _CASE | {
    "verification": "verified",
    "source": {
        "kind": "observed_payslip",
        "sha256": "a" * 64,
        "verified_by": "claude-opus-5-5",
        "verified_at": "2026-10-15",
        "independence": "issued by the payroll of the employer",
    },
    "tolerance": "0.00",
}


def test_a_production_ccnl_needs_a_valid_and_a_verified_case(tmp_path: Path) -> None:
    """A source-linked case is evidence, not an independent output.

    No CCNL is exempt: the list of production CCNLs promoted before the
    rule is gone, and a reviewed CCNL needs no case.
    """
    knowledge = _knowledge(tmp_path / "k", x="production", y="production", z="reviewed")
    folder = _cases(tmp_path, a=_CASE, b=_VERIFIED | {"inputs": {"ccnl_id": "z"}})

    assert production_errors(knowledge, folder) == [
        "agreement/x.json: production without a verified reference case",
        "agreement/y.json: production without a valid reference case",
        "agreement/y.json: production without a verified reference case",
    ]


def test_a_verified_case_clears_a_production_ccnl(tmp_path: Path) -> None:
    """A production CCNL with a verified case has what it needs."""
    knowledge = _knowledge(tmp_path / "k", x="production")
    folder = _cases(tmp_path, a=_VERIFIED)

    assert production_errors(knowledge, folder) == []


def test_verified_cases_counts_the_verified_reference_cases(tmp_path: Path) -> None:
    """The field the engine reports as externally compared must hold."""
    knowledge = _knowledge(tmp_path / "k", x="reviewed", y="reviewed")
    folder = _cases(tmp_path, a=_VERIFIED, b=_CASE | {"inputs": {"ccnl_id": "y"}})
    for ccnl_id, count in (("x", 0), ("y", 1)):
        path = knowledge / "agreement" / f"{ccnl_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["verification"]["verified_cases"] = count
        path.write_text(json.dumps(data), encoding="utf-8")

    field = "verification.verified_cases is"
    assert verified_count_errors(knowledge, folder) == [
        f"agreement/x.json: {field} 0, the verified reference cases are 1",
        f"agreement/y.json: {field} 1, the verified reference cases are 0",
    ]


def test_the_bundle_counts_its_verified_cases() -> None:
    """Every CCNL of the bundle records the verified cases it has."""
    assert verified_count_errors(KNOWLEDGE_DIR) == []


def test_the_bundle_binds_each_production_ccnl_to_a_case() -> None:
    """Every production CCNL of the bundle has a valid reference case."""
    assert production_errors(KNOWLEDGE_DIR) == []


def test_the_index_is_printed_from_the_command_line() -> None:
    """``--index`` prints each CCNL with its readiness and cases as JSON."""
    out = subprocess.run(
        [sys.executable, str(_SCRIPT), "--index"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    printed = json.loads(out)

    entry = printed["metalmeccanico-federmeccanica"]
    assert entry["readiness"] == "production"
    assert {
        "file": "metalmeccanico-federmeccanica_c3_2026_observed.json",
        "verification": "verified",
        "axes": ["base_salary"],
        "elements": [],
    } in entry["reference_cases"]
