"""Generate docs/contracts/capability-matrix.md from knowledge-base JSON files.

The page has two tables, both derived from the capability registry:

- per capability: implementation, applicability, handler, facts and
  variants from the registry, and the provenance of the payable rules it
  reads;
- per CCNL: the functional coverage of each layer and the capabilities its
  data leaves partial, the same cells as the contracts index
  (:func:`scripts.docs.coverage_report.coverage_cells`).

Run with::

    uv run python scripts/docs/gen_capability_matrix.py

Check for drift without writing (for CI)::

    uv run python scripts/docs/gen_capability_matrix.py --check
"""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.payroll.capability.models_catalog import CapabilityImplementation
from scripts.ci.payable_rules import count_by_capability, count_by_file, inventory
from scripts.docs.coverage_report import (
    IMPLEMENTATION_LEGEND,
    bundled_ccnls,
    coverage_cells,
    latest_catalog_year,
    registry_summary,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.capability.models_catalog import (
        CapabilityCatalog,
        CapabilityEntry,
    )

__all__ = [
    "build_page",
    "capability_label",
    "capability_rows",
    "latest_catalog_year",
    "main",
]

_WEAK_SOURCES = ("assumed", "missing")

_AUTO_COMMENT = (
    "<!-- auto-generated; run: uv run python "
    "scripts/docs/gen_capability_matrix.py -->\n"
)
_DATE_LINE_RE = re.compile(r"<!-- generated: \d{4}-\d{2}-\d{2} -->\n?")

_PREAMBLE = """\
# Capability Matrix

What the engine computes for fiscal year {year}, and how far the bundled
data behind it is backed by sources. Generated from the capability registry
(`knowledge/capability/{year}/catalog.json`), the provenance records of the
payable rules, the `missing` notes and the model limitations of the {count}
bundled CCNLs. The
runtime capability report of every run, the [CCNL Coverage
index](index.md) and this page all derive from the same registry.

→ [Provenance statuses](../trust/provenance.md) ·
[Assurance of a result](../trust/index.md)

## Capabilities

Each capability declares:

- **Implementation:** `native` (bundled rules and request facts),
  `caller_supplied` (a caller rate or amount stands in for a rule),
  `partial` (only the listed variants) or `unsupported`.
- **Applies when:** `always`; `decided` by its decision owner; `event`
  (the request declares an event of the capability); `termination_run`
  (the run closes the employment); `outside_input` (the request has no
  field for the fact that makes it apply: a case with that fact is outside
  the engine input).
- **Handler:** the code that decides and traces it (`pipeline`, `event`,
  `decision`); an unsupported capability has none.
- **Facts:** the request facts it reads; for an `outside_input` capability,
  the fact the request lacks.

A run reports every capability as `applicable`, `not_applicable` or
`outside_input`. Only an applicable capability can leave a gap: an
unsupported one blocks payment, a partial one that executed makes the
coverage partial and blocks payment too.

| Label | Meaning |
|---|---|
| verified | Implemented; a named person checked every bundled rule it reads |
| caller-supplied | Computed from caller rates or amounts that stand in for a rule |
| implemented | Computed; the bundled rules it reads, if any, cite a source |
| simplified | Partial, or reads an `assumed` or `missing` rule |
| unavailable | Not computed by the engine |

Rules counts the payable rules of the bundle each capability reads, by
provenance status: verified / derived / assumed / missing. "none bundled"
means the capability reads no bundled table: it computes from engine
formulas or caller-declared amounts.
"""

_CCNL_PREAMBLE = """
## CCNL coverage

The same cells as the [CCNL Coverage index](index.md). **Limits** names the
capabilities a `missing` note or a model limitation with a monetary impact
of the contract file lowers to partial. **Rules** counts the payable rules
of the contract file by provenance status: verified / derived / assumed /
missing. The `assumed` and `missing` ones are listed in the shrink-only
evidence baseline (`scripts/ci/provenance_baseline.json`), so these counts
never grow.

{legend}
"""


def capability_label(entry: CapabilityEntry, counts: Mapping[str, int]) -> str:
    """Return the matrix label of one registry capability.

    Args:
        entry: The registry entry.
        counts: Payable rules the capability reads, by provenance status.

    Returns:
        ``unavailable``, ``caller-supplied``, ``simplified``, ``verified`` or
        ``implemented``, the first that applies.
    """
    implementation = entry.implementation
    if implementation is CapabilityImplementation.UNSUPPORTED:
        return "unavailable"
    if implementation is CapabilityImplementation.CALLER_SUPPLIED:
        return "caller-supplied"
    if implementation is CapabilityImplementation.PARTIAL or any(
        counts.get(status, 0) for status in _WEAK_SOURCES
    ):
        return "simplified"
    total = sum(counts.values())
    if total and counts.get("verified", 0) == total:
        return "verified"
    return "implemented"


def _rules(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none bundled"
    return " / ".join(
        str(counts.get(s, 0)) for s in ("verified", "derived", "assumed", "missing")
    )


def capability_rows(
    catalog: CapabilityCatalog, by_capability: Mapping[str, Mapping[str, int]]
) -> list[str]:
    """Return the capability table, header included.

    Args:
        catalog: Capability registry of the year.
        by_capability: Payable rules per capability and provenance status.

    Returns:
        Markdown table lines, one row per registry capability.
    """
    lines = [
        (
            "| Capability | Description | Layer | Implementation | Applies when"
            " | Handler | Facts | Variants | Label | Rules (v / d / a / m) |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for entry in catalog.capabilities:
        counts = by_capability.get(entry.feature, {})
        facts = ", ".join(f"`{f}`" for f in entry.required_facts) or "—"
        variants = ", ".join(entry.variants) or "—"
        lines.append(
            f"| `{entry.feature}` | {entry.description} | {entry.layer.value} "
            f"| {entry.implementation.value} | {entry.applies_when.value} "
            f"| {entry.handler.value if entry.handler else '—'} | {facts} "
            f"| {variants} | {capability_label(entry, counts)} | {_rules(counts)} |"
        )
    return lines


def _ccnl_rows(
    catalog: CapabilityCatalog, by_file: Mapping[str, Mapping[str, int]]
) -> list[str]:
    """Return the CCNL coverage table, header included.

    Args:
        catalog: Capability registry of the year.
        by_file: Payable rules per data file and provenance status.

    Returns:
        Markdown table lines, one row per bundled CCNL.
    """
    lines = [
        "| # | CCNL | L1 | L2 | L3 | Limits | Rules (v / d / a / m) |",
        "|---|---|:---:|:---:|:---:|---|---|",
    ]
    for i, ccnl in enumerate(bundled_ccnls(), 1):
        cells = coverage_cells(catalog, ccnl)
        l1, l2, l3 = cells.layers
        link = f"[{ccnl.meta.name}]({ccnl.meta.ccnl_id}.md)"
        rules = _rules(by_file.get(f"contract/agreement/{ccnl.meta.ccnl_id}.json", {}))
        lines.append(
            f"| {i} | {link} | {l1} | {l2} | {l3} | {cells.limits} | {rules} |"
        )
    return lines


def build_page(year: int) -> str:
    """Build the full capability-matrix markdown page.

    Args:
        year: Fiscal year of the capability registry.

    Returns:
        Markdown string for docs/contracts/capability-matrix.md.
    """
    catalog = load_capability_catalog(year)
    rules = inventory()
    ccnl_rows = _ccnl_rows(catalog, count_by_file(rules))
    lines: list[str] = [
        _AUTO_COMMENT,
        f"<!-- generated: {datetime.now(tz=UTC).date()} -->\n",
        _PREAMBLE.format(year=year, count=len(ccnl_rows) - 2),
        *registry_summary(catalog),
        "",
        *capability_rows(catalog, count_by_capability(rules)),
        _CCNL_PREAMBLE.format(legend=IMPLEMENTATION_LEGEND),
        *ccnl_rows,
    ]
    return "\n".join(lines) + "\n"


def _strip_date(text: str) -> str:
    return _DATE_LINE_RE.sub("", text)


def main() -> None:
    """Write the page, or check it for drift with ``--check``."""
    root = Path(__file__).resolve().parents[2]
    capability_matrix = root / "docs" / "contracts" / "capability-matrix.md"
    generated = build_page(latest_catalog_year())
    rows = generated.count("\n| ")
    if "--check" not in sys.argv:
        capability_matrix.write_text(generated, encoding="utf-8")
        print(f"Written {capability_matrix} ({rows} rows).")
        return
    committed = capability_matrix.read_text(encoding="utf-8")
    if _strip_date(generated) != _strip_date(committed):
        print("docs/contracts/capability-matrix.md is out of date.", file=sys.stderr)
        print(
            "Run: uv run python scripts/docs/gen_capability_matrix.py",
            file=sys.stderr,
        )
        print("and commit the result.", file=sys.stderr)
        sys.exit(1)
    print(f"OK: docs/contracts/capability-matrix.md is up to date ({rows} rows).")


if __name__ == "__main__":
    main()
