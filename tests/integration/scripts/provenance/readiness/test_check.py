"""Production readiness bound to the outputs the validation matrix covers."""

from __future__ import annotations

from scripts.documentation.validation_matrix.generate import Row
from scripts.provenance.readiness.check import (
    load_baseline,
    missing_outputs,
    readiness_errors,
)
from scripts.provenance.reference_case.check import AXES

_ALL = set(AXES)


def _row(readiness: str, outputs: set[str]) -> Row:
    return Row(readiness=readiness, last_review="—", review_due="—", outputs=outputs)


def test_only_production_ccnls_must_cover_every_output() -> None:
    """A reviewed CCNL misses nothing; a full production CCNL misses nothing."""
    rows = {
        "full": _row("production", _ALL),
        "half": _row("production", {"base_salary", "gross"}),
        "reviewed": _row("reviewed", set()),
    }

    assert missing_outputs(rows) == {"half": frozenset(_ALL - {"base_salary", "gross"})}


def test_a_gap_the_baseline_does_not_list_fails() -> None:
    """A new production CCNL, or a lost output, fails the gate."""
    rows = {"x": _row("production", _ALL - {"net", "tax"})}

    assert readiness_errors(rows, {"x": frozenset({"net"})}) == [
        "agreement/x.json: production without evidence for tax"
    ]


def test_the_baseline_only_shrinks() -> None:
    """An entry naming an output now covered, or a demoted CCNL, is stale."""
    rows = {
        "x": _row("production", _ALL - {"net"}),
        "y": _row("reviewed", set()),
    }
    baseline = {"x": frozenset({"net", "tax"}), "y": frozenset({"net"})}

    stale = "now covered or the CCNL is not production"
    assert readiness_errors(rows, baseline) == [
        f"agreement/x.json: stale entry of baseline.json: tax {stale}",
        f"agreement/y.json: stale entry of baseline.json: net {stale}",
    ]


def test_the_bundle_meets_its_baseline() -> None:
    """Every production CCNL of the bundle covers its outputs or lists them."""
    assert readiness_errors() == []
    assert "metalmeccanico-federmeccanica" not in load_baseline()
