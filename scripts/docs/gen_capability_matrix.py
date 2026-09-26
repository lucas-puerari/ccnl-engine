"""Generate docs/contracts/capability-matrix.md from knowledge-base JSON files.

The capability matrix shows, for each CCNL, the coverage status of every
payroll feature: L1 gross, L2 net, and each L3 work-rules sub-feature.

Run with::

    uv run python scripts/docs/gen_capability_matrix.py

Check for drift without writing (for CI)::

    uv run python scripts/docs/gen_capability_matrix.py --check
"""

import importlib.resources
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ccnl_engine.engine.contract.domain.identity import CoverageStatus, WorkRuleFeature
from ccnl_engine.engine.contract.service.loaders import load_ccnl

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

_DATE_LINE_RE = re.compile(r"<!-- generated: \d{4}-\d{2}-\d{2} -->\n?")

_PREAMBLE = """\
# Capability Matrix

Per-feature coverage for all {count} bundled CCNLs. Generated from
`coverage` blocks in the knowledge-base JSON files.

→ [CCNL Coverage index](index.md)

## Legend

| | |
|---|---|
| ✅ | Implemented |
| ⚠️ | Partial — see contract notes |
| 🚫 | Out of scope |
| 🔲 | Not yet implemented |

**L1 — Gross:** base salary, seniority, fixed allowances, additional months.
**L2 — Net:** INPS contributions, TFR, IRPEF, surtax, family deductions.
**OT / Night / Holiday / Absence / Sick / Leave / Bonus / Benefits /
Welfare / Fringe / Fam.Ded. / Co.Agr. / Terr.Agr.:** L3 work-rules
per-feature status.

## Matrix

"""


def _build_page() -> str:
    """Build the full capability-matrix markdown page.

    Returns:
        Markdown string for docs/contracts/capability-matrix.md.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    filenames = sorted(e.name for e in pkg.iterdir() if e.name.endswith(".json"))
    ccnls = sorted([load_ccnl(fn) for fn in filenames], key=lambda c: c.meta.name)

    features = list(WorkRuleFeature)
    feature_headers = " | ".join(_FEATURE_LABELS[f] for f in features)
    sep_cols = " | ".join(":---:" for _ in features)

    header = f"| # | CCNL | L1 | L2 | {feature_headers} |"
    sep = f"|---|---|:---:|:---:| {sep_cols} |"

    auto_comment = (
        "<!-- auto-generated"
        " -- run: uv run python scripts/docs/gen_capability_matrix.py -->\n"
    )
    lines: list[str] = [
        auto_comment,
        f"<!-- generated: {datetime.now(tz=UTC).date()} -->\n",
        _PREAMBLE.format(count=len(ccnls)),
        header,
        sep,
    ]

    for i, ccnl in enumerate(ccnls, 1):
        l1 = _SYMBOL[ccnl.coverage.gross]
        l2 = _SYMBOL[ccnl.coverage.net]
        link = f"[{ccnl.meta.name}]({ccnl.meta.ccnl_id}.md)"
        feature_cells = " | ".join(
            _SYMBOL[
                ccnl.coverage.work_rules_features.get(f, CoverageStatus.NOT_IMPLEMENTED)
            ]
            for f in features
        )
        lines.append(f"| {i} | {link} | {l1} | {l2} | {feature_cells} |")

    return "\n".join(lines)


def _strip_date(text: str) -> str:
    return _DATE_LINE_RE.sub("", text)


check_mode = "--check" in sys.argv
root = Path(__file__).parent.parent.parent
capability_matrix = root / "docs" / "contracts" / "capability-matrix.md"
generated = _build_page()

if check_mode:
    committed = capability_matrix.read_text(encoding="utf-8")
    if _strip_date(generated) != _strip_date(committed):
        print("docs/contracts/capability-matrix.md is out of date.", file=sys.stderr)
        print(
            "Run: uv run python scripts/docs/gen_capability_matrix.py",
            file=sys.stderr,
        )
        print("and commit the result.", file=sys.stderr)
        sys.exit(1)
    n = generated.count("\n| ")
    print(f"OK — docs/contracts/capability-matrix.md is up to date ({n} rows).")
else:
    capability_matrix.write_text(generated, encoding="utf-8")
    n = generated.count("\n| ")
    print(f"Written {capability_matrix} ({n} rows).")
