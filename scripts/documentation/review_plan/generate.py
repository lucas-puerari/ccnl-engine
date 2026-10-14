"""Regenerate docs/trust/review-plan.md: the CCNLs still to review, by group.

The CCNLs of one tax sector share its INPS and tax rules, so a group is a
sector: verifying the shared rules once covers every CCNL of the group, and
one CCNL reviewed in full anchors the group before rules derived from the
same source are promoted for the others.  Groups are ordered by the workers
they cover, then by their weak rules; within a group the CCNLs follow the
same order.  A CCNL whose main source is an aggregator (a paid or unofficial
table service) is listed as such: its rules are the first to re-source.

Run with::

    uv run python scripts/documentation/review_plan/generate.py

Check for drift without writing (for CI)::

    uv run python scripts/documentation/review_plan/generate.py --check
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.provenance.rules import KNOWLEDGE_DIR, inventory

ROOT = Path(__file__).resolve().parents[3]
PAGE = ROOT / "docs" / "trust" / "review-plan.md"
#: The CCNLs of the first review round (TODO P1), the anchor of their group.
FIRST_ROUND = frozenset({
    "metalmeccanico-federmeccanica",
    "commercio-confcommercio",
    "edilizia-ance",
    "operai-agricoli-florovivaisti",
    "funzioni-centrali-aran",
    "lavoro-domestico-non-convivente",
    "bancari-abi",
    "logistica-trasporto-confetra",
    "sanita-privata-aiop-aris",
    "metalmeccanico-artigianato",
})
#: Hosts of table services that are neither a contracting party nor an
#: official body.
AGGREGATORS = frozenset({
    "contratticcnl.it",
    "direzionelavoro.it",
    "dottrinalavoro.it",
    "ilccnl.it",
    "kitech.it",
    "lavoro-economia.it",
    "lawinsider.com",
    "leggeinchiaro.it",
    "lexplain.it",
    "consulenza.it",
    "mysolution.it",
    "wolterskluwer.it",
})
_WORKERS = re.compile(r"(\d+(?:[.,]\d+)?)\s*([kKmM]?)")


@dataclass(frozen=True)
class Agreement:
    """One CCNL of the plan.

    Attributes:
        slug: File name without extension.
        sector: Tax sector.
        workers: Estimated workers covered, 0 when not stated.
        readiness: Readiness tier, ``exploratory`` when not stated.
        review_due: Next review date, ``None`` when not set.
        aggregator: Whether the main source is an aggregator.
        weak: Payable rules ``assumed`` or ``missing``.
        derived: Payable rules ``derived``.
        verified: Payable rules ``verified``.
    """

    slug: str
    sector: str
    workers: int
    readiness: str
    review_due: str | None
    aggregator: bool
    weak: int
    derived: int
    verified: int


def workers(text: object) -> int:
    """Return the number of workers of an estimate such as ``~120k``.

    Returns:
        The estimate as an integer, 0 when it cannot be read.
    """
    match = _WORKERS.search(str(text or "").replace(" ", ""))
    if match is None:
        return 0
    value = float(match.group(1).replace(",", "."))
    unit = {"k": 1_000, "m": 1_000_000}.get(match.group(2).lower(), 1)
    return int(value * unit)


def _host(data: dict[str, Any]) -> str:
    sources = data["meta"].get("sources") or []
    if not sources:
        return ""
    host = urlparse(str(sources[0]["url"])).netloc.lower()
    return host.removeprefix("www.")


def agreements() -> list[Agreement]:
    """Return every bundled CCNL with its rule counts.

    Returns:
        The agreements, in file order.
    """
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for rule in inventory():
        if rule.file.startswith("agreement/") and rule.status is not None:
            counts[Path(rule.file).stem][rule.status] += 1
    result = []
    for path in sorted((KNOWLEDGE_DIR / "agreement").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        verification = data.get("verification") or {}
        tally = counts[path.stem]
        result.append(
            Agreement(
                slug=path.stem,
                sector=data["meta"]["tax_sector"],
                workers=workers(data["meta"].get("workers_estimate")),
                readiness=verification.get("readiness", "exploratory"),
                review_due=verification.get("review_due"),
                aggregator=_host(data) in AGGREGATORS,
                weak=tally["assumed"] + tally["missing"],
                derived=tally["derived"],
                verified=tally["verified"],
            )
        )
    return result


_SCRIPT = "scripts/documentation/review_plan/generate.py"
_GROUP_HEADER = (
    "| Group | CCNLs | Workers | Weak | Derived | Verified | Aggregator | Anchor |"
)
_CCNL_HEADER = (
    "| CCNL | Workers | Readiness | Weak | Derived | Verified | Source | Next review |"
)


def _order(agreement: Agreement) -> tuple[int, int, str]:
    return (-agreement.workers, -agreement.weak, agreement.slug)


def _thousands(value: int) -> str:
    return f"{value:,}".replace(",", " ") if value else "none"


def build_page(items: list[Agreement]) -> str:
    """Render the review plan.

    Returns:
        The Markdown page.
    """
    groups: dict[str, list[Agreement]] = defaultdict(list)
    for item in items:
        groups[item.sector].append(item)
    ordered = sorted(
        groups.items(),
        key=lambda kv: (
            -sum(a.workers for a in kv[1]),
            -sum(a.weak for a in kv[1]),
            kv[0],
        ),
    )
    lines = [
        f"<!-- auto-generated; run: uv run python {_SCRIPT} -->",
        "",
        "# Review plan",
        "",
        (
            "The CCNLs of one tax sector share its INPS and tax rules, so the plan "
            "groups them by sector: the shared rules are verified once for the "
            "group, and the CCNL of the first review round anchors it. Before "
            "rules derived from the same source are promoted for the other CCNLs "
            "of a group, at least one more CCNL of the group is reviewed in full."
        ),
        "",
        (
            "Groups are ordered by the workers they cover, then by their weak "
            "(`assumed` or `missing`) rules; the CCNLs within a group follow the "
            "same order. *Aggregator* marks a CCNL whose main source is a table "
            "service rather than a contracting party or an official body: its "
            "rules are the first to re-source. Workers is the estimate each CCNL "
            "file declares: the CCNLs of one comparto (such as the four "
            "Istruzione e Ricerca sections) repeat its figure, so a group total "
            "overstates the workers and serves only to rank the groups."
        ),
        "",
        _GROUP_HEADER,
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for sector, members in ordered:
        anchors = sorted(a.slug for a in members if a.slug in FIRST_ROUND)
        lines.append(
            f"| {sector} | {len(members)} | "
            f"{_thousands(sum(a.workers for a in members))} | "
            f"{sum(a.weak for a in members)} | {sum(a.derived for a in members)} | "
            f"{sum(a.verified for a in members)} | "
            f"{sum(a.aggregator for a in members)} | "
            f"{', '.join(f'`{a}`' for a in anchors) or 'none'} |"
        )
    for sector, members in ordered:
        lines += [
            "",
            f"## {sector}",
            "",
            _CCNL_HEADER,
            "|---|---:|---|---:|---:|---:|---|---|",
        ]
        for item in sorted(members, key=_order):
            name = f"[`{item.slug}`](../contracts/{item.slug}.md)"
            if item.slug in FIRST_ROUND:
                name += " (anchor)"
            source = "aggregator" if item.aggregator else "party or official"
            lines.append(
                f"| {name} | {_thousands(item.workers)} | {item.readiness} | "
                f"{item.weak} | {item.derived} | {item.verified} | {source} | "
                f"{item.review_due or 'none'} |"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Write the page, or check it with ``--check``.

    Returns:
        The exit code.
    """
    page = build_page(agreements())
    if "--check" in argv:
        if PAGE.read_text(encoding="utf-8") != page:
            print("docs/trust/review-plan.md is out of date.", file=sys.stderr)
            return 1
        print("OK: docs/trust/review-plan.md is up to date.")
        return 0
    PAGE.write_text(page, encoding="utf-8")
    print(f"Written {PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
