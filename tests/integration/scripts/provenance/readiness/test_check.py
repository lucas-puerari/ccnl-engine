"""Production readiness bound to explicit (ccnl, output, independence) pairs."""

from __future__ import annotations

from scripts.documentation.validation_matrix.generate import Row
from scripts.provenance.readiness.check import (
    load_baseline,
    missing_outputs,
    readiness_errors,
)
from scripts.provenance.reference_case.check import AXES

_ALL = set(AXES)


def _row(readiness: str, outputs: set[str], independence: str = "hand oracle") -> Row:
    row = Row(readiness=readiness, last_review="—", review_due="—")
    row.pin(outputs, independence)
    return row


def _baseline(
    any_: dict[str, frozenset[str]] | None = None,
    provider: dict[str, frozenset[str]] | None = None,
) -> dict[str, dict[str, frozenset[str]]]:
    return {"any": any_ or {}, "provider output": provider or {}}


def test_only_production_ccnls_must_cover_every_output() -> None:
    """A reviewed CCNL misses nothing; a full production CCNL misses nothing."""
    rows = {
        "full": _row("production", _ALL),
        "half": _row("production", {"base_salary", "gross"}),
        "reviewed": _row("reviewed", set()),
    }

    assert missing_outputs(rows) == {"half": frozenset(_ALL - {"base_salary", "gross"})}


def test_components_and_rates_cover_no_output() -> None:
    """A row pinning every component and rate still misses every total."""
    row = _row("production", _ALL - {"gross", "employee_contributions"})
    labels = ["fixed_allowances", "employee_inps_rate", "contribution_base"]
    row.pin(labels, "provider output")

    assert missing_outputs({"x": row}) == {
        "x": frozenset({"gross", "employee_contributions"})
    }


def test_a_hand_oracle_never_covers_an_output_independently() -> None:
    """A provider output on the base salary, hand oracles on the rest.

    Every output has evidence, but only the base salary is independent:
    the union of the two sets would call the net independently covered.
    """
    row = _row("production", _ALL)
    row.pin(["base_salary"], "provider output")

    assert missing_outputs({"x": row}) == {}
    assert missing_outputs({"x": row}, "provider output") == {
        "x": frozenset(_ALL - {"base_salary"})
    }


def test_a_rate_does_not_cover_the_contributions_independently() -> None:
    """An INPS rate from a payslip leaves the contribution totals uncovered."""
    row = _row("production", {"net"}, "provider output")
    row.pin(["employee_inps_rate"], "provider output")

    gaps = missing_outputs({"x": row}, "provider output")["x"]
    assert {"employee_contributions", "employer_contributions"} <= gaps
    assert "net" not in gaps


def test_a_gap_the_baseline_does_not_list_fails() -> None:
    """A new production CCNL, or a lost output, fails the gate at each level."""
    rows = {"x": _row("production", _ALL - {"net", "tax"})}
    baseline = _baseline({"x": frozenset({"net"})}, {"x": frozenset(_ALL - {"gross"})})

    assert readiness_errors(rows, baseline) == [
        "agreement/x.json: production without evidence for tax",
        "agreement/x.json: production without provider output evidence for gross",
    ]


def test_the_baseline_only_shrinks() -> None:
    """An entry naming an output now covered, or a demoted CCNL, is stale."""
    rows = {
        "x": _row("production", _ALL - {"net"}),
        "y": _row("reviewed", set()),
        "z": _row("production", _ALL, "provider output"),
    }
    baseline = _baseline(
        {"x": frozenset({"net", "tax"}), "y": frozenset({"net"})},
        {"x": frozenset(_ALL), "z": frozenset({"tfr"})},
    )

    stale = "now covered or the CCNL is not production"
    entry = "entry of baseline.json"
    assert readiness_errors(rows, baseline) == [
        f"agreement/x.json: stale 'any' {entry}: tax {stale}",
        f"agreement/y.json: stale 'any' {entry}: net {stale}",
        f"agreement/z.json: stale 'provider output' {entry}: tfr {stale}",
    ]


def test_the_bundle_meets_its_baseline() -> None:
    """Every production CCNL of the bundle covers its outputs or lists them."""
    assert readiness_errors() == []
    assert "metalmeccanico-federmeccanica" not in load_baseline()["any"]
    assert "net" in load_baseline()["provider output"]["metalmeccanico-federmeccanica"]
