"""CCNL coverage data for the contracts index and the capability matrix.

Every coverage cell comes from one derivation: the capability registry of
the fiscal year, lowered for a CCNL by the ``missing`` notes of its file
(``ccnl_engine.payroll.capability.services_coverage``).  The index and the
matrix render the same :func:`coverage_cells`, so they cannot disagree.

Functional coverage, source quality and readiness are three separate axes;
no percentage blends them.

Not part of the engine API -- documentation tooling only.
Regenerate output files with::

    uv run python scripts/docs/gen_coverage_matrix.py
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.knowledge.loaders_manifest import resources
from ccnl_engine.payroll.capability.models_catalog import (
    CapabilityImplementation,
    CapabilityLayer,
)
from ccnl_engine.payroll.capability.services_coverage import (
    ccnl_capabilities,
    layer_coverage,
)
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.provenance.source.models_extraction import ExtractionMethod
from scripts.ci.payable_rules import inventory

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.capability.models_catalog import CapabilityCatalog

#: Symbol of each implementation, shared by the index and the matrix.
IMPLEMENTATION_SYMBOL: dict[CapabilityImplementation, str] = {
    CapabilityImplementation.NATIVE: "✅",
    CapabilityImplementation.CALLER_SUPPLIED: "📝",
    CapabilityImplementation.PARTIAL: "⚠️",
    CapabilityImplementation.UNSUPPORTED: "🔲",
}

IMPLEMENTATION_LEGEND = """\
| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |
"""

_STATUSES = ("verified", "derived", "assumed", "missing")

_VERIFICATION_EMOJI = {
    "Machine extracted": "🤖",
    "Human verified": "🧑",
    "Expert verified": "🧑✓",
    "Needs review": "🔍",
}

_READINESS_SYMBOL = {
    RulesetReadiness.EXPLORATORY: "🧪",
    RulesetReadiness.REVIEWED: "👁",
    RulesetReadiness.PRODUCTION: "🏭",
}


@dataclass(frozen=True)
class CoverageCells:
    """Functional coverage of one CCNL as rendered in both pages.

    Attributes:
        layers: Symbol of the gross, net and work-rules layers.
        limits: Capabilities a ``missing`` note of the CCNL lowers to
            partial, comma separated; ``—`` when none.
    """

    layers: tuple[str, str, str]
    limits: str


def coverage_cells(catalog: CapabilityCatalog, ccnl: CCNL) -> CoverageCells:
    """Return the functional coverage cells of *ccnl*.

    Returns:
        The layer symbols and the CCNL-specific limits.
    """
    capabilities = ccnl_capabilities(catalog, ccnl)
    layers = layer_coverage(capabilities)
    gross, net, work = (
        IMPLEMENTATION_SYMBOL[layers[layer]] for layer in CapabilityLayer
    )
    limits = sorted(c.feature for c in capabilities if c.limited_by_ccnl)
    return CoverageCells((gross, net, work), ", ".join(limits) or "—")


def registry_summary(catalog: CapabilityCatalog) -> list[str]:
    """Return the per-layer count of registry capabilities by implementation.

    Returns:
        Markdown table lines, header included.
    """
    header = " | ".join(i.value for i in CapabilityImplementation)
    lines = [f"| Layer | {header} |", "|---|" + "---:|" * len(CapabilityImplementation)]
    for layer in CapabilityLayer:
        counts = Counter(
            e.implementation for e in catalog.capabilities if e.layer is layer
        )
        cells = " | ".join(str(counts[i]) for i in CapabilityImplementation)
        lines.append(f"| {layer.value} | {cells} |")
    return lines


def latest_catalog_year() -> int:
    """Return the latest fiscal year with a bundled capability registry.

    Returns:
        The year of the newest ``capability/<year>/catalog.json``.
    """
    return max(r.year for r in resources("capability") if r.year is not None)


def bundled_ccnls() -> list[CCNL]:
    """Return every bundled CCNL, sorted by name.

    Returns:
        The CCNL models.
    """
    filenames = [r.name for r in resources("contract/agreement")]
    return sorted((load_ccnl(fn) for fn in filenames), key=lambda c: c.meta.name)


@dataclass(frozen=True)
class CCNLCoverageRow:
    """One row in the per-CCNL index table."""

    ccnl_id: str
    cnel_code: str
    name: str
    sector: str
    workers_estimate: str
    agreement_year: str
    """4-digit renewal year, e.g. '2024'. Empty string when not recorded."""
    cells: CoverageCells
    sources: str
    """Payable rules of the file by status: verified / derived / assumed / missing."""
    verification_label: str
    readiness: RulesetReadiness


@dataclass(frozen=True)
class CoverageReport:
    """Aggregated coverage data for the full CCNL bundle."""

    ccnl_rows: list[CCNLCoverageRow]
    registry: list[str]
    generated_at: date


def _verification_label(ccnl: CCNL) -> str:
    vs = ccnl.verification.confidence
    if vs == VerificationStatus.VERIFIED:
        if ccnl.meta.extraction.method == ExtractionMethod.MANUAL:
            return "Expert verified"
        return "Human verified"
    if vs == VerificationStatus.NEEDS_REVIEW:
        return "Needs review"
    return "Machine extracted"


def _sources_by_file() -> dict[str, str]:
    counts: dict[str, Counter[str]] = {}
    for rule in inventory():
        counts.setdefault(rule.file, Counter())[rule.status or "missing"] += 1
    return {
        file: " / ".join(str(bucket[s]) for s in _STATUSES)
        for file, bucket in counts.items()
    }


def build_coverage_report(year: int) -> CoverageReport:
    """Build the index data of every bundled CCNL for the registry of *year*.

    Returns:
        CoverageReport with per-CCNL rows sorted by name.
    """
    catalog = load_capability_catalog(year)
    sources = _sources_by_file()
    rows = [
        CCNLCoverageRow(
            ccnl_id=ccnl.meta.ccnl_id,
            cnel_code=ccnl.meta.cnel_code,
            name=ccnl.meta.name,
            sector=ccnl.meta.sector,
            workers_estimate=ccnl.meta.workers_estimate,
            agreement_year=(ccnl.meta.agreement_date or "")[:4],
            cells=coverage_cells(catalog, ccnl),
            sources=sources.get(f"contract/agreement/{ccnl.meta.ccnl_id}.json", "—"),
            verification_label=_verification_label(ccnl),
            readiness=ccnl.verification.readiness,
        )
        for ccnl in bundled_ccnls()
    ]
    return CoverageReport(
        ccnl_rows=rows,
        registry=registry_summary(catalog),
        generated_at=datetime.now(tz=UTC).date(),
    )


_CONTRACTS_PREAMBLE_TEMPLATE = """\
# CCNL Coverage

{count} contract configurations covering an estimated **16 million employees**[^1]
across private and public sectors -- including ARAN public-sector agreements (funzioni
centrali, locali, sanità, istruzione) and one Presidential Decree (DPR 53/2025[^2]).
Covers 75+ of the ~99 major private-sector CCNLs (>10,000 workers, CNEL II/2024).

→ [Domain: What is a CCNL](../domain/index.md) ·
[Capability matrix](capability-matrix.md)

## Three separate axes

No percentage blends them: a contract can be fully covered and still rest
on unverified sources, or be well sourced and not cleared for production.

- **Coverage (L1, L2, L3):** what the engine computes, derived from the
  capability registry of {year}. A layer shows its weakest capability; the
  [capability matrix](capability-matrix.md) lists each one. **Limits**
  names the capabilities this contract's data leaves partial: a `missing`
  note, or a model limitation with a monetary impact.
- **Sources:** payable rules of the contract file by provenance status,
  verified / derived / assumed / missing.
- **Readiness:** the review tier of the contract ruleset.

Capabilities of the registry by layer and implementation:

{registry}

{legend}
| | Readiness and extraction |
|---|---|
| 🧪 | Exploratory — demo, research, prototyping only |
| 👁 | Reviewed — key values human-verified; use with disclaimer |
| 🏭 | Production — full review, reference case, named owner |
| 🤖 | Machine extracted |
| 🧑 | Human reviewed |

## Matrix
"""

_CONTRACTS_FOOTER = """
[^1]: Estimated represented population. Individual contracts may cover overlapping \
worker populations; figures should not be summed to derive total coverage.
[^2]: DPR 53/2025 -- Compensation for Forze di Polizia ad ordinamento civile is \
set by Presidential Decree, not a CNEL-registered agreement. \
D.P.R. 24 marzo 2025, n. 53 (GU n. 91, 18 April 2025, SO).
[^3]: Approximate estimates. Sources: CNEL, INPS, Ministero del Lavoro, \
CCNL renewal communications.
[^4]: Salary tables extracted from official CCNL documents using AI-assisted \
tooling, no manual human review. Verify against the official source before use \
in production.
"""


def render_contracts_index(report: CoverageReport, year: int) -> str:
    """Render the contracts/index.md page with per-CCNL data and links.

    Returns:
        Markdown string for docs/contracts/index.md.
    """
    auto_header = (
        "<!-- auto-generated"
        " -- run: uv run python scripts/docs/gen_coverage_matrix.py -->\n"
        f"<!-- generated: {report.generated_at} -->\n"
    )
    preamble = _CONTRACTS_PREAMBLE_TEMPLATE.format(
        count=len(report.ccnl_rows),
        year=year,
        registry="\n".join(report.registry),
        legend=IMPLEMENTATION_LEGEND,
    )
    lines: list[str] = [
        auto_header,
        preamble,
        (
            "| # | CNEL | CCNL | Sector | Workers (~)[^3] | Renewal"
            " | L1 | L2 | L3 | Limits | Sources (v / d / a / m)"
            " | Readiness | Ext[^4] |"
        ),
        "|---|---|---|---|---:|:---:|:---:|:---:|:---:|---|---|:---:|:---:|",
    ]
    for i, row in enumerate(report.ccnl_rows, 1):
        l1, l2, l3 = row.cells.layers
        link = f"[{row.name}]({row.ccnl_id}.md)"
        lines.append(
            f"| {i} | {row.cnel_code} | {link} | {row.sector}"
            f" | {row.workers_estimate or '—'} | {row.agreement_year or '—'}"
            f" | {l1} | {l2} | {l3} | {row.cells.limits} | {row.sources}"
            f" | {_READINESS_SYMBOL[row.readiness]}"
            f" | {_VERIFICATION_EMOJI[row.verification_label]} |"
        )
    lines.append(_CONTRACTS_FOOTER)
    return "\n".join(lines)
