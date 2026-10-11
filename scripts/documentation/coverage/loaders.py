"""CCNL coverage data for the contracts index and the capability matrix.

Every coverage cell comes from one derivation: the capability registry of
the fiscal year, lowered for a CCNL by the ``missing`` notes of its file
(``ccnl_engine.capability.support.services``).  The index and the
matrix render the same :func:`coverage_cells`, so they cannot disagree.

Functional coverage, source quality and readiness are three separate axes;
no percentage blends them.

Not part of the engine API -- documentation tooling only.
Regenerate output files with::

    uv run python scripts/documentation/coverage_matrix/generate.py
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from ccnl_engine.bundle.loaders import resources
from ccnl_engine.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.capability.registry.models import (
    CapabilityApplicability,
    CapabilityImplementation,
)
from ccnl_engine.capability.support.services import ccnl_capabilities
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from ccnl_engine.provenance.source.extraction.models import ExtractionMethod
from scripts.provenance.rules import inventory

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.capability.registry.models import (
        CapabilityCatalog,
        CapabilityEntry,
    )

#: Symbol of each implementation, shared by the index and the matrix.
IMPLEMENTATION_SYMBOL: dict[CapabilityImplementation, str] = {
    CapabilityImplementation.NATIVE: "✅",
    CapabilityImplementation.CALLER_SUPPLIED: "📝",
    CapabilityImplementation.PARTIAL: "⚠️",
    CapabilityImplementation.UNSUPPORTED: "🔲",
}

IMPLEMENTATION_LEGEND = """\
| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |
"""

#: Scope of a capability on the pages, in display order.
SCOPES = ("core", "scenario", "outside_input")

_SCOPE_TITLE = {
    "core": "Core payroll path: computed on every run of every contract",
    "scenario": (
        "Scenario features: computed when the request declares the event,"
        " the fact or the termination"
    ),
    "outside_input": (
        "Outside the input: the request has no field for the fact,"
        " so the engine does not compute them"
    ),
}

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
    """Functional coverage of one CCNL as rendered on every page.

    Only what differs between contracts is a cell: the scenario features and
    the ones outside the input are the same for every contract and are shown
    once, by :func:`scope_summary`.

    Attributes:
        core: Symbol of the core payroll path for this contract.
        limits: Capabilities the contract's data leave partial (a
            ``missing`` note or a blocking limitation), comma separated;
            ``—`` when none.
    """

    core: str
    limits: str


def capability_scope(entry: CapabilityEntry) -> str:
    """Return the scope of a registry capability.

    A capability every run computes or decides, natively in the registry, is
    core. One the request has no field for is outside the input. The others
    apply in some scenarios: an event, a termination, or a decided capability
    the engine covers only in part (a foreign tax credit, a pension fund).

    Returns:
        One of :data:`SCOPES`.
    """
    if entry.applies_when is CapabilityApplicability.OUTSIDE_INPUT:
        return "outside_input"
    if entry.applies_when is CapabilityApplicability.ALWAYS or (
        entry.applies_when is CapabilityApplicability.DECIDED
        and entry.implementation is CapabilityImplementation.NATIVE
    ):
        return "core"
    return "scenario"


def coverage_cells(catalog: CapabilityCatalog, ccnl: CCNL) -> CoverageCells:
    """Return the functional coverage cells of *ccnl*.

    Returns:
        The symbol of the core path and the CCNL-specific limits.
    """
    capabilities = ccnl_capabilities(catalog, ccnl)
    scopes = {entry.feature: capability_scope(entry) for entry in catalog.capabilities}
    core = CapabilityImplementation.worst(
        c.implementation for c in capabilities if scopes[c.feature] == "core"
    )
    limits = sorted(c.feature for c in capabilities if c.limited_by_ccnl)
    return CoverageCells(IMPLEMENTATION_SYMBOL[core], ", ".join(limits) or "—")


def scope_summary(catalog: CapabilityCatalog) -> list[str]:
    """Return the registry capabilities by scope, the same for every contract.

    Returns:
        Markdown lines: one paragraph and capability list per scope.
    """
    lines: list[str] = []
    for scope in SCOPES:
        entries = [e for e in catalog.capabilities if capability_scope(e) == scope]
        lines.extend([f"**{_SCOPE_TITLE[scope]}** ({len(entries)}):", ""])
        lines.extend(
            f"- {IMPLEMENTATION_SYMBOL[e.implementation]} `{e.feature}`"
            f" ({e.implementation.value})"
            for e in entries
        )
        lines.append("")
    return lines


def registry_summary(catalog: CapabilityCatalog) -> list[str]:
    """Return the count of registry capabilities by scope and implementation.

    Returns:
        Markdown table lines, header included.
    """
    header = " | ".join(i.value for i in CapabilityImplementation)
    lines = [f"| Scope | {header} |", "|---|" + "---:|" * len(CapabilityImplementation)]
    for scope in SCOPES:
        counts = Counter(
            e.implementation
            for e in catalog.capabilities
            if capability_scope(e) == scope
        )
        cells = " | ".join(str(counts[i]) for i in CapabilityImplementation)
        lines.append(f"| {scope} | {cells} |")
    return lines


def latest_catalog_year() -> int:
    """Return the latest fiscal year with a bundled capability registry.

    Returns:
        The year of the newest ``capability/registry/<year>.json``.
    """
    return max(r.year for r in resources("capability/registry") if r.year is not None)


def bundled_ccnls() -> list[CCNL]:
    """Return every bundled CCNL, sorted by name.

    Returns:
        The CCNL models.
    """
    filenames = [r.name for r in resources("agreement")]
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
    """Markdown lines of :func:`scope_summary`."""
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
            sources=sources.get(f"agreement/{ccnl.meta.ccnl_id}.json", "—"),
            verification_label=_verification_label(ccnl),
            readiness=ccnl.verification.readiness,
        )
        for ccnl in bundled_ccnls()
    ]
    return CoverageReport(
        ccnl_rows=rows,
        registry=scope_summary(catalog),
        generated_at=datetime.now(tz=UTC).date(),
    )


_CONTRACTS_PREAMBLE_TEMPLATE = """\
# CCNL Coverage

{count} bundled contract configurations, private and public sector,
including ARAN public-sector agreements and one Presidential Decree
(DPR 53/2025[^2]). The table is generated from the data: search it, or use
`search_ccnls()` from Python.

→ [Domain: What is a CCNL](../domain/index.md) ·
[Capability matrix](capability-matrix.md)

## Three separate axes

No percentage blends them: a contract can be fully covered and still rest
on unverified sources, or be well sourced and not cleared for production.

- **Coverage:** what the engine computes, from the capability registry of
  {year}. **Core** is the path every run takes; **Limits** names the
  capabilities this contract's data leave partial (a `missing` note, or a
  model limitation with a monetary impact). The scenario features and the
  ones outside the input are the same for every contract and are listed
  below.
- **Sources:** payable rules of the contract file by provenance status,
  verified / derived / assumed / missing.
- **Readiness:** the review tier of the contract ruleset.

{scopes}
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
[^2]: DPR 53/2025 -- Compensation for Forze di Polizia ad ordinamento civile is \
set by Presidential Decree, not a CNEL-registered agreement. \
D.P.R. 24 marzo 2025, n. 53 (GU n. 91, 18 April 2025, SO).
[^3]: Approximate estimates of the represented population. Contracts can \
cover overlapping populations, so the figures do not add up. Sources: CNEL, \
INPS, Ministero del Lavoro, CCNL renewal communications.
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
        " -- run: uv run python scripts/documentation/coverage_matrix/generate.py -->\n"
        f"<!-- generated: {report.generated_at} -->\n"
    )
    preamble = _CONTRACTS_PREAMBLE_TEMPLATE.format(
        count=len(report.ccnl_rows),
        year=year,
        scopes="\n".join(report.registry),
        legend=IMPLEMENTATION_LEGEND,
    )
    lines: list[str] = [
        auto_header,
        preamble,
        (
            "| # | CNEL | CCNL | Sector | Workers (~)[^3] | Renewal"
            " | Core | Limits | Sources (v / d / a / m)"
            " | Readiness | Ext[^4] |"
        ),
        "|---|---|---|---|---:|:---:|:---:|---|---|:---:|:---:|",
    ]
    for i, row in enumerate(report.ccnl_rows, 1):
        link = f"[{row.name}]({row.ccnl_id}.md)"
        lines.append(
            f"| {i} | {row.cnel_code} | {link} | {row.sector}"
            f" | {row.workers_estimate or '—'} | {row.agreement_year or '—'}"
            f" | {row.cells.core} | {row.cells.limits} | {row.sources}"
            f" | {_READINESS_SYMBOL[row.readiness]}"
            f" | {_VERIFICATION_EMOJI[row.verification_label]} |"
        )
    lines.append(_CONTRACTS_FOOTER)
    return "\n".join(lines)
