"""CCNL coverage matrix -- per-contract and per-feature metrics.

Aggregate the coverage blocks and data fields from every bundled CCNL
JSON file into two views:

* Per-CCNL: name, sector, coverage %, verification label, layer status.
* Per-feature: engine feature (base salary, seniority, IRPEF, ...),
  the layer it belongs to, and the percentage of contracts that implement it.

Not part of the engine API -- this is documentation tooling only.
Regenerate docs/coverage-matrix.md with::

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
    ccnl_id: str
    name: str
    sector: str
    coverage_pct: int
    """0-100, within-engine-scope score (layers 1 and 2)."""
    verification_label: str
    layer_1: str
    layer_2: str
    layer_3: str
    """Always 'not_implemented' -- overtime/leave/bonuses not yet in engine."""


@dataclass(frozen=True)
class FeatureRow:
    name: str
    layer: int
    """1 = gross, 2 = net, 3 = not yet in engine."""
    pct: int
    """0-100, percentage of CCNLs that implement this feature."""
    note: str


@dataclass(frozen=True)
class CoverageReport:
    ccnl_rows: list[CCNLCoverageRow]
    feature_rows: list[FeatureRow]
    generated_at: date


# Helpers


def _layer_score(status: str) -> float:
    return {"implemented": 1.0, "partial": 0.5, "out_of_scope": 0.0}[status]


def _coverage_pct(ccnl: CCNL) -> int:
    """0-100 score within the engine's scope (layers 1+2).

    Formula:
        base = layer_score(layer_1) * 0.6 + layer_score(layer_2) * 0.4
        penalty = min(missing_note_count * 0.05, 0.20)
        result = round((base - penalty) * 100)

    If meta.withholding_exempt=True and layer_2='out_of_scope', the employer
    not withholding IRPEF is by design -- layer_2 is not penalised.
    """
    l1 = _layer_score(ccnl.coverage.layer_1)
    l2_status = ccnl.coverage.layer_2
    if ccnl.meta.withholding_exempt and l2_status == "out_of_scope":
        l2 = 1.0
    else:
        l2 = _layer_score(l2_status)
    base = l1 * 0.6 + l2 * 0.4
    missing_count = sum(
        1 for n in ccnl.coverage.notes if n.kind == NoteKind.MISSING
    )
    penalty = min(missing_count * 0.05, 0.20)
    return round((base - penalty) * 100)


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
    return CCNLCoverageRow(
        ccnl_id=ccnl.meta.ccnl_id,
        name=ccnl.meta.name,
        sector=ccnl.meta.sector,
        coverage_pct=_coverage_pct(ccnl),
        verification_label=_verification_label(ccnl),
        layer_1=ccnl.coverage.layer_1,
        layer_2=ccnl.coverage.layer_2,
        layer_3="not_implemented",
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
    """0 for withholding-exempt contracts (intentional by design)."""
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

    return [
        FeatureRow("Base salary", 1, _pct(base_salary, n), "Minimo contrattuale da tabella CCNL"),
        FeatureRow("Seniority allowance", 1, _pct(seniority, n), "Scatti di anzianita"),
        FeatureRow("Fixed allowances", 1, _pct(allowances, n), "Indennita fisse contrattuali"),
        FeatureRow("Additional months", 1, _pct(float(n), n), "13/14 mensilita -- obbligatorio per schema"),
        FeatureRow("Hourly rate", 1, _pct(float(n), n), "Da divisore orario -- obbligatorio per schema"),
        FeatureRow("INPS contributions", 2, _pct(inps, n), "Contributi INPS dipendente e datore"),
        FeatureRow("TFR", 2, _pct(inps, n), "Trattamento fine rapporto Art. 2120 c.c."),
        FeatureRow("IRPEF", 2, _pct(irpef, n), "Ritenuta IRPEF (esclusi withholding-exempt per design)"),
        FeatureRow("Regional/municipal surtax", 2, _pct(irpef, n), "Addizionali -- richiede regione/comune in input"),
        FeatureRow("Overtime", 3, 0, "Non in scope -- engine layer 3"),
        FeatureRow("Sick/injury leave", 3, 0, "Non in scope -- engine layer 3"),
        FeatureRow("Performance bonuses", 3, 0, "Non in scope -- engine layer 3"),
        FeatureRow("Welfare/benefits", 3, 0, "Non in scope -- engine layer 3"),
    ]


# Public API


def build_coverage_report() -> CoverageReport:
    """Build a coverage report from all bundled CCNL JSON files."""
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    filenames = sorted(
        e.name for e in pkg.iterdir() if e.name.endswith(".json")
    )
    ccnls = [load_ccnl(fn) for fn in filenames]
    return CoverageReport(
        ccnl_rows=sorted(
            [_make_ccnl_row(c) for c in ccnls], key=lambda r: r.name
        ),
        feature_rows=_make_feature_rows(ccnls),
        generated_at=datetime.now(tz=UTC).date(),
    )


# Markdown rendering

_LAYER_BADGE = {
    1: "Layer 1 -- Gross",
    2: "Layer 2 -- Net",
    3: "Layer 3 -- Not implemented",
}


def render_markdown(report: CoverageReport) -> str:
    """Render report as a Markdown document string."""
    header = (
        "<!-- auto-generated"
        " -- run: uv run python docs/scripts/gen_coverage_matrix.py -->"
    )
    ccnl_header = (
        "| CCNL | Sector | Coverage | Verification"
        " | Layer 1 | Layer 2 | Layer 3 |"
    )
    ccnl_sep = (
        "|------|--------|----------|-------------|"
        "---------|---------|---------|"
    )
    lines: list[str] = [
        header,
        f"<!-- generated: {report.generated_at} -->",
        "",
        "# Coverage Matrix",
        "",
        f"Generated: {report.generated_at} - {len(report.ccnl_rows)} CCNL",
        "",
        "## Per-CCNL Coverage",
        "",
        ccnl_header,
        ccnl_sep,
    ]
    lines.extend(
        f"| {row.name} | {row.sector} | {row.coverage_pct}%"
        f" | {row.verification_label}"
        f" | {row.layer_1} | {row.layer_2} | {row.layer_3} |"
        for row in report.ccnl_rows
    )
    lines += [
        "",
        "## Feature Coverage",
        "",
        "| Feature | Layer | Coverage | Note |",
        "|---------|-------|----------|------|",
    ]
    current_layer = 0
    for row in report.feature_rows:
        if row.layer != current_layer:
            current_layer = row.layer
            lines.append(f"| **{_LAYER_BADGE[row.layer]}** | | | |")
        lines.append(
            f"| {row.name} | {row.layer} | {row.pct}% | {row.note} |"
        )
    lines.append("")
    return "\n".join(lines)
