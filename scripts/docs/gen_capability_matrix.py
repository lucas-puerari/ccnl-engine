"""Generate docs/contracts/capability-matrix.md from knowledge-base JSON files.

The page has two tables:

- per capability of the fiscal-year catalog: whether it is implemented,
  verified, simplified or unavailable, from the catalog status and the
  provenance status of the payable rules it reads;
- per CCNL: the coverage status of every payroll feature, L1 gross, L2 net
  and each L3 work-rules sub-feature.

Run with::

    uv run python scripts/docs/gen_capability_matrix.py

Check for drift without writing (for CI)::

    uv run python scripts/docs/gen_capability_matrix.py --check
"""

from __future__ import annotations

import importlib.resources
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.contract.domain.identity import CoverageStatus, WorkRuleFeature
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.payroll.application.period._caller_rules import (
    CALLER_SUPPLIED_CAPABILITIES,
)
from ccnl_engine.payroll.domain.capability_catalog import CapabilityStatus
from scripts.ci.payable_rules import count_by_capability, inventory

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.domain.capability_catalog import (
        CapabilityCatalog,
        CapabilityEntry,
    )

# Abbreviated column headers (keep short for table readability).
_FEATURE_LABELS: dict[WorkRuleFeature, str] = {
    WorkRuleFeature.OVERTIME: "OT",
    WorkRuleFeature.NIGHT_WORK: "Night",
    WorkRuleFeature.HOLIDAY_WORK: "Holiday",
    WorkRuleFeature.ABSENCE: "Absence",
    WorkRuleFeature.SICKNESS: "Sick",
    WorkRuleFeature.LEAVE: "Leave",
    WorkRuleFeature.BONUS: "Bonus",
    WorkRuleFeature.BENEFITS: "Benefits",
    WorkRuleFeature.WELFARE: "Welfare",
    WorkRuleFeature.FRINGE_BENEFITS: "Fringe",
    WorkRuleFeature.FAMILY_DEDUCTIONS: "Fam.Ded.",
    WorkRuleFeature.COMPANY_AGREEMENT: "Co.Agr.",
    WorkRuleFeature.TERRITORIAL_AGREEMENT: "Terr.Agr.",
}

_SYMBOL: dict[str, str] = {
    "implemented": "✅",
    "partial": "⚠️",
    "out_of_scope": "🚫",
    "not_implemented": "🔲",
}

_UNAVAILABLE = frozenset({
    CapabilityStatus.NOT_COMPUTED,
    CapabilityStatus.BLOCKED,
    CapabilityStatus.NOT_APPLICABLE,
})
_WEAK_SOURCES = ("assumed", "missing")

_AUTO_COMMENT = (
    "<!-- auto-generated; run: uv run python "
    "scripts/docs/gen_capability_matrix.py -->\n"
)
_DATE_LINE_RE = re.compile(r"<!-- generated: \d{4}-\d{2}-\d{2} -->\n?")

_PREAMBLE = """\
# Capability Matrix

What the engine computes for fiscal year {year}, and how far the bundled
data behind it is backed by sources. Generated from the capability catalog,
the provenance records of the payable rules and the `coverage` blocks of the
{count} bundled CCNLs.

→ [CCNL Coverage index](index.md) ·
[Provenance statuses](../trust/provenance.md)

## Capabilities

| Label | Meaning |
|---|---|
| verified | Implemented; a named person checked every bundled rule it reads |
| caller-supplied | Computed from caller rates or amounts that stand in for a rule |
| implemented | Computed; the bundled rules it reads, if any, cite a source |
| simplified | Computed partially, or reads an `assumed` or `missing` rule |
| unavailable | Not computed by the engine |

Rules counts the payable rules of the bundle each capability reads, by
provenance status: verified / derived / assumed / missing. "none bundled"
means the capability reads no bundled table: it computes from engine
formulas or caller-declared amounts.
"""

_CCNL_PREAMBLE = """
## CCNL coverage

| | |
|---|---|
| ✅ | Implemented |
| ⚠️ | Partial, see contract notes |
| 🚫 | Out of scope |
| 🔲 | Not yet implemented |

**L1 (gross):** base salary, seniority, fixed allowances, additional months.
**L2 (net):** INPS contributions, TFR, IRPEF, surtax, family deductions.
**OT / Night / Holiday / Absence / Sick / Leave / Bonus / Benefits /
Welfare / Fringe / Fam.Ded. / Co.Agr. / Terr.Agr.:** L3 work-rules
per-feature status.

"""


def capability_label(entry: CapabilityEntry, counts: Mapping[str, int]) -> str:
    """Return the matrix label of one catalog capability.

    Args:
        entry: The catalog entry.
        counts: Payable rules the capability reads, by provenance status.

    Returns:
        ``unavailable``, ``caller-supplied``, ``simplified``, ``verified`` or
        ``implemented``, the first that applies.
    """
    if entry.status in _UNAVAILABLE:
        return "unavailable"
    if entry.feature in CALLER_SUPPLIED_CAPABILITIES:
        return "caller-supplied"
    if entry.status is CapabilityStatus.PARTIALLY_COMPUTED or any(
        counts.get(status, 0) for status in _WEAK_SOURCES
    ):
        return "simplified"
    total = sum(counts.values())
    if total and counts.get("verified", 0) == total:
        return "verified"
    return "implemented"


def capability_rows(
    catalog: CapabilityCatalog, by_capability: Mapping[str, Mapping[str, int]]
) -> list[str]:
    """Return the capability table, header included.

    Args:
        catalog: Capability catalog of the year.
        by_capability: Payable rules per capability and provenance status.

    Returns:
        Markdown table lines, one row per catalog capability.
    """
    lines = [
        "| Capability | Description | Catalog | Label | Rules (v / d / a / m) |",
        "|---|---|---|---|---|",
    ]
    for entry in catalog.capabilities:
        counts = by_capability.get(entry.feature, {})
        rules = (
            " / ".join(
                str(counts.get(s, 0))
                for s in ("verified", "derived", "assumed", "missing")
            )
            if counts
            else "none bundled"
        )
        lines.append(
            f"| `{entry.feature}` | {entry.description} | {entry.status.value} "
            f"| {capability_label(entry, counts)} | {rules} |"
        )
    return lines


def _ccnl_rows() -> list[str]:
    """Return the CCNL coverage table, header included.

    Returns:
        Markdown table lines, one row per bundled CCNL.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    filenames = sorted(e.name for e in pkg.iterdir() if e.name.endswith(".json"))
    ccnls = sorted([load_ccnl(fn) for fn in filenames], key=lambda c: c.meta.name)
    features = list(WorkRuleFeature)
    feature_headers = " | ".join(_FEATURE_LABELS[f] for f in features)
    sep_cols = " | ".join(":---:" for _ in features)
    lines = [
        f"| # | CCNL | L1 | L2 | {feature_headers} |",
        f"|---|---|:---:|:---:| {sep_cols} |",
    ]
    for i, ccnl in enumerate(ccnls, 1):
        link = f"[{ccnl.meta.name}]({ccnl.meta.ccnl_id}.md)"
        feature_cells = " | ".join(
            _SYMBOL[
                ccnl.coverage.work_rules_features.get(f, CoverageStatus.NOT_IMPLEMENTED)
            ]
            for f in features
        )
        l1, l2 = _SYMBOL[ccnl.coverage.gross], _SYMBOL[ccnl.coverage.net]
        lines.append(f"| {i} | {link} | {l1} | {l2} | {feature_cells} |")
    return lines


def build_page(year: int) -> str:
    """Build the full capability-matrix markdown page.

    Args:
        year: Fiscal year of the capability catalog.

    Returns:
        Markdown string for docs/contracts/capability-matrix.md.
    """
    catalog = load_capability_catalog(year)
    ccnl_rows = _ccnl_rows()
    lines: list[str] = [
        _AUTO_COMMENT,
        f"<!-- generated: {datetime.now(tz=UTC).date()} -->\n",
        _PREAMBLE.format(year=year, count=len(ccnl_rows) - 2),
        *capability_rows(catalog, count_by_capability(inventory())),
        _CCNL_PREAMBLE,
        *ccnl_rows,
    ]
    return "\n".join(lines) + "\n"


def latest_catalog_year() -> int:
    """Return the latest fiscal year with a bundled capability catalog.

    Returns:
        The year of the newest ``capabilities/data/<year>.json``.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.capabilities.data")
    return max(
        int(e.name.split(".")[0])
        for e in pkg.iterdir()
        if e.name.split(".")[0].isdigit()
    )


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
