"""Regenerate the bundle counts quoted in ``docs/trust/``.

Every number the trust pages state about the bundle (ruleset readiness,
provenance statuses, reference cases, model limitations) sits between two markers and is
rendered from the data, never written by hand::

    <!-- trust:NAME -->...<!-- /trust:NAME -->

Run with::

    uv run python scripts/documentation/generate_trust_counts.py

Check for drift without writing (for CI)::

    uv run python scripts/documentation/generate_trust_counts.py --check

The check also fails on a marker with an unknown name and on a count that no
page quotes any more, so a deleted marker cannot hide a stale number.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.identity.facade import NoteKind
from ccnl_engine.knowledge.limitation.loaders import load_engine_limitations
from ccnl_engine.knowledge.limitation.models import LimitationTrigger
from ccnl_engine.knowledge.loaders_manifest import resources
from ccnl_engine.provenance.ruleset.models import (
    RulesetReadiness,
    VerificationStatus,
)
from scripts.provenance import check as check_provenance
from scripts.provenance import rules as payable_rules

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.contract.identity.facade import CCNL

ROOT = Path(__file__).resolve().parents[2]
TRUST_DIR = ROOT / "docs" / "trust"
MARKER_RE = re.compile(
    r"<!-- trust:(?P<name>[a-z0-9-]+) -->(?P<body>.*?)<!-- /trust:(?P=name) -->",
    re.DOTALL,
)


def _n(count: int) -> str:
    """Format *count* with a space as thousands separator, as the docs do.

    Returns:
        The formatted count, e.g. ``"5 705"``.
    """
    return f"{count:,}".replace(",", " ")


def _bundled_ccnls() -> list[CCNL]:
    return [load_ccnl(r.name) for r in resources("contract/agreement")]


def _readiness_counts(ccnls: list[CCNL]) -> dict[str, str]:
    """Render the readiness distribution of the bundled CCNL rulesets.

    Returns:
        Snippets keyed by marker name.
    """
    counts = Counter(c.verification.readiness for c in ccnls)
    rows = [f"| `{tier.value}` | {counts[tier]} |" for tier in RulesetReadiness]
    table = "\n".join(["| Readiness | CCNL rulesets |", "|---|---:|", *rows])
    reviewed = sorted(
        c.meta.ccnl_id
        for c in ccnls
        if c.verification.readiness is RulesetReadiness.REVIEWED
    )
    names = ", ".join(f"`{ccnl_id}`" for ccnl_id in reviewed) or "none"
    return {
        "ccnl-total": str(len(ccnls)),
        "readiness-table": f"\n\n{table}\n\n",
        "readiness-reviewed": str(len(reviewed)),
        "readiness-production": str(counts[RulesetReadiness.PRODUCTION]),
        "readiness-reviewed-list": names,
    }


def _review_record_counts(ccnls: list[CCNL]) -> dict[str, str]:
    """Count the review records of the ``reviewed`` rulesets.

    Returns:
        Snippets keyed by marker name.
    """
    reviewed = [
        c.verification
        for c in ccnls
        if c.verification.readiness is RulesetReadiness.REVIEWED
    ]
    recorded = sum(1 for v in reviewed if v.human_reviewed_by and v.last_reviewed)
    confirmed = sum(1 for v in reviewed if v.confidence is VerificationStatus.VERIFIED)
    return {
        "reviewed-with-reviewer": str(recorded),
        "reviewed-confidence-verified": str(confirmed),
    }


def _provenance_counts(rules: tuple[payable_rules.PayableRule, ...]) -> dict[str, str]:
    """Render the provenance statuses of the payable rules.

    Returns:
        Snippets keyed by marker name.
    """
    ccnl = Counter(r.status for r in rules if r.file.startswith("ccnl/"))
    fiscal = Counter(r.status for r in rules if not r.file.startswith("ccnl/"))
    rows = [
        f"| `{s}` | {_n(ccnl[s])} | {_n(fiscal[s])} | {_n(ccnl[s] + fiscal[s])} |"
        for s in payable_rules.STATUSES
    ]
    header = ["| Status | CCNL rules | Fiscal blocks | Total |", "|---|---:|---:|---:|"]
    accrual = Counter(r.status for r in rules if r.path == "accrual_rule")
    extra_months = {r.file for r in rules if r.path.startswith("additional_months")}
    extra_assumed = {
        r.file
        for r in rules
        if r.path.startswith("additional_months") and r.status == "assumed"
    }
    return {
        "provenance-table": "\n\n" + "\n".join([*header, *rows]) + "\n\n",
        "rules-verified": str(ccnl["verified"] + fiscal["verified"]),
        "rules-missing": str(ccnl["missing"] + fiscal["missing"]),
        "accrual-missing": str(accrual["missing"]),
        "accrual-assumed": str(accrual["assumed"]),
        "extra-months-assumed": f"{len(extra_assumed)} of {len(extra_months)}",
    }


def _reference_case_counts() -> dict[str, str]:
    """Count the reference cases by verification status.

    Returns:
        Snippets keyed by marker name.
    """
    paths = sorted(check_provenance.CASES_DIR.glob("*.json"))
    _, counts = check_provenance.check(paths, mode="all", base="HEAD")
    return {
        "reference-cases": str(sum(counts.values())),
        "reference-cases-source-linked": str(counts["source_linked"]),
        "reference-cases-verified": str(counts["verified"]),
    }


def _limitation_counts(ccnls: list[CCNL]) -> dict[str, str]:
    """Render the simplification notes and the limitation registry counts.

    Returns:
        Snippets keyed by marker name.
    """
    notes = [
        note
        for ccnl in ccnls
        for note in ccnl.coverage.notes
        if note.kind is NoteKind.SIMPLIFICATION
    ]
    impact = Counter(str(note.monetary_impact) for note in notes)
    registry = [
        *load_engine_limitations(),
        *(lim for ccnl in ccnls for lim in ccnl.limitations),
    ]
    documented = sum(
        lim.applies_when.trigger is LimitationTrigger.OUTSIDE_INPUT for lim in registry
    )
    return {
        "simplification-notes": str(len(notes)),
        "simplification-yes": str(impact["yes"]),
        "simplification-unknown": str(impact["unknown"]),
        "simplification-no": str(impact["no"]),
        "limitations-total": str(len(registry)),
        "limitations-engine": str(len(load_engine_limitations())),
        "limitations-outside-input": str(documented),
    }


def bundle_counts() -> dict[str, str]:
    """Render every count the trust pages may quote.

    Returns:
        Snippets keyed by marker name.
    """
    ccnls = _bundled_ccnls()
    return {
        **_readiness_counts(ccnls),
        **_review_record_counts(ccnls),
        **_provenance_counts(payable_rules.inventory()),
        **_reference_case_counts(),
        **_limitation_counts(ccnls),
    }


def render(text: str, counts: Mapping[str, str]) -> tuple[str, set[str]]:
    """Fill every marker of *text* whose name is a known count.

    A marker with an unknown name is left as it is.

    Returns:
        The filled text and the names of all its markers, known or not.
    """
    names: set[str] = set()

    def _fill(match: re.Match[str]) -> str:
        name = match["name"]
        names.add(name)
        if name not in counts:
            return match[0]
        return f"<!-- trust:{name} -->{counts[name]}<!-- /trust:{name} -->"

    return MARKER_RE.sub(_fill, text), names


@dataclass(frozen=True)
class TrustPages:
    """Outcome of rendering the trust pages against the bundle counts.

    Attributes:
        changed: Pages whose content changes, with their new content.
        unknown: Marker names that match no count.
        unused: Count names that no page quotes.
    """

    changed: dict[Path, str]
    unknown: list[str]
    unused: list[str]


def render_pages(trust_dir: Path, counts: Mapping[str, str]) -> TrustPages:
    """Render the trust pages of *trust_dir* without writing them.

    Returns:
        The changed pages and the marker problems found.
    """
    changed: dict[Path, str] = {}
    names: set[str] = set()
    for page in sorted(trust_dir.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        filled, page_names = render(text, counts)
        names |= page_names
        if filled != text:
            changed[page] = filled
    return TrustPages(
        changed=changed,
        unknown=sorted(names - set(counts)),
        unused=sorted(set(counts) - names),
    )


def _marker_errors(pages: TrustPages) -> list[str]:
    errors = [f"unknown trust count marker: {name}" for name in pages.unknown]
    errors += [f"count quoted by no trust page: {name}" for name in pages.unused]
    return errors


def main(argv: list[str] | None = None, *, trust_dir: Path = TRUST_DIR) -> int:
    """Write the counts into the trust pages, or check them with ``--check``.

    Returns:
        Process exit code: 1 on drift or on a marker problem.
    """
    args = sys.argv[1:] if argv is None else argv
    pages = render_pages(trust_dir, bundle_counts())
    errors = _marker_errors(pages)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if "--check" not in args:
        for page, content in pages.changed.items():
            page.write_text(content, encoding="utf-8")
        print(f"Updated {len(pages.changed)} trust page(s).")
        return 0
    if pages.changed:
        names = ", ".join(page.name for page in pages.changed)
        print(f"Trust counts out of date in: {names}", file=sys.stderr)
        print(
            "Run: uv run python scripts/documentation/generate_trust_counts.py",
            file=sys.stderr,
        )
        return 1
    print("OK: docs/trust/ counts match the bundle.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
