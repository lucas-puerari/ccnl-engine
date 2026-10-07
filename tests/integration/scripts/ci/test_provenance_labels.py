"""Labels that outrun their evidence fail the schema gate, without a baseline."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.knowledge.service.loader_utils import provenance_label_errors
from scripts.ci.payable_rules import PayableRule, inventory
from scripts.ci.provenance_labels import (
    file_label_errors,
    label_errors,
    readiness_errors,
    record_reasons,
    weak_counts,
)

if TYPE_CHECKING:
    from pathlib import Path

_CITED: dict[str, Any] = {
    "source_document": {"document_id": "d", "url": "https://example.org/d.pdf"},
    "section": "Art. 1",
}
_PAYLOADS: list[dict[str, Any]] = [
    {"block": {"provenance": {"status": "derived", "location": _CITED}}},
    {"ruleset": {"source_type": "estimated"}, "x_provenance": {"status": "derived"}},
    {"levels": [{"provenance": {"status": "verified", "location": _CITED}}]},
    {
        "b": {
            "provenance": {"status": "derived", "location": _CITED, "note": "estimate"}
        }
    },
    {"rinnovo": {"source_status": "derived", "source": {"section": "c. 7"}}},
    {"b": {"provenance": {"status": "assumed"}}, "c": "text"},
]


@pytest.mark.parametrize("payload", _PAYLOADS)
def test_gate_and_loader_apply_the_same_rule(payload: dict[str, Any]) -> None:
    """The stdlib gate and the engine loader reject the same records."""
    assert file_label_errors(payload) == provenance_label_errors(payload)


def test_weak_record_has_no_reason() -> None:
    """An assumed or missing record claims no source."""
    assert record_reasons({"status": "assumed"}, estimated=True) == []


def _tree(root: Path, ccnl: dict[str, Any], fiscal: dict[str, Any]) -> Path:
    for group in ("ccnl", "tax", "inps", "surtax"):
        (root / group / "data").mkdir(parents=True)
    (root / "ccnl" / "data" / "x.json").write_text(json.dumps(ccnl), "utf-8")
    (root / "tax" / "data" / "2026-x.json").write_text(json.dumps(fiscal), "utf-8")
    return root


def test_label_errors_name_the_file_of_each_record(tmp_path: Path) -> None:
    """Every data file is scanned, payable rule or not."""
    derived = {"provenance": {"status": "derived", "location": _CITED}}
    root = _tree(
        tmp_path,
        {"apprenticeship": derived},
        {"ruleset": {"source_type": "estimated"}, "tfr": derived},
    )
    estimated = "its ruleset declares source_type 'estimated'"
    assert label_errors(root) == [
        f"tax/data/2026-x.json: tfr.provenance: derived: {estimated}"
    ]


def _ccnl(verification: dict[str, Any]) -> dict[str, Any]:
    return {"meta": {"ccnl_id": "x"}, "verification": verification}


def _weak(file: str = "ccnl/data/x.json") -> PayableRule:
    return PayableRule(file, "accrual_rule", ("base_salary",), "missing")


@pytest.mark.parametrize(
    ("verification", "rules", "expected"),
    [
        ({}, (_weak(),), []),
        ({"readiness": "exploratory"}, (_weak(),), []),
        ({"readiness": "reviewed", "confidence": "verified"}, (), []),
        (
            {"readiness": "reviewed", "confidence": "verified"},
            (_weak(), _weak(), _weak("tax/data/2026-x.json")),
            ["reviewed with 2 assumed or missing payable rule(s)"],
        ),
        (
            {"readiness": "production", "confidence": "high"},
            (),
            ["production without confidence 'verified'"],
        ),
    ],
)
def test_a_cleared_ccnl_needs_verified_confidence_and_no_weak_rule(
    tmp_path: Path,
    verification: dict[str, Any],
    rules: tuple[PayableRule, ...],
    expected: list[str],
) -> None:
    """Only the payable rules of the CCNL file itself count."""
    root = _tree(tmp_path, _ccnl(verification), {})
    assert readiness_errors(rules, root) == [f"ccnl/data/x.json: {e}" for e in expected]


def test_weak_counts_skip_sourced_rules() -> None:
    """Derived rules are not counted; files without a weak rule are left out."""
    rules = (_weak(), PayableRule("ccnl/data/y.json", "r", ("tfr",), "derived"))
    assert weak_counts(rules) == {"ccnl/data/x.json": 1}


def test_bundle_has_no_label_beyond_its_evidence() -> None:
    """No record and no readiness of the bundle claims more than it records."""
    assert label_errors() == []
    assert readiness_errors(inventory()) == []
