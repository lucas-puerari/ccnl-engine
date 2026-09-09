"""Generate one documentation page per CCNL contract from its JSON data.

Run:
    uv run python docs/scripts/gen_contract_pages.py

Each page replaces the raw JSON dump with a structured layout:
  - Header card: CNEL code, sector, renewal, workers, extraction status
  - Coverage badges
  - Salary table (latest tranche per level)
  - Seniority rules
  - Apprenticeship tracks
  - Simplification warnings
  - Sources with links
  - Collapsed raw JSON (provenance artifact, always present)
  - Usage example snippet
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "src" / "ccnl_engine" / "knowledge" / "ccnl" / "data"
OUT_DIR = ROOT / "docs" / "contracts"
TODAY = datetime.datetime.now(tz=datetime.UTC).date().isoformat()

COVERAGE_ICON: dict[str | None, str] = {
    "implemented": "✅",
    "partial": "⚠️",
    "not_implemented": "🔲",
    None: "—",
}

VERIFICATION_BADGE: dict[str, str] = {
    "verified": "🟢 Verified",
    "unverified": "🔴 Unverified",
    "needs_review": "🟡 Needs review",
}

EXTRACTION_BADGE: dict[str, str] = {
    "manual": "🧑 Manual",
    "ai_assisted": "🤖 AI-assisted",
}


def _latest_value(periods: list[dict[str, Any]]) -> str | None:
    """Return the amount from the most recent period in a time-series.

    Returns:
        The ``amount`` or ``value`` from the last period, or ``None`` when
        the periods list is empty.
    """
    if not periods:
        return None
    sorted_periods = sorted(periods, key=lambda p: p.get("from", ""))
    last = sorted_periods[-1]
    return last.get("amount") or last.get("value")


def _latest_date(periods: list[dict[str, Any]]) -> str | None:
    """Return the start date of the most recent period.

    Returns:
        ISO-8601 string from the most recent ``from`` key, or ``None``.
    """
    if not periods:
        return None
    sorted_periods = sorted(periods, key=lambda p: p.get("from", ""))
    return sorted_periods[-1].get("from")


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
    if prow.get("under_level"):
        parts.append(f"under-level: `{prow['under_level']}`")
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
        url = src.get("url", "")
        link = f"[↗]({url})" if url else "—"
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
    extraction = meta.get("extraction") or {}
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
    ext_method = extraction.get("method") or "—"
    ext_status = ruleset.get("verification_status") or "unverified"
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
        f"| **Extraction** | {EXTRACTION_BADGE.get(ext_method, ext_method)} |",
        f"| **Verification** | {VERIFICATION_BADGE.get(ext_status, ext_status)} |",
        "",
        "[← Contracts index](index.md)",
        "",
    ]
    if signatories:
        lines.extend(['??? note "Signatories"'])
        lines.extend([f"    - {sig}" for sig in signatories])
        lines.append("")
    return lines


def _coverage_section(coverage: dict[str, Any]) -> list[str]:
    """Build the coverage table section.

    Returns:
        List of markdown lines.
    """

    def row(label: str, status: str | None) -> str:
        icon = COVERAGE_ICON.get(status, "—")
        return f"| **{label}** | {icon} {status or '—'} |"

    return [
        "## Coverage",
        "",
        "| Layer | Status |",
        "|---|---|",
        row("L1 — Gross", coverage.get("gross")),
        row("L2 — Net", coverage.get("net")),
        row("L3 — Work rules", coverage.get("work_rules")),
        "",
    ]


def _simplification_lines(notes_by_kind: dict[str, list[str]]) -> list[str]:
    """Render simplification warning blocks.

    Returns:
        List of markdown lines for the Known simplifications section.
    """
    simplifications = notes_by_kind.get("simplification", [])
    if not simplifications:
        return []
    lines: list[str] = [
        "## Known simplifications",
        "",
        (
            "These are deliberate modelling approximations. "
            "Read them before using this contract in a sensitive context."
        ),
        "",
    ]
    for text in simplifications:
        lines.append('!!! warning ""')
        lines.extend([f"    {sub}" for sub in text.splitlines()])
        lines.append("")
    return lines


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


def _body_sections(data: dict[str, Any]) -> list[str]:
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

    lines.extend(_simplification_lines(notes_by_kind))

    if sources:
        lines.extend(["## Sources", "", _render_sources(sources), ""])

    lines.extend(_info_notes_lines(notes_by_kind))

    return lines


def _tail_section(ccnl_id: str) -> list[str]:
    """Build the raw-JSON collapse block and optional usage example.

    Returns:
        List of markdown lines.
    """
    lines: list[str] = [
        "## Raw data",
        "",
        '??? note "Full JSON (provenance artifact)"',
        "    ```json",
        f'    --8<-- "src/ccnl_engine/knowledge/ccnl/data/{ccnl_id}.json"',
        "    ```",
        "",
    ]
    example_path = f"docs/examples/contracts/{ccnl_id}.py"
    if (ROOT / example_path).exists():
        lines.extend([
            "## Usage example",
            "",
            "```python",
            f'--8<-- "{example_path}"',
            "```",
            "",
        ])
    return lines


def generate_page(json_path: Path) -> str:
    """Generate a complete markdown contract page from its JSON data file.

    Returns:
        Full markdown content as a string.
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    ccnl_id = json_path.stem

    coverage = data.get("coverage", {})

    lines: list[str] = []
    lines.extend(_header_section(data, ccnl_id))
    lines.extend(_coverage_section(coverage))
    lines.extend(_body_sections(data))
    lines.extend(_tail_section(ccnl_id))

    return "\n".join(lines)


def main() -> None:
    """Generate documentation pages for every existing contract markdown file."""
    json_files = sorted(DATA_DIR.glob("*.json"))
    count = 0
    for json_path in json_files:
        out_path = OUT_DIR / f"{json_path.stem}.md"
        if not out_path.exists():
            continue
        content = generate_page(json_path)
        out_path.write_text(content, encoding="utf-8")
        count += 1
        print(f"  {json_path.stem}")

    print(f"\nGenerated {count} contract pages.")
    print(f"<!-- generated: {TODAY} -->")


if __name__ == "__main__":
    main()
