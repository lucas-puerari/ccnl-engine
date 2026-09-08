"""CCNL coverage matrix -- per-contract and per-feature metrics.

Aggregate the coverage blocks and data fields from every bundled CCNL
JSON file into two views:

* Per-CCNL: CNEL code, name (linked), sector, workers estimate, coverage %,
  L1/L2/L3 symbols, verification emoji.
* Per-feature: engine feature (base salary, seniority, IRPEF, ...),
  grouped by layer, with % of contracts implementing it.

Not part of the engine API -- this is documentation tooling only.
Regenerate output files with::

    uv run python docs/scripts/gen_coverage_matrix.py
"""

from __future__ import annotations

import importlib.resources
from dataclasses import dataclass
from datetime import UTC, date, datetime

from ccnl_engine.engine.contract.domain.ccnl import CCNL, NoteKind
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.provenance.domain.extraction import ExtractionMethod

# Data classes


@dataclass(frozen=True)
class CCNLCoverageRow:
    """One row in the per-CCNL coverage table."""

    ccnl_id: str
    cnel_code: str
    name: str
    sector: str
    workers_estimate: str
    agreement_year: str
    """4-digit renewal year, e.g. '2024'. Empty string when not recorded."""
    coverage_pct: int
    """0-100, score across layers 1-3 (L1*50% + L2*35% + L3*15% - penalty)."""
    verification_label: str
    layer_1: str
    layer_2: str
    layer_3: str


@dataclass(frozen=True)
class FeatureRow:
    """One row in the per-feature coverage table."""

    name: str
    layer: int
    """1 = gross, 2 = net, 3 = not yet in engine."""
    pct: int
    """0-100, percentage of CCNLs that implement this feature."""
    note: str


@dataclass(frozen=True)
class CoverageReport:
    """Aggregated coverage data for the full CCNL bundle."""

    ccnl_rows: list[CCNLCoverageRow]
    feature_rows: list[FeatureRow]
    generated_at: date


# Helpers


def _layer_score(status: str) -> float:
    return {
        "implemented": 1.0,
        "partial": 0.5,
        "out_of_scope": 0.0,
        "not_implemented": 0.0,
    }[status]


def _coverage_pct(ccnl: CCNL) -> int:
    """0-100 score across layers 1-3.

    Formula:
        base = L1 * 0.50 + L2 * 0.35 + L3 * 0.15
        penalty = min(missing_note_count * 0.05, 0.20)
        result = round((base - penalty) * 100)

    L3 defaults to 'not_implemented' for all current contracts, so the
    effective maximum is 85 until a contract implements extended features.

    If meta.withholding_exempt=True and layer_2='out_of_scope', the employer
    not withholding IRPEF is by design -- layer_2 is not penalised.

    Returns:
        Coverage percentage as an integer in [0, 100].
    """
    l1 = _layer_score(ccnl.coverage.layer_1)
    l2_status = ccnl.coverage.layer_2
    if ccnl.meta.withholding_exempt and l2_status == "out_of_scope":
        l2 = 1.0
    else:
        l2 = _layer_score(l2_status)
    l3 = _layer_score(ccnl.coverage.layer_3)
    base = l1 * 0.50 + l2 * 0.35 + l3 * 0.15
    missing_count = sum(1 for n in ccnl.coverage.notes if n.kind == NoteKind.MISSING)
    penalty = min(missing_count * 0.05, 0.20)
    return round((base - penalty) * 100)


_LAYER_SYMBOL = {
    "implemented": "✅",
    "partial": "⚠️",
    "out_of_scope": "🚫",
    "not_implemented": "🔲",
}

_VERIFICATION_EMOJI = {
    "Machine extracted": "🤖",
    "Human verified": "🧑",
    "Expert verified": "🧑✓",
    "Needs review": "🔍",
}


def _verification_label(ccnl: CCNL) -> str:
    vs = ccnl.coverage.verification_status
    if vs == VerificationStatus.VERIFIED:
        if ccnl.meta.extraction.method == ExtractionMethod.MANUAL:
            return "Expert verified"
        return "Human verified"
    if vs == VerificationStatus.NEEDS_REVIEW:
        return "Needs review"
    return "Machine extracted"


def _has_seniority(ccnl: CCNL) -> bool:
    si = ccnl.parameters.seniority_increments
    return (
        bool(si.amount_by_level)
        or bool(si.tiers)
        or bool(si.amount_by_level_by_category)
    )


def _has_fixed_allowances(ccnl: CCNL) -> bool:
    return any(bool(level.fixed_allowances) for level in ccnl.levels)


def _make_ccnl_row(ccnl: CCNL) -> CCNLCoverageRow:
    year = (ccnl.meta.agreement_date or "")[:4]
    return CCNLCoverageRow(
        ccnl_id=ccnl.meta.ccnl_id,
        cnel_code=ccnl.meta.cnel_code,
        name=ccnl.meta.name,
        sector=ccnl.meta.sector,
        workers_estimate=ccnl.meta.workers_estimate,
        agreement_year=year,
        coverage_pct=_coverage_pct(ccnl),
        verification_label=_verification_label(ccnl),
        layer_1=ccnl.coverage.layer_1,
        layer_2=ccnl.coverage.layer_2,
        layer_3=ccnl.coverage.layer_3,
    )


def _pct(score: float, total: int) -> int:
    if total == 0:
        return 0
    return round(score / total * 100)


def _inps_score(ccnl: CCNL) -> float:
    if ccnl.meta.withholding_exempt:
        return 1.0
    if ccnl.coverage.layer_2 == "implemented":
        return 1.0
    if ccnl.coverage.layer_2 == "partial":
        return 0.5
    return 0.0


def _irpef_score(ccnl: CCNL) -> float:
    """Compute IRPEF score; 0 for withholding-exempt contracts by design.

    Returns:
        1.0, 0.5, or 0.0 depending on layer_2 status and withholding_exempt.
    """
    if ccnl.meta.withholding_exempt:
        return 0.0
    if ccnl.coverage.layer_2 == "implemented":
        return 1.0
    if ccnl.coverage.layer_2 == "partial":
        return 0.5
    return 0.0


def _make_feature_rows(ccnls: list[CCNL]) -> list[FeatureRow]:
    n = len(ccnls)

    # Layer 1 -- gross
    base_salary = sum(
        1.0
        if c.coverage.layer_1 == "implemented"
        else (0.5 if c.coverage.layer_1 == "partial" else 0.0)
        for c in ccnls
    )
    seniority = sum(1.0 if _has_seniority(c) else 0.0 for c in ccnls)
    allowances = sum(1.0 if _has_fixed_allowances(c) else 0.0 for c in ccnls)

    # Layer 2 -- net
    inps = sum(_inps_score(c) for c in ccnls)
    irpef = sum(_irpef_score(c) for c in ccnls)

    always_100 = _pct(float(n), n)
    return [
        FeatureRow(
            "Base salary",
            1,
            _pct(base_salary, n),
            "Minimo contrattuale da tabella CCNL",
        ),
        FeatureRow(
            "Seniority allowance",
            1,
            _pct(seniority, n),
            "Scatti di anzianita",
        ),
        FeatureRow(
            "Fixed allowances",
            1,
            _pct(allowances, n),
            "Indennita fisse contrattuali",
        ),
        FeatureRow(
            "Additional months",
            1,
            always_100,
            "13/14 mensilita -- obbligatorio per schema",
        ),
        FeatureRow(
            "Hourly rate",
            1,
            always_100,
            "Da divisore orario -- obbligatorio per schema",
        ),
        FeatureRow(
            "INPS contributions",
            2,
            _pct(inps, n),
            "Contributi INPS dipendente e datore",
        ),
        FeatureRow(
            "TFR",
            2,
            _pct(inps, n),
            "Trattamento fine rapporto Art. 2120 c.c.",
        ),
        FeatureRow(
            "IRPEF",
            2,
            _pct(irpef, n),
            "Ritenuta IRPEF (esclusi withholding-exempt per design)",
        ),
        FeatureRow(
            "Regional/municipal surtax",
            2,
            _pct(irpef, n),
            "Addizionali -- richiede regione/comune in input",
        ),
        FeatureRow("Overtime", 3, 0, "Not yet implemented -- engine layer 3"),
        FeatureRow("Sick/injury leave", 3, 0, "Not yet implemented -- engine layer 3"),
        FeatureRow("Performance bonuses", 3, 0, "Not yet implemented -- layer 3"),
        FeatureRow("Welfare/benefits", 3, 0, "Not yet implemented -- engine layer 3"),
    ]


# Public API


def build_coverage_report() -> CoverageReport:
    """Build a coverage report from all bundled CCNL JSON files.

    Returns:
        CoverageReport with per-CCNL and per-feature rows.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    filenames = sorted(e.name for e in pkg.iterdir() if e.name.endswith(".json"))
    ccnls = [load_ccnl(fn) for fn in filenames]
    return CoverageReport(
        ccnl_rows=sorted([_make_ccnl_row(c) for c in ccnls], key=lambda r: r.name),
        feature_rows=_make_feature_rows(ccnls),
        generated_at=datetime.now(tz=UTC).date(),
    )


# Markdown rendering

_LAYER_TITLES = {
    1: "Layer 1 -- Gross",
    2: "Layer 2 -- Net",
    3: "Layer 3 -- Extended (not yet implemented)",
}

_CONTRACTS_PREAMBLE = """\
# CCNL Coverage

100+ contract configurations covering approximately **16 million employees** across
private and public sectors -- including ARAN public-sector agreements (funzioni
centrali, locali, sanità, istruzione) and one Presidential Decree (DPR 53/2025[^3]).
Covers 75+ of the ~99 major private-sector CCNLs (>10,000 workers, CNEL II/2024).

→ [Domain: What is a CCNL](../domain/index.md)

## Legend

| | |
|---|---|
| ✅ | Implemented |
| ⚠️ | Partial -- see contract notes |
| 🚫 | Out of scope |
| 🔲 | Not yet implemented |
| 🤖 | Machine extracted |
| 🧑 | Human reviewed |

**L1 — Gross:** base salary, seniority, fixed allowances,
additional months, hourly rate.
**L2 — Net:** INPS contributions, TFR, IRPEF, regional/municipal surtax.
**L3 — Extended:** overtime, sick/injury leave, performance bonuses, welfare/benefits.
**Coverage %:** (L1 x 50% + L2 x 35% + L3 x 15%) - 5% per missing data note (max -20%).
L3 defaults to not yet implemented; current contracts score a maximum of 85%.

## Matrix
"""

_CONTRACTS_FOOTER = """
[^1]: Approximate estimates. Sources: CNEL, INPS, Ministero del Lavoro, \
CCNL renewal communications.
[^2]: Salary tables extracted from official CCNL documents using AI-assisted \
tooling, no manual human review. Verify against the official source before use \
in production.
[^3]: DPR 53/2025 -- Compensation for Forze di Polizia ad ordinamento civile is \
set by Presidential Decree, not a CNEL-registered agreement. \
D.P.R. 24 marzo 2025, n. 53 (GU n. 91, 18 April 2025, SO).
"""


def render_contracts_index(report: CoverageReport) -> str:
    """Render the contracts/index.md page with per-CCNL data and links.

    Returns:
        Markdown string for docs/contracts/index.md.
    """
    auto_header = (
        "<!-- auto-generated"
        " -- run: uv run python docs/scripts/gen_coverage_matrix.py -->\n"
        f"<!-- generated: {report.generated_at} -->\n"
    )
    lines: list[str] = [
        auto_header,
        _CONTRACTS_PREAMBLE,
        (
            "| # | CNEL | CCNL | Sector | Workers (~)[^1]"
            " | Renewal | Coverage | L1 | L2 | L3 | Ext[^2] |"
        ),
        "|---|---|---|---|---:|:---:|---:|:---:|:---:|:---:|:---:|",
    ]
    for i, row in enumerate(report.ccnl_rows, 1):
        l1 = _LAYER_SYMBOL[row.layer_1]
        l2 = _LAYER_SYMBOL[row.layer_2]
        l3 = _LAYER_SYMBOL[row.layer_3]
        ext = _VERIFICATION_EMOJI[row.verification_label]
        workers = row.workers_estimate or "—"
        renewal = row.agreement_year or "—"
        link = f"[{row.name}]({row.ccnl_id}.md)"
        lines.append(
            f"| {i} | {row.cnel_code} | {link} | {row.sector}"
            f" | {workers} | {renewal} | {row.coverage_pct}%"
            f" | {l1} | {l2} | {l3} | {ext} |"
        )
    lines.append(_CONTRACTS_FOOTER)
    return "\n".join(lines)


def render_feature_matrix(report: CoverageReport) -> str:
    """Render the feature coverage matrix, one table per layer.

    Returns:
        Markdown string for docs/coverage-matrix.md.
    """
    auto_header = (
        "<!-- auto-generated"
        " -- run: uv run python docs/scripts/gen_coverage_matrix.py -->\n"
        f"<!-- generated: {report.generated_at} -->"
    )
    lines: list[str] = [
        auto_header,
        "",
        "# Feature Coverage Matrix",
        "",
        f"Generated: {report.generated_at} - {len(report.ccnl_rows)} CCNL",
        "",
        (
            "Coverage % = percentage of bundled CCNLs that implement"
            " the feature (partial = 0.5)."
        ),
        "",
    ]
    by_layer: dict[int, list[FeatureRow]] = {}
    for row in report.feature_rows:
        by_layer.setdefault(row.layer, []).append(row)

    for layer, rows in sorted(by_layer.items()):
        lines += [
            f"## {_LAYER_TITLES[layer]}",
            "",
            "| Feature | Coverage | Note |",
            "|---------|----------|------|",
        ]
        for row in rows:
            lines.append(f"| {row.name} | {row.pct}% | {row.note} |")
        lines.append("")
    return "\n".join(lines)
