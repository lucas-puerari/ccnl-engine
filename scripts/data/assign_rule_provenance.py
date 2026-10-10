"""Assign a provenance status to every rule record of the knowledge data.

CCNL records already cite a document location and an extraction trace; the
status follows from what they record:

- ``assumed``: a record without a citation (an http(s) document url and a
  section or page), or an AI extraction without the review below;
- ``verified``: ``extraction.verification_status`` is ``verified`` and the
  record names the reviewer (``verified_by``) and the date (``verified_at``);
- ``derived``: any other record.

A legacy ``verified`` without reviewer and date becomes ``derived``: the
record claims a check but does not say who made it or when.  The file-level
``verification.human_reviewed_by`` is not used, because it does not say
which values were checked.

Each additional-months period without a record receives an ``assumed``
record: the contract documents are known, the clause is not located.

Fiscal files record no per-block provenance.  Their records come from
:data:`FISCAL_RECORDS`, copied from each file's own notes and ruleset
source, or from the rule model docstrings where that is the only citation
in the repository.  A block whose value is a reconstruction, a proxy or an
estimate is ``assumed`` even when a document is cited.

The script is idempotent: a record that already has a status is kept.
Touched files get a recomputed ``ruleset.source_hash``.

Usage::

    uv run python scripts/data/assign_rule_provenance.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ccnl_engine.provenance.domain.ruleset_identity import source_hash
from scripts.ci.provenance_labels import has_citation
from scripts.data.fiscal_provenance import FISCAL_RECORDS

KNOWLEDGE: Final = (
    Path(__file__).resolve().parents[2] / "src" / "ccnl_engine" / "knowledge"
)
_ASSUMED_EXTRA_MONTHS: Final = (
    "Number of monthly payments read from the contract file; no clause is cited for it."
)


def ccnl_status(record: dict[str, Any]) -> str:
    """Return the status a CCNL provenance record supports.

    Returns:
        ``verified``, ``assumed`` or ``derived`` (see the module docstring).
    """
    extraction = record.get("extraction") or {}
    if not has_citation(record.get("location")):
        return "assumed"
    if (
        extraction.get("verification_status") == "verified"
        and extraction.get("verified_by")
        and extraction.get("verified_at")
    ):
        return "verified"
    return "assumed" if extraction.get("method") == "ai" else "derived"


def _with_status(record: dict[str, Any], counts: Counter[str]) -> dict[str, Any]:
    """Return ``record`` with a status first, keeping an existing one.

    Returns:
        The record, ``status`` as its first key.
    """
    status = record.get("status") or ccnl_status(record)
    counts[status] += 1
    return {"status": status} | {k: v for k, v in record.items() if k != "status"}


def _walk(value: object, counts: Counter[str]) -> object:
    """Return ``value`` with every nested provenance record given a status.

    Returns:
        A copy of ``value``.
    """
    if isinstance(value, list):
        return [_walk(item, counts) for item in value]
    if not isinstance(value, dict):
        return value
    out: dict[str, Any] = {}
    for key, item in value.items():
        if key == "provenance" and isinstance(item, dict):
            out[key] = _with_status(item, counts)
        else:
            out[key] = _walk(item, counts)
    return out


def migrate_ccnl(data: dict[str, Any], counts: Counter[str]) -> dict[str, Any]:
    """Return a CCNL payload whose provenance records all carry a status.

    An additional-months period without a record receives an ``assumed``
    one; its validity is the one of the period itself.

    Returns:
        The migrated payload.
    """
    migrated: dict[str, Any] = _walk(data, counts)  # type: ignore[assignment]
    series = migrated.get("parameters", {}).get("additional_months", {})
    for period in series.get("periods", []):
        if period.get("value") is not None and not period.get("provenance"):
            period["provenance"] = {
                "status": "assumed",
                "location": None,
                "note": _ASSUMED_EXTRA_MONTHS,
            }
            counts["assumed"] += 1
    return migrated


def migrate_fiscal(
    name: str, data: dict[str, Any], counts: Counter[str]
) -> dict[str, Any]:
    """Return a fiscal payload with the records of :data:`FISCAL_RECORDS`.

    A block keeps a record it already has.  A regime takes the status only,
    its ``source`` being its location.

    Returns:
        The migrated payload.
    """
    for block, record in FISCAL_RECORDS.get(name, {}).items():
        target, key = _slot(data, block)
        if key == "source_status":
            target.setdefault(key, record["status"])
            counts[target[key]] += 1
            continue
        if not target.get(key):
            target[key] = record
        counts[target[key]["status"]] += 1
    return data


def _slot(data: dict[str, Any], block: str) -> tuple[dict[str, Any], str]:
    """Return the object and key that hold the record of ``block``.

    Returns:
        ``(container, key)``.
    """
    if block in {"irpef_brackets", "fixed_term_additional_rate"}:
        return data, f"{block}_provenance"
    if block == "*":
        return data, "provenance"
    if block in {"rinnovo", "notte_festivi_turni"}:
        return data[block], "source_status"
    return data[block], "provenance"


def write_rehashed(path: Path, data: dict[str, Any], original: str) -> None:
    """Rehash ``data`` when it carries a hash and write it to ``path``.

    The indentation of ``original`` is kept, so only the records change.
    """
    ruleset = data.get("ruleset")
    if isinstance(ruleset, dict) and "source_hash" in ruleset:
        ruleset["source_hash"] = source_hash(data)
    second_line = original.split("\n", 2)[1]
    indent = len(second_line) - len(second_line.lstrip(" "))
    text = json.dumps(data, ensure_ascii=False, indent=indent) + "\n"
    if text != original:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    """Migrate every CCNL and fiscal data file and print the status counts."""
    ccnl_counts: Counter[str] = Counter()
    for path in sorted((KNOWLEDGE / "contract" / "agreement").glob("*.json")):
        text = path.read_text(encoding="utf-8")
        write_rehashed(path, migrate_ccnl(json.loads(text), ccnl_counts), text)
    fiscal_counts: Counter[str] = Counter()
    for name in sorted(FISCAL_RECORDS):
        path = KNOWLEDGE / name
        text = path.read_text(encoding="utf-8")
        migrated = migrate_fiscal(name, json.loads(text), fiscal_counts)
        write_rehashed(path, migrated, text)
    print(f"CCNL provenance records: {dict(sorted(ccnl_counts.items()))}")
    print(f"Fiscal provenance records: {dict(sorted(fiscal_counts.items()))}")


if __name__ == "__main__":
    main()
