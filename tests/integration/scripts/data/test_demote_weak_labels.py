"""Labels are only lowered, to what the record and the ruleset back."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from ccnl_engine.provenance.domain.ruleset_identity import source_hash
from scripts.ci.provenance_labels import file_label_errors
from scripts.data.demote_weak_labels import (
    demote_readiness,
    demote_records,
    main,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

_CITED: dict[str, Any] = {
    "source_document": {"document_id": "d", "url": "https://example.org/d.pdf"},
    "section": "Art. 1",
}


def _derived(**extra: object) -> dict[str, Any]:
    return {"status": "derived", "location": _CITED, **extra}


def test_estimated_ruleset_demotes_its_records_and_keeps_their_location() -> None:
    """The record keeps its citation; the note says why it is assumed."""
    data: dict[str, Any] = {
        "ruleset": {"source_type": "estimated"},
        "inps": {"provenance": _derived(note="Circ. 6/2026.")},
        "tfr": {"provenance": _derived()},
        "levels": [{"provenance": {"status": "assumed"}}],
    }
    assert demote_records(data, estimated=True) == 2
    assert data["inps"]["provenance"] == {
        "status": "assumed",
        "location": _CITED,
        "note": "Circ. 6/2026. Assumed, not derived: its ruleset declares "
        "source_type 'estimated'.",
    }
    assert data["tfr"]["provenance"]["note"].startswith("Assumed, not derived")
    assert file_label_errors(data) == []
    assert demote_records(data, estimated=True) == 0


def test_regime_without_citation_is_demoted() -> None:
    """A regime keeps its source and loses its derived status."""
    data: dict[str, Any] = {
        "rinnovo": {"source_status": "derived", "source": _CITED},
        "notte": {"source_status": "derived", "source": {"section": "c. 10"}},
    }
    assert demote_records(data, estimated=False) == 1
    assert data["rinnovo"]["source_status"] == "derived"
    assert data["notte"] == {"source_status": "assumed", "source": {"section": "c. 10"}}


def test_cleared_readiness_needs_verified_confidence_and_no_weak_rule() -> None:
    """Only a CCNL whose data backs the review keeps its tier."""
    backed = {"verification": {"readiness": "reviewed", "confidence": "verified"}}
    assert not demote_readiness(backed, weak_rules=0)
    assert not demote_readiness({"verification": None}, weak_rules=3)
    assert not demote_readiness({"verification": {}}, weak_rules=3)
    weak = {
        "verification": {
            "readiness": "reviewed",
            "confidence": "verified",
            "human_reviewed_by": "reviewer",
        }
    }
    assert demote_readiness(weak, weak_rules=1)
    assert weak["verification"] == {
        "readiness": "exploratory",
        "confidence": "verified",
        "human_reviewed_by": "reviewer",
    }
    unverified = {"verification": {"readiness": "production", "confidence": "high"}}
    assert demote_readiness(unverified, weak_rules=0)


def _write(path: Path, data: dict[str, Any]) -> None:
    data["ruleset"]["source_hash"] = source_hash(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def test_main_rewrites_and_rehashes_only_what_it_demotes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Records first, then the readiness they no longer back; files rehashed."""
    for group in ("ccnl", "tax", "inps", "surtax"):
        (tmp_path / group / "data").mkdir(parents=True)
    ccnl = tmp_path / "ccnl" / "data" / "x.json"
    _write(
        ccnl,
        {
            "ruleset": {"source_type": "estimated"},
            "verification": {"readiness": "reviewed", "confidence": "verified"},
            "parameters": {"accrual_rule": {"provenance": _derived()}},
        },
    )
    sourced = tmp_path / "tax" / "data" / "2026-x.json"
    _write(sourced, {"ruleset": {"source_type": "official_primary"}})
    untouched = sourced.read_text("utf-8")
    main(tmp_path)
    data = json.loads(ccnl.read_text("utf-8"))
    assert data["parameters"]["accrual_rule"]["provenance"]["status"] == "assumed"
    assert data["verification"]["readiness"] == "exploratory"
    assert data["ruleset"]["source_hash"] == source_hash(data)
    assert sourced.read_text("utf-8") == untouched
    out = capsys.readouterr().out
    assert "Records demoted to assumed: 1" in out
    assert "  ccnl/data/x.json" in out
