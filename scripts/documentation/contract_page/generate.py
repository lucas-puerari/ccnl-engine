"""Generate one documentation page per CCNL contract from its JSON data.

Run:
    uv run python scripts/documentation/contract_page/generate.py

Check for drift without writing (for CI)::

    uv run python scripts/documentation/contract_page/generate.py --check

The output depends only on the bundle and the committed usage examples, never
on the current date, so a committed page stays valid until its data changes.

Each page replaces the raw JSON dump with a structured layout:
  - Header card: CNEL code, sector, renewal, workers, ruleset version
  - Coverage of the core payroll path and the contract's limits
  - Assurance: the five axes, each with its meaning
  - Freshness and known simplifications
  - Salary table (latest tranche per level)
  - Seniority rules
  - Apprenticeship tracks
  - Known simplifications, generated from the limitation registry
  - Sources with links
  - A link to the contract file in the repository, never its content: the
    full JSON would weigh on every page and on the search index
  - Usage example snippet
"""

from __future__ import annotations

import functools
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.capability.loaders import (
    load_capability_catalog,
)
from scripts.documentation.coverage.loaders import (
    IMPLEMENTATION_LEGEND,
    CoverageCells,
    coverage_cells,
    latest_catalog_year,
)
from scripts.documentation.limitation.generate import limitation_lines
from scripts.provenance.rules import STATUSES, count_by_file, inventory

ROOT = Path(__file__).resolve().parents[3]
#: Where a page links the contract file it is generated from.
REPOSITORY_FILE_URL = (
    "https://github.com/lucas-puerari/ccnl-engine/blob/main/"
    "src/ccnl_engine/knowledge/agreement/{ccnl_id}.json"
)
DATA_DIR = ROOT / "src" / "ccnl_engine" / "knowledge" / "agreement"
OUT_DIR = ROOT / "docs" / "contracts"

VERIFICATION_BADGE: dict[str, str] = {
    "verified": "🟢 Verified",
    "unverified": "🔴 Unverified",
    "needs_review": "🟡 Needs review",
}

READINESS_BADGE: dict[str, str] = {
    "exploratory": "🧪 Exploratory",
    "reviewed": "👁 Reviewed",
    "production": "🏭 Production",
}

EXTRACTION_BADGE: dict[str, str] = {
    "manual": "🧑 Manual",
    "ai": "🤖 AI-assisted",
    "back_calculation": "🔢 Back-calculation",
    "import": "📥 Import",
}


def _latest_value(periods: list[dict[str, Any]]) -> str | None:
    """Return the amount from the most recent period in a time-series.

    Returns:
        The ``amount`` or ``value`` from the last period, or ``None`` when
        the periods list is empty.
    """
    if not periods:
        return None
    sorted_periods = sorted(periods, key=lambda p: p.get("valid_from", ""))
    last = sorted_periods[-1]
    return last.get("amount") or last.get("value")


def _latest_date(periods: list[dict[str, Any]]) -> str | None:
    """Return the start date of the most recent period.

    Returns:
        ISO-8601 string from the most recent ``valid_from`` key, or ``None``.
    """
    if not periods:
        return None
    sorted_periods = sorted(periods, key=lambda p: p.get("valid_from", ""))
    return sorted_periods[-1].get("valid_from")


def _fmt_eur(amount: str | None) -> str:
    """Format a decimal string as EUR with thousands separator.

    Returns:
        Formatted string like ``"€ 1,234.56"`` or ``"—"`` when *amount* is
        ``None`` or not parseable.
    """
    if amount is None:
        return "—"
    try:
        return f"€ {float(amount):,.2f}"
    except (ValueError, TypeError):
        return str(amount)


def _render_salary_table(levels: list[dict[str, Any]]) -> str:
    """Render a markdown table of base salaries per level.

    Returns:
        Markdown table string, or empty string when *levels* is empty.
    """
    rows = []
    for lvl in sorted(levels, key=lambda item: item.get("order", 99), reverse=True):
        code = lvl.get("code", "?")
        desc = lvl.get("description") or ""
        periods = lvl.get("base_salary", {}).get("periods", [])
        amount = _latest_value(periods)
        eff_from = _latest_date(periods)
        rows.append(f"| `{code}` | {desc} | {_fmt_eur(amount)} | {eff_from or '—'} |")
    if not rows:
        return ""
    header = (
        "| Level | Description | Base salary (monthly) | Effective from |\n"
        "|---|---|---:|:---:|"
    )
    return header + "\n" + "\n".join(rows)


def _render_seniority(params: dict[str, Any]) -> str:
    """Render seniority cadence and per-level increment table.

    Returns:
        Markdown string, or empty string when no seniority block is present.
    """
    si = params.get("seniority_increments")
    if not si:
        return ""
    cadence = si.get("cadence_months", "?")
    maximum = si.get("maximum_count", "?")
    lines = [
        f"**Cadence:** every {cadence} months  ",
        f"**Maximum:** {maximum} increments",
    ]
    amounts = si.get("amount_by_level", {})
    if amounts:
        lines.extend([
            "",
            "| Level | Increment (monthly) |",
            "|---|---:|",
        ])
        for lvl_code, val in amounts.items():
            if isinstance(val, dict):
                periods = val.get("periods", [])
                amount = _latest_value(periods)
            else:
                amount = str(val)
            lines.append(f"| `{lvl_code}` | {_fmt_eur(amount)} |")
    return "\n".join(lines)


def _track_params_line(periods: list[Any]) -> str:
    """Extract percentage/under-level params from the last period row.

    Returns:
        A comma-separated params string, or empty string when nothing applies.
    """
    if not periods:
        return ""
    prow = periods[-1]
    parts = []
    if prow.get("percentage"):
        parts.append(f"percentage: {prow['percentage']}")
    if prow.get("levels_below"):
        parts.append(f"under-level: `{prow['levels_below']}`")
    return ", ".join(parts)


def _render_one_track(track: dict[str, Any]) -> str:
    """Render a single apprenticeship track block.

    Returns:
        Markdown block for this track.
    """
    track_type = track.get("type", "?")
    name = track.get("name", "")
    dest = track.get("destination_levels", [])
    dest_str = ", ".join(f"`{d}`" for d in dest) if dest else "—"
    header = f"**{name or track_type}** (type: `{track_type}`)"
    if dest:
        header += f"  \nDestination levels: {dest_str}"
    params = _track_params_line(track.get("periods", []))
    if params:
        header += f"  \n{params}"
    return header


def _render_apprenticeship(tracks: list[dict[str, Any]]) -> str:
    """Render apprenticeship track descriptions.

    Returns:
        Markdown string with one block per track.
    """
    if not tracks:
        return "_No apprenticeship track defined._"
    return "\n\n".join(_render_one_track(t) for t in tracks)


def _render_sources(sources: list[dict[str, Any]]) -> str:
    """Render a sources table with links.

    Returns:
        Markdown table string.
    """
    if not sources:
        return "_No sources recorded._"
    rows = ["| Document | Kind | Date | URL |", "|---|---|---|---|"]
    for src in sources:
        title = src.get("title") or src.get("document_id", "—")
        kind = src.get("kind", "—")
        pub = src.get("published_on") or src.get("agreement_date") or "—"
        url = str(src.get("url") or "")
        # Only a public HTTP address is a link: a local file name or the
        # "unavailable" placeholder is not reachable from the site.
        public = url.startswith(("http://", "https://"))
        link = f"[↗]({url})" if public else "not available"
        rows.append(f"| {title} | {kind} | {pub} | {link} |")
    return "\n".join(rows)


def _group_notes(notes: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Group coverage notes by kind.

    Returns:
        Mapping of note kind to list of text strings.
    """
    groups: dict[str, list[str]] = {}
    for note in notes:
        kind = note.get("kind", "info")
        groups.setdefault(kind, []).append(note.get("text", ""))
    return groups


def _header_section(data: dict[str, Any], ccnl_id: str) -> list[str]:
    """Build the page header: title, metadata card, back link, signatories.

    Returns:
        List of markdown lines.
    """
    meta = data.get("meta", {})
    ruleset = data.get("ruleset", {})
    sources = meta.get("sources") or []

    name = meta.get("name", ccnl_id)
    cnel = meta.get("cnel_code", "—")
    sector = meta.get("sector", "—")
    tax_sector = meta.get("tax_sector", "—")
    workers = meta.get("workers_estimate", "—")
    agreement_date = (
        meta.get("agreement_date")
        or (sources[0].get("published_on") if sources else None)
        or "—"
    )
    ruleset_version = ruleset.get("version") or ruleset.get("id") or "—"
    verification = data.get("verification", {})
    readiness = verification.get("readiness", "exploratory")
    signatories = meta.get("signatories") or []

    lines: list[str] = [
        f"# {name}",
        "",
        "| | |",
        "|---|---|",
        f"| **CNEL code** | `{cnel}` |",
        f"| **Sector** | {sector} |",
        f"| **Tax sector** | `{tax_sector}` |",
        f"| **Last renewal** | {agreement_date} |",
        f"| **Workers (est.)** | {workers} |",
        f"| **Ruleset version** | `{ruleset_version}` |",
        f"| **Readiness** | {READINESS_BADGE.get(readiness, readiness)} |",
        "",
        "[← Contracts index](index.md)",
        "",
    ]
    if signatories:
        lines.extend(['??? note "Signatories"'])
        lines.extend([f"    - {sig}" for sig in signatories])
        lines.append("")
    return lines


def _latest_salary_tranche(levels: list[dict[str, Any]]) -> str:
    """Return the latest salary tranche start date across all levels.

    Returns:
        ISO-8601 date string, or '—' when no tranche is recorded.
    """
    starts: list[str] = []
    for level in levels:
        bs = level.get("base_salary") or {}
        periods = bs.get("periods", []) if isinstance(bs, dict) else []
        starts.extend(p["valid_from"] for p in periods if p.get("valid_from"))
    return max(starts) if starts else "—"


@functools.cache
def _rule_counts() -> dict[str, dict[str, int]]:
    """Return the payable rules of each data file by provenance status.

    Returns:
        :func:`scripts.provenance.rules.count_by_file` of the bundle.
    """
    return count_by_file(inventory())


def _provenance_cell(ccnl_id: str) -> str:
    """Return the payable rules of a contract file by provenance status.

    Returns:
        ``verified / derived / assumed / missing`` counts, ``—`` when the
        file holds no payable rule.
    """
    counts = _rule_counts().get(f"agreement/{ccnl_id}.json")
    if not counts:
        return "—"
    return " / ".join(f"{counts[status]} {status}" for status in STATUSES)


def _coverage_lines(cells: CoverageCells) -> list[str]:
    """Build the coverage table of the core payroll path and the limits.

    Returns:
        Markdown lines, from the section heading to a blank line.
    """
    return [
        "## Coverage",
        "",
        (
            "Derived from the capability registry. The scenario features and"
            " the ones outside the input are the same for every contract: see"
            " the [capability matrix](capability-matrix.md)."
        ),
        "",
        IMPLEMENTATION_LEGEND,
        "| | |",
        "|---|---|",
        f"| **Core payroll path** | {cells.core} |",
        f"| **Limits of this contract** | {cells.limits} |",
        "",
    ]


def _assurance_lines(data: dict[str, Any], ccnl_id: str) -> list[str]:
    """Build the five assurance axes, each with what it says.

    The axes are independent: an AI-assisted extraction can feed a reviewed
    ruleset, and verified rules can sit in an exploratory one.

    Returns:
        Markdown lines, from the section heading to a blank line.
    """
    verification = data.get("verification", {})
    extraction = data.get("meta", {}).get("extraction") or {}
    method = extraction.get("method") or "—"
    review = data.get("ruleset", {}).get("verification_status") or "unverified"
    confidence = verification.get("confidence", "unverified")
    readiness = verification.get("readiness", "exploratory")
    return [
        "## Assurance",
        "",
        "| Axis | Value | What it says |",
        "|---|---|---|",
        (
            f"| **Extraction method** | {EXTRACTION_BADGE.get(method, method)}"
            " | How the values were read from the sources |"
        ),
        (
            f"| **Extraction review** | {VERIFICATION_BADGE.get(review, review)}"
            " | Whether a person checked the extracted file against its sources |"
        ),
        (
            f"| **Rule provenance** | {_provenance_cell(ccnl_id)}"
            " | Payable rules of the file by the evidence behind each value"
            " ([statuses](../trust/provenance.md)) |"
        ),
        (
            "| **Ruleset confidence** |"
            f" {VERIFICATION_BADGE.get(confidence, confidence)}"
            " | The confidence the ruleset declares as a whole |"
        ),
        (
            f"| **Readiness** | {READINESS_BADGE.get(readiness, readiness)}"
            " | Whether runs of this contract can be paid in `operational` mode"
            " ([tiers](../trust/readiness.md)) |"
        ),
        "",
    ]


def _freshness_lines(
    verification: dict[str, Any],
    meta: dict[str, Any],
    levels: list[dict[str, Any]],
) -> list[str]:
    """Build the freshness table.

    Returns:
        Markdown lines, from the section heading to a blank line.
    """
    last_reviewed = verification.get("last_reviewed") or "—"
    sources = meta.get("sources") or []
    agreement_date = (
        meta.get("agreement_date")
        or (sources[0].get("published_on") if sources else None)
        or "—"
    )
    return [
        "## Freshness",
        "",
        "| | |",
        "|---|---|",
        f"| **Last renewal** | {agreement_date} |",
        f"| **Last human review** | {last_reviewed} |",
        f"| **Latest salary tranche** | {_latest_salary_tranche(levels)} |",
        "",
    ]


def _simplification_summary(notes: list[dict[str, Any]]) -> list[str]:
    """Summarise the simplification and missing-feature note counts.

    Returns:
        List of markdown lines, ending with a blank line.
    """
    simplifications = sum(1 for n in notes if n.get("kind") == "simplification")
    missing = sum(1 for n in notes if n.get("kind") == "missing")
    return [
        (
            f"{simplifications} documented simplification(s) and {missing}"
            " missing feature(s): see [Known simplifications](#known-simplifications)."
        ),
        "",
    ]


def _coverage_section(
    cells: CoverageCells,
    data: dict[str, Any],
    ccnl_id: str,
) -> list[str]:
    """Build coverage, assurance and freshness.

    Returns:
        List of markdown lines.
    """
    meta = data.get("meta", {})
    notes = data.get("coverage", {}).get("notes") or []
    return [
        *_coverage_lines(cells),
        *_simplification_summary(notes),
        *_assurance_lines(data, ccnl_id),
        *_freshness_lines(data.get("verification", {}), meta, data.get("levels", [])),
    ]


def _info_notes_lines(notes_by_kind: dict[str, list[str]]) -> list[str]:
    """Render the collapsed coverage-notes block.

    Returns:
        List of markdown lines, or empty list when there are no info notes.
    """
    info_notes = notes_by_kind.get("info", []) + notes_by_kind.get("source", [])
    if not info_notes:
        return []
    lines: list[str] = ['??? note "Coverage notes"']
    for text in info_notes:
        lines.extend([f"    {sub}" for sub in text.splitlines()])
        lines.append("    ")
    lines.append("")
    return lines


def _body_sections(data: dict[str, Any], ccnl: CCNL) -> list[str]:
    """Build salary, seniority, apprenticeship, simplifications, sources, notes.

    Returns:
        List of markdown lines.
    """
    params = data.get("parameters", {})
    levels = data.get("levels", [])
    apprenticeship = data.get("apprenticeship", [])
    sources = data.get("meta", {}).get("sources") or []
    notes_by_kind = _group_notes(data.get("coverage", {}).get("notes") or [])

    lines: list[str] = []

    salary_table = _render_salary_table(levels) if levels else ""
    if salary_table:
        lines.extend([
            "## Salary table",
            "",
            "Latest effective values per level (monthly gross, EUR).",
            "",
            salary_table,
            "",
        ])

    seniority_block = _render_seniority(params)
    if seniority_block:
        lines.extend(["## Seniority increments", "", seniority_block, ""])

    if apprenticeship:
        lines.extend([
            "## Apprenticeship",
            "",
            _render_apprenticeship(apprenticeship),
            "",
        ])

    lines.extend(limitation_lines(ccnl))

    if sources:
        lines.extend(["## Sources", "", _render_sources(sources), ""])

    lines.extend(_info_notes_lines(notes_by_kind))

    return lines


def _tail_section(ccnl_id: str, root: Path) -> list[str]:
    """Build the link to the contract file and the optional usage example.

    Returns:
        List of markdown lines.
    """
    url = REPOSITORY_FILE_URL.format(ccnl_id=ccnl_id)
    lines: list[str] = [
        "## Raw data",
        "",
        (
            "The contract file this page is generated from:"
            f" [`agreement/{ccnl_id}.json`]({url})."
        ),
        "",
    ]
    example_path = f"docs/examples/agreement/{ccnl_id}/example.py"
    if (root / example_path).exists():
        lines.extend([
            "## Usage example",
            "",
            "```python",
            f'--8<-- "{example_path}"',
            "```",
            "",
        ])
    return lines


def generate_page(json_path: Path, root: Path = ROOT) -> str:
    """Generate a complete markdown contract page from its JSON data file.

    Args:
        json_path: CCNL JSON file.
        root: Repository root, used to find the committed usage example.

    Returns:
        Full markdown content as a string.
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    ccnl_id = json_path.stem

    lines: list[str] = []
    lines.extend(_header_section(data, ccnl_id))
    catalog = load_capability_catalog(latest_catalog_year())
    ccnl = CCNL.model_validate(data)
    cells = coverage_cells(catalog, ccnl)
    lines.extend(_coverage_section(cells, data, ccnl_id))
    lines.extend(_body_sections(data, ccnl))
    lines.extend(_tail_section(ccnl_id, root))

    return "\n".join(lines)


def expected_pages(data_dir: Path, root: Path) -> dict[str, str]:
    """Render the page of every CCNL JSON file in *data_dir*.

    Returns:
        Mapping of page file name (``<ccnl_id>.md``) to its content.
    """
    return {
        f"{path.stem}.md": generate_page(path, root)
        for path in sorted(data_dir.glob("*.json"))
    }


def drifted_pages(pages: dict[str, str], out_dir: Path) -> list[str]:
    """Compare rendered pages with the committed ones without writing.

    Returns:
        Sorted names of pages that are missing or differ from *pages*.
    """
    drifted: list[str] = []
    for name, content in pages.items():
        page = out_dir / name
        if not page.exists() or page.read_text(encoding="utf-8") != content:
            drifted.append(name)
    return sorted(drifted)


def main(
    argv: list[str] | None = None,
    *,
    data_dir: Path = DATA_DIR,
    out_dir: Path = OUT_DIR,
    root: Path = ROOT,
) -> int:
    """Write every contract page, or check them for drift with ``--check``.

    Returns:
        Process exit code: 1 when ``--check`` finds a missing or stale page.
    """
    args = sys.argv[1:] if argv is None else argv
    pages = expected_pages(data_dir, root)
    if "--check" in args:
        drifted = drifted_pages(pages, out_dir)
        if drifted:
            print("Contract pages out of date:", file=sys.stderr)
            print("\n".join(f"  {name}" for name in drifted), file=sys.stderr)
            print(
                "Run: uv run python scripts/documentation/contract_page/generate.py",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {len(pages)} contract pages are up to date.")
        return 0
    for name, content in pages.items():
        (out_dir / name).write_text(content, encoding="utf-8")
    print(f"Generated {len(pages)} contract pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
