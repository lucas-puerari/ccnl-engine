"""Regenerate docs/trust/validation-matrix.md: what validates each CCNL.

The raw count of tests says little about how far a CCNL is validated.  This
page crosses, for each CCNL that is ``reviewed`` or ``production`` or that
any evidence runs, the evidence the repository holds:

- reference cases (``tests/knowledge/ccnl_engine/period/reference_case/``):
  the primary source they cite, or the independent output they were
  checked against, and the totals, components and rates they pin;
- observed payslips replayed through the engine
  (``tests/knowledge/ccnl_engine/period/observed_payslip/``, ``replay``),
  only those valid under :mod:`scripts.provenance.replay.check`;
- the hand oracles of a year and a termination per contribution sector
  (``tests/knowledge/ccnl_engine/period/sector/scenarios.json``);
- the divergences of the review log, by decision, and the review dates.

The columns follow the dimensions of the validation review: source,
independence, cycle, relationship, variables, thresholds, outputs, outcome
and freshness.  Outputs split in three columns: complete totals
(:data:`~scripts.provenance.reference_case.check.AXES`), components of a
total and rates or rules.  Only a total covers an output: fixed allowances
never stand for the gross, an INPS rate never for the contributions.
Readiness depends on it: a ``production`` CCNL must cover every total of
the definition of done, or list what it misses in the shrink-only baseline
of :mod:`scripts.provenance.readiness.check`.

Run with::

    uv run python scripts/documentation/validation_matrix/generate.py

Check for drift without writing (for CI)::

    uv run python scripts/documentation/validation_matrix/generate.py --check
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.provenance.reference_case.check import (
    AXES,
    AXIS_OF,
    COMPONENTS,
    RULES,
    index,
)
from scripts.provenance.replay.check import credited_records
from scripts.provenance.rules import KNOWLEDGE_DIR

ROOT = Path(__file__).resolve().parents[3]
PAGE = ROOT / "docs" / "trust" / "validation-matrix.md"
_PERIOD = ROOT / "tests" / "knowledge" / "ccnl_engine" / "period"
SCENARIOS = _PERIOD / "sector" / "scenarios.json"
#: Outcome each divergence decision stands for.
_OUTCOMES = {
    "engine_bug": "engine bug fixed",
    "source_context_missing": "blocker",
    "accepted_external_variance": "explained variance",
    "external_artifact_error": "artifact rejected",
}


@dataclass
class Row:
    """The evidence of one CCNL, as sets of labels."""

    readiness: str
    last_review: str
    review_due: str
    sources: set[str] = field(default_factory=set)
    independence: set[str] = field(default_factory=set)
    cycles: set[str] = field(default_factory=set)
    relationships: set[str] = field(default_factory=set)
    variables: set[str] = field(default_factory=set)
    thresholds: set[str] = field(default_factory=set)
    outputs: set[str] = field(default_factory=set)
    components: set[str] = field(default_factory=set)
    rules: set[str] = field(default_factory=set)
    outcomes: set[str] = field(default_factory=set)

    def pin(self, labels: Iterable[str]) -> None:
        """Add each label to the totals, the components or the rules.

        Raises:
            ValueError: If a label is no total, component or rule.
        """
        for label in labels:
            if label in AXES:
                self.outputs.add(label)
            elif label in COMPONENTS:
                self.components.add(label)
            elif label in RULES:
                self.rules.add(label)
            else:
                msg = f"unknown output, component or rule {label!r}"
                raise ValueError(msg)

    @property
    def has_evidence(self) -> bool:
        """Whether any evidence runs the CCNL."""
        return bool(self.sources)


def _agreements() -> dict[str, Row]:
    rows: dict[str, Row] = {}
    for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json")):
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        verification = data.get("verification") or {}
        reviews = verification.get("reviews") or []
        row = Row(
            readiness=verification.get("readiness", "exploratory"),
            last_review=reviews[-1]["date"] if reviews else "—",
            review_due=verification.get("review_due") or "—",
        )
        for review in reviews:
            for divergence in review.get("divergences") or []:
                row.outcomes.add(_OUTCOMES[divergence["decision"]])
        rows[path.stem] = row
    return rows


def _add_reference_cases(rows: dict[str, Row]) -> None:
    for ccnl, cases in index().items():
        row = rows[ccnl]
        for case in cases:
            verified = case.verification == "verified"
            row.sources.add("payslip or official example" if verified else "primary")
            row.independence.add("provider output" if verified else "source-linked")
            row.cycles.add("ordinary month")
            row.relationships.add("permanent, full time")
            row.pin(case.axes + case.elements)
            row.outcomes.add("match")


def _add_payslips(rows: dict[str, Row]) -> None:
    today = datetime.now(tz=UTC).date()
    for replay in credited_records(today).values():
        row = rows[replay["inputs"]["ccnl_id"]]
        row.sources.add("real payslip")
        row.independence.add("provider output")
        row.cycles.add("ordinary month")
        row.relationships.add(f"{replay['inputs']['contract_type']}, hours not stated")
        row.thresholds.add(f"headcount {replay['inputs']['headcount']}")
        row.pin(AXIS_OF[key] for key in replay["expected"])
        known = replay.get("known_differences") or []
        row.outcomes.add("explained variance" if known else "match")


def _add_oracles(rows: dict[str, Row]) -> None:
    scenarios: dict[str, Any] = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    for scenario in scenarios.values():
        row = rows[scenario["ccnl"]]
        row.sources.add("primary")
        row.independence.add("hand oracle")
        row.cycles.update(scenario["cycles"])
        row.relationships.add(scenario["relationship"])
        row.variables.update(scenario["variables"])
        row.thresholds.update(scenario["thresholds"])
        row.pin(scenario["outputs"])
        row.outcomes.add("match")


def matrix() -> dict[str, Row]:
    """Return the rows of the page, by CCNL id.

    Returns:
        A row for each CCNL that is ``reviewed`` or ``production`` or that
        any evidence runs, in id order.
    """
    rows = _agreements()
    _add_reference_cases(rows)
    _add_payslips(rows)
    _add_oracles(rows)
    return {
        ccnl: row
        for ccnl, row in rows.items()
        if row.has_evidence or row.readiness != "exploratory"
    }


def _cell(labels: set[str]) -> str:
    return ", ".join(sorted(labels)) or "—"


def build_page(rows: dict[str, Row]) -> str:
    """Render the page.

    Returns:
        The Markdown of the page.
    """
    header = (
        "| CCNL | Readiness | Source | Independence | Cycle | Relationship "
        "| Variables | Thresholds | Totals | Components | Rates and rules "
        "| Outcome | Last review | Review due |"
    )
    lines = [
        "# Validation matrix",
        "",
        (
            "<!-- Generated by scripts/documentation/validation_matrix/generate.py:"
            " do not edit. -->"
        ),
        "",
        "What validates each CCNL that is `reviewed` or `production` or that any",
        "evidence runs: reference cases, observed payslips replayed through the",
        "engine, the hand oracles of each contribution sector, and the",
        "divergences of the review log. `primary` evidence checks the",
        "transcription of a signed source; a `hand oracle` recomputes the",
        "pipeline from the same sources; only a `provider output` (a real",
        "payslip, an official worked example) is independent of them.",
        "`Totals` lists the complete outputs compared; `Components` the parts",
        "of a total (fixed allowances, bases, tax components) and `Rates and",
        "rules` the rates compared: neither covers the total it belongs to.",
        "Readiness depends on the page: a `production` CCNL must cover every",
        "total (base salary, gross, employee and employer contributions, tax,",
        "net, TFR, employer cost), or list what it still misses in",
        "`scripts/provenance/readiness/baseline.json`, a list that only shrinks.",
        "",
        header,
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| `{ccnl}` | {row.readiness} | {_cell(row.sources)} "
        f"| {_cell(row.independence)} | {_cell(row.cycles)} "
        f"| {_cell(row.relationships)} | {_cell(row.variables)} "
        f"| {_cell(row.thresholds)} | {_cell(row.outputs)} "
        f"| {_cell(row.components)} | {_cell(row.rules)} "
        f"| {_cell(row.outcomes)} | {row.last_review} | {row.review_due} |"
        for ccnl, row in rows.items()
    )
    without = sorted(c for c, r in rows.items() if not r.has_evidence)
    lines += [
        "",
        f"{len(rows)} CCNLs listed; {len(without)} without any evidence"
        + (": " + ", ".join(f"`{c}`" for c in without) if without else "")
        + ".",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    """Write the page, or check it with ``--check``.

    Returns:
        The exit code.
    """
    page = build_page(matrix())
    if "--check" in argv:
        if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != page:
            print("docs/trust/validation-matrix.md is out of date.", file=sys.stderr)
            return 1
        print("OK: docs/trust/validation-matrix.md is up to date.")
        return 0
    PAGE.write_text(page, encoding="utf-8")
    print(f"Written {PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
