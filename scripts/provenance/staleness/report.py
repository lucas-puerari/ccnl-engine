"""Report how stale each ruleset of the bundle is, ahead of its deadlines.

The deadline gate (``scripts/provenance/check.py --deadlines``) fails on a
review that is overdue or due soon.  This report looks further, at what
goes stale without any deadline in the data:

- each CCNL: its readiness, ``review_due``, the next pay tranche of its
  tables and the day its tables run out (the last ``valid_until`` of the
  base salaries, when the last period is closed);
- each ruleset with ``effective_until`` in the horizon, or ``provisional``
  while in force;
- each yearly directory (contributions, sectors, surtaxes, tax credits)
  without the file of the year the horizon reaches;
- the municipal surtax, whose rates the MEF republishes every month: a
  file published more than :data:`MUNICIPAL_CADENCE_DAYS` ago is stale.

The report never fails: the weekly job publishes it next to the deadline
gate, which does.  It reads raw JSON with the standard library only.

Run with::

    uv run python scripts/provenance/staleness/report.py [--within DAYS]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.provenance.rules import KNOWLEDGE_DIR

#: Days after which the municipal surtax file is stale (monthly MEF updates).
MUNICIPAL_CADENCE_DAYS: Final = 31
#: Directories that hold one file per year, by year or with one file per sector.
YEARLY: Final = (
    "contribution",
    "sector",
    "surtax/municipal",
    "surtax/regional",
    "tax_credit/somma_esente",
)

Json = dict[str, Any]


@dataclass(frozen=True)
class Finding:
    """One thing of the bundle that is stale or about to be."""

    file: str
    reason: str


def _date(value: object) -> date | None:
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def _in(day: date, today: date, horizon: date) -> bool:
    return today <= day <= horizon


def _periods(data: Json) -> list[Json]:
    levels = data.get("levels")
    return [
        period
        for level in (levels if isinstance(levels, list) else [])
        for period in (level.get("base_salary") or {}).get("periods") or []
    ]


def _agreement(file: str, data: Json, today: date, horizon: date) -> list[Finding]:
    verification = data.get("verification") or {}
    readiness = verification.get("readiness", "exploratory")
    findings: list[Finding] = []
    due = _date(verification.get("review_due"))
    if due is not None and due <= horizon:
        findings.append(Finding(file, f"{readiness}: review due on {due}"))
    periods = _periods(data)
    starts = [
        d
        for p in periods
        if (d := _date(p.get("valid_from"))) is not None and _in(d, today, horizon)
    ]
    if starts:
        findings.append(Finding(file, f"{readiness}: new tranche on {min(starts)}"))
    if periods and all(p.get("valid_until") for p in periods):
        end = max(d for p in periods if (d := _date(p.get("valid_until"))) is not None)
        if end <= horizon:
            findings.append(Finding(file, f"{readiness}: pay tables run out on {end}"))
    return findings


def _ruleset(file: str, data: Json, today: date, horizon: date) -> list[Finding]:
    ruleset = data.get("ruleset")
    if not isinstance(ruleset, dict):
        return []
    findings: list[Finding] = []
    start = _date(ruleset.get("effective_from")) or date.min
    until = _date(ruleset.get("effective_until"))
    if until is not None and until <= horizon:
        findings.append(Finding(file, f"ruleset effective until {until}"))
    if ruleset.get("provisional") and start <= horizon and (until or date.max) >= today:
        findings.append(Finding(file, "provisional ruleset in force"))
    return findings


def _yearly(root: Path, horizon: date) -> list[Finding]:
    findings = []
    for directory in YEARLY:
        base = root / directory
        found = base.iterdir() if base.is_dir() else ()
        years = {int(p.stem) for p in found if p.stem.isdigit()}
        if years and horizon.year not in years:
            findings.append(Finding(directory, f"no data for {horizon.year}"))
    return findings


def _municipal(root: Path, today: date) -> list[Finding]:
    path = root / "surtax" / "municipal" / f"{today.year}.json"
    if not path.exists():
        return []
    data: Json = json.loads(path.read_text(encoding="utf-8"))
    published = _date((data.get("ruleset") or {}).get("published_at"))
    if published is None or (today - published).days <= MUNICIPAL_CADENCE_DAYS:
        return []
    file = path.relative_to(root).as_posix()
    return [
        Finding(file, f"municipal surtax published on {published}, over a month ago")
    ]


def staleness(
    root: Path = KNOWLEDGE_DIR, today: date | None = None, within: int = 60
) -> list[Finding]:
    """Return what in the bundle is stale or goes stale within ``within`` days.

    Returns:
        The findings, by file.
    """
    day = today or datetime.now(tz=UTC).date()
    horizon = day + timedelta(days=within)
    findings: list[Finding] = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        file = path.relative_to(root).as_posix()
        if file.startswith("agreement/"):
            findings += _agreement(file, data, day, horizon)
        findings += _ruleset(file, data, day, horizon)
    findings += _yearly(root, horizon)
    findings += _municipal(root, day)
    return sorted(findings, key=lambda f: (f.file, f.reason))


def render(findings: list[Finding], today: date, within: int) -> str:
    """Render the findings as Markdown.

    Returns:
        A table of the findings, or a line saying there are none.
    """
    title = f"## Staleness on {today}, next {within} days"
    if not findings:
        return f"{title}\n\nNothing stale.\n"
    rows = "\n".join(f"| `{f.file}` | {f.reason} |" for f in findings)
    return f"{title}\n\n| File | Finding |\n|---|---|\n{rows}\n"


def main(argv: list[str] | None = None) -> int:
    """Print the report.

    Returns:
        Always 0: the report informs, the deadline gate fails.
    """
    parser = argparse.ArgumentParser(description="Report the staleness of the bundle.")
    parser.add_argument("--within", type=int, default=60, metavar="DAYS")
    args = parser.parse_args(argv)
    today = datetime.now(tz=UTC).date()
    print(render(staleness(today=today, within=args.within), today, args.within))
    return 0


if __name__ == "__main__":
    sys.exit(main())
