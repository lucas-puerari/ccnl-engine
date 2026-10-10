"""The evidence requirements and the shrink-only ratchet of the bundle."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.identity.facade import CCNLVerification
from ccnl_engine.knowledge.limitation.loaders import load_engine_limitations
from ccnl_engine.knowledge.limitation.models import LimitationStatus
from ccnl_engine.provenance.source.models_chain import RuleProvenance
from scripts.documentation.coverage import bundled_ccnls
from scripts.provenance.evidence import (
    ENGINE_LIMITATIONS,
    Snapshot,
    compare,
    load_baseline,
    open_limitations,
    report_lines,
    schema_errors,
    snapshot,
    write_baseline,
)
from scripts.provenance.rules import PayableRule, inventory

if TYPE_CHECKING:
    from pathlib import Path

_DIGEST = "0" * 64
_VERIFIED: dict[str, object] = {
    "status": "verified",
    "location": {
        "source_document": {
            "document_id": "ccnl-x",
            "title": "CCNL X",
            "kind": "cnel",
            "sha256": _DIGEST,
        },
        "page": "12",
        "section": "Art. 7",
    },
    "extraction": {
        "method": "manual",
        "extraction_timestamp": "2026-09-01T00:00:00",
        "verified_by": "reviewer",
        "verified_at": "2026-09-02T00:00:00",
        "effective_from": "2026-01-01",
    },
}
_PRODUCTION: dict[str, object] = {
    "confidence": "verified",
    "readiness": "production",
    "owner": "owner",
    "human_reviewed_by": "reviewer",
    "last_reviewed": "2026-09-02",
    "review_due": "2027-03-02",
}


def _note(variant: str, **extra: object) -> dict[str, object]:
    return {
        "kind": "simplification",
        "text": variant,
        "capability": "base_salary",
        "monetary_impact": "yes",
        "limitation": {"variant": variant, **extra},
    }


def _ccnl(**extra: object) -> dict[str, object]:
    return {
        "meta": {"ccnl_id": "x"},
        "ruleset": {"id": "ccnl/x"},
        "levels": [
            {
                "code": "A",
                "provenance": {"status": "assumed"},
                "base_salary": {"periods": [{"valid_from": "2026-01-01", "value": 1}]},
            }
        ],
        "parameters": {},
        **extra,
    }


def _knowledge(root: Path, ccnl: dict[str, object]) -> Path:
    """Write a knowledge tree with one CCNL and two engine limitations.

    Returns:
        The knowledge directory.
    """
    for group in (
        "contract/agreement",
        "taxation/annual",
        "social_security/contribution",
        "surtax/regional",
        "limitation",
    ):
        (root / group).mkdir(parents=True)
    (root / "contract" / "agreement" / "x.json").write_text(json.dumps(ccnl), "utf-8")
    engine = {
        "limitations": [
            {"id": "engine_open"},
            {"id": "engine_resolved", "status": "resolved"},
        ]
    }
    (root / ENGINE_LIMITATIONS).write_text(json.dumps(engine), "utf-8")
    return root


def test_snapshot_lists_weak_rules_and_limitations(tmp_path: Path) -> None:
    """Weak rules and open limitations are recorded."""
    notes = [
        _note("open_one"),
        _note("closed", status="resolved"),
        {"kind": "info", "text": "no limitation"},
        {**_note("no_capability"), "capability": None},
    ]
    root = _knowledge(tmp_path, _ccnl(coverage={"notes": notes}))
    found = snapshot(root)
    assert found.weak_rules == {
        "contract/agreement/x.json": {
            "levels[A].base_salary[2026-01-01]": "assumed",
            "accrual_rule": "missing",
        }
    }
    assert found.open_limitations == {
        ENGINE_LIMITATIONS: ("engine_open",),
        "contract/agreement/x.json": ("x/open_one",),
    }


def test_tree_without_weak_evidence_has_an_empty_snapshot(tmp_path: Path) -> None:
    """No open limitation: nothing is listed."""
    root = _knowledge(tmp_path, _ccnl())
    (root / ENGINE_LIMITATIONS).write_text('{"limitations": null}', "utf-8")
    assert open_limitations(root) == {}


_BASE = Snapshot(
    weak_rules={"f.json": {"a": "assumed", "b": "missing", "c": "assumed"}},
    open_limitations={"f.json": ("f/one",)},
)


def test_matching_snapshot_passes() -> None:
    """The bundle equal to its baseline neither grows nor goes stale."""
    ratchet = compare(_BASE, _BASE)
    assert ratchet.ok
    assert (ratchet.grown, ratchet.stale) == ((), ())


def test_new_or_weaker_entries_are_growth() -> None:
    """A new weak rule, a weaker rule or a new limitation all grow."""
    current = Snapshot(
        weak_rules={
            "f.json": {"a": "missing", "b": "missing", "c": "assumed"},
            "g.json": {"z": "assumed"},
        },
        open_limitations={"f.json": ("f/one", "f/two")},
    )
    ratchet = compare(current, _BASE)
    assert ratchet.grown == (
        "f.json: a: assumed became missing",
        "g.json: z: new assumed rule",
        "f.json: new open limitation f/two",
    )
    assert ratchet.stale == ()
    assert not ratchet.ok


def test_improved_entries_are_stale() -> None:
    """A stronger, fixed or removed entry must leave the baseline."""
    current = Snapshot(
        weak_rules={"f.json": {"a": "assumed", "b": "assumed"}},
        open_limitations={},
    )
    ratchet = compare(current, _BASE)
    assert ratchet.grown == ()
    assert ratchet.stale == (
        "f.json: b: missing is now assumed",
        "f.json: c: no longer assumed",
        "f.json: open limitation f/one no longer open",
    )
    assert not ratchet.ok


def test_baseline_round_trips(tmp_path: Path) -> None:
    """A written baseline reads back to the same snapshot, keys sorted."""
    path = tmp_path / "baseline.json"
    write_baseline(_BASE, path)
    assert load_baseline(path) == _BASE
    assert list(json.loads(path.read_text("utf-8"))["weak_rules"]["f.json"]) == [
        "a",
        "b",
        "c",
    ]


@pytest.mark.parametrize(
    ("document", "error", "fragment"),
    [
        ([], TypeError, "baseline must be a JSON object"),
        ({"weak_rules": []}, TypeError, "weak_rules must be"),
        ({"weak_rules": {"f": []}}, TypeError, r"weak_rules\[f\] must be"),
        ({"weak_rules": {"f": {"a": "derived"}}}, ValueError, "status other"),
        (
            {"weak_rules": {}, "open_limitations": {"f": [1]}},
            TypeError,
            r"open_limitations\[f\] must be a list",
        ),
    ],
)
def test_malformed_baseline_is_rejected(
    document: object, error: type[Exception], fragment: str
) -> None:
    """Every part of the baseline is checked for its shape."""
    with pytest.raises(error, match=fragment):
        Snapshot.from_json(document)


def test_baseline_with_invalid_json_is_rejected(tmp_path: Path) -> None:
    """A baseline that is not JSON names the file."""
    path = tmp_path / "baseline.json"
    path.write_text("{", "utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_baseline(path)


def _verified_rule(record: dict[str, object]) -> PayableRule:
    return PayableRule("f.json", "rule", ("base_salary",), "verified", record)


def test_verified_rule_with_full_evidence_passes(tmp_path: Path) -> None:
    """The gate accepts it and so does the engine model."""
    root = _knowledge(tmp_path, _ccnl())
    assert schema_errors((_verified_rule(_VERIFIED),), root) == []
    assert RuleProvenance.model_validate(_VERIFIED).location is not None


def test_verified_rule_without_evidence_lists_each_gap(tmp_path: Path) -> None:
    """Reviewer, review date, exact location and document hash are required."""
    root = _knowledge(tmp_path, _ccnl())
    rule = PayableRule("f.json", "rule", ("base_salary",), "verified")
    assert schema_errors((rule,), root) == [
        "f.json: rule: verified without extraction.verified_by",
        "f.json: rule: verified without extraction.verified_at",
        "f.json: rule: verified without an exact location (location.page or section)",
        "f.json: rule: verified without location.source_document.sha256",
    ]


def test_production_ccnl_with_full_evidence_passes(tmp_path: Path) -> None:
    """Owner, reviewer and review dates are present; the model accepts them."""
    root = _knowledge(tmp_path, _ccnl(verification=_PRODUCTION))
    assert schema_errors((), root) == []
    assert CCNLVerification.model_validate(_PRODUCTION).owner == "owner"


@pytest.mark.parametrize(
    ("verification", "expected"),
    [
        (
            {"readiness": "production"},
            [
                "production without verification.owner",
                "production without verification.human_reviewed_by",
                "production without verification.last_reviewed",
                "production without confidence 'verified'",
                "production without a valid verification.review_due",
            ],
        ),
        (
            {**_PRODUCTION, "review_due": "2026-09-02"},
            ["verification.review_due is not after last_reviewed"],
        ),
        (
            {**_PRODUCTION, "review_due": "soon"},
            ["production without a valid verification.review_due"],
        ),
        (
            {**_PRODUCTION, "last_reviewed": 20260902},
            [],
        ),
    ],
)
def test_production_ccnl_without_evidence_fails(
    tmp_path: Path, verification: dict[str, object], expected: list[str]
) -> None:
    """Each missing or inconsistent field of a production CCNL is listed."""
    root = _knowledge(tmp_path, _ccnl(verification=verification))
    assert schema_errors((), root) == [
        f"contract/agreement/x.json: {e}" for e in expected
    ]


def test_ccnl_ruleset_id_carries_the_ccnl_prefix(tmp_path: Path) -> None:
    """A CCNL ruleset id is ``ccnl/<ccnl_id>``."""
    root = _knowledge(tmp_path, _ccnl(ruleset={"id": "x"}))
    assert schema_errors((), root) == [
        "contract/agreement/x.json: ruleset.id 'x' is not 'ccnl/x'"
    ]


def test_report_ranks_ccnl_files_by_weak_rules() -> None:
    """Capabilities are listed by name, CCNL files weakest first."""
    rules = (
        PayableRule("contract/agreement/a.json", "r1", ("seniority",), "assumed"),
        PayableRule("contract/agreement/b.json", "r1", ("base_salary",), "missing"),
        PayableRule("contract/agreement/b.json", "r2", ("base_salary",), "assumed"),
        PayableRule("contract/agreement/c.json", "r1", ("base_salary",), "derived"),
        PayableRule("taxation/annual/2026/t.json", "r1", ("irpef",), "assumed"),
    )
    assert report_lines(rules, top=1) == [
        "Rules per capability (verified / derived / assumed / missing):",
        "  base_salary: 0 / 1 / 1 / 1",
        "  irpef: 0 / 0 / 1 / 0",
        "  seniority: 0 / 0 / 1 / 0",
        "CCNL files with weak rules: 2; top 1:",
        "  contract/agreement/b.json: 0 / 0 / 1 / 1",
    ]


def test_bundle_matches_the_committed_baseline() -> None:
    """The committed baseline lists exactly the weak evidence of the bundle."""
    ratchet = compare(snapshot(), load_baseline())
    assert ratchet.grown == ()
    assert ratchet.stale == ()


def test_bundle_meets_the_evidence_its_records_claim() -> None:
    """No verified rule or production CCNL lacks its evidence."""
    assert schema_errors(inventory()) == []


def test_stdlib_reading_matches_the_engine_models() -> None:
    """Open limitations agree with the loaded models."""
    ccnls = bundled_ccnls()
    engine_open = {
        lim.id
        for lim in (
            *load_engine_limitations(),
            *(item for c in ccnls for item in c.limitations),
        )
        if lim.status is LimitationStatus.OPEN
    }
    found = snapshot()
    assert {i for ids in found.open_limitations.values() for i in ids} == engine_open
