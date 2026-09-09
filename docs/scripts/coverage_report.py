"""CCNL coverage data for the per-contract index page.

Aggregates the coverage blocks and data fields from every bundled CCNL
JSON file into a per-contract view:

* CNEL code, name (linked), sector, workers estimate, coverage %,
  L1/L2/L3 symbols, verification emoji.

Not part of the engine API -- documentation tooling only.
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
    """0-100 score: L1 x 50% + L2 x 35% + work_rules x 15% - penalty."""
    verification_label: str
    gross: str
    net: str
    work_rules: str


@dataclass(frozen=True)
class CoverageReport:
    """Aggregated coverage data for the full CCNL bundle."""

    ccnl_rows: list[CCNLCoverageRow]
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
    """0-100 score: L1 x 50% + L2 x 35% + work_rules x 15% - penalty.

    Formula:
        base = L1 * 0.50 + L2 * 0.35 + work_rules * 0.15
        penalty = min(missing_note_count * 0.05, 0.20)
        result = round((base - penalty) * 100)

    work_rules defaults to 'not_implemented' for most contracts, so the
    effective maximum is 85 until a contract implements work-rules features.

    If meta.withholding_exempt=True and layer_2='out_of_scope', the employer
    not withholding IRPEF is by design -- layer_2 is not penalised.

    Returns:
        Coverage percentage as an integer in [0, 100].
    """
    l1 = _layer_score(ccnl.coverage.gross)
    l2_status = ccnl.coverage.net
    if ccnl.meta.withholding_exempt and l2_status == "out_of_scope":
        l2 = 1.0
    else:
        l2 = _layer_score(l2_status)
    wr = _layer_score(ccnl.coverage.work_rules)
    base = l1 * 0.50 + l2 * 0.35 + wr * 0.15
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
        gross=ccnl.coverage.gross,
        net=ccnl.coverage.net,
        work_rules=ccnl.coverage.work_rules,
    )


# Public API


def build_coverage_report() -> CoverageReport:
    """Build a coverage report from all bundled CCNL JSON files.

    Returns:
        CoverageReport with per-CCNL rows sorted by name.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    filenames = sorted(e.name for e in pkg.iterdir() if e.name.endswith(".json"))
    ccnls = [load_ccnl(fn) for fn in filenames]
    return CoverageReport(
        ccnl_rows=sorted([_make_ccnl_row(c) for c in ccnls], key=lambda r: r.name),
        generated_at=datetime.now(tz=UTC).date(),
    )


# Markdown rendering

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

**L2 — Net:** INPS contributions, TFR, IRPEF, regional/municipal surtax,
family deductions (Art. 12), mortgage interest deduction (Art. 15).

**L3 — Work rules:** overtime/night/holiday supplements, sick/injury leave,
leave entitlement, absence deduction.

**Coverage %:** (L1 x 50% + L2 x 35% + work_rules x 15%) - 5% per missing data
note (max -20%). work_rules status defaults to not_implemented for most contracts
(data exists but coverage block not yet updated); current maximum is 85%.

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
        l1 = _LAYER_SYMBOL[row.gross]
        l2 = _LAYER_SYMBOL[row.net]
        l3 = _LAYER_SYMBOL[row.work_rules]
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
