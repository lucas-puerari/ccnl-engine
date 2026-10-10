"""Labels that must agree with their evidence: rule statuses and readiness.

Two checks back the schema gate of :mod:`scripts.provenance.check`:

- :func:`label_errors`: a ``derived`` or ``verified`` record claims a
  located source.  It is rejected when the ruleset of its file declares
  ``source_type`` ``estimated``, when its ``note`` or ``transformation``
  records an estimate, or when it has no citation: an http(s)
  ``location.source_document.url`` and a ``location.section`` or
  ``location.page``.  Every record of every data file is checked, payable
  or not, nested or not; a substitute-tax regime records its status in
  ``source_status`` and its location in ``source``.  The loaders apply the
  same rule (``ccnl_engine.knowledge.validators``).
- :func:`readiness_errors`: a ``reviewed`` or ``production`` CCNL claims a
  review, so its ``confidence`` is ``verified`` and none of the payable
  rules of its own file is ``assumed`` or ``missing``.

``extraction.verification_status: unverified`` is not a reason: it is what
``derived`` means, a value read from a cited location without a recorded
check.

The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Final

from scripts.provenance import rules as payable_rules

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from scripts.provenance.rules import PayableRule

#: Statuses that claim a located source.
SOURCED: Final = ("verified", "derived")
#: Readiness tiers that claim a review.
CLEARED: Final = ("reviewed", "production")
_WEAK: Final = ("assumed", "missing")
_ESTIMATE: Final = re.compile(r"\bestimat(?:e|ed|es|ion)\b", re.IGNORECASE)

type Json = dict[str, object]


def records(node: object, path: str = "") -> Iterator[tuple[str, Json]]:
    """Yield every provenance record under ``node`` with its path.

    Yields:
        ``(path, record)``; a regime yields its ``source_status`` as the
        status and its ``source`` as the location.
    """
    if isinstance(node, list):
        for index, item in enumerate(node):
            yield from records(item, f"{path}[{index}]")
        return
    if not isinstance(node, dict):
        return
    if "source_status" in node:
        yield path, {"status": node["source_status"], "location": node.get("source")}
    for key, value in node.items():
        child = f"{path}.{key}" if path else key
        if (key == "provenance" or key.endswith("_provenance")) and isinstance(
            value, dict
        ):
            yield child, value
        else:
            yield from records(value, child)


def has_citation(location: object) -> bool:
    """Return whether ``location`` cites a reachable document and a clause.

    Returns:
        ``True`` when the source document has an http(s) ``url`` and the
        location names a ``section`` or a ``page``.
    """
    if not isinstance(location, dict):
        return False
    document = location.get("source_document")
    url = document.get("url") if isinstance(document, dict) else None
    reachable = isinstance(url, str) and url.startswith(("https://", "http://"))
    return reachable and bool(location.get("section") or location.get("page"))


def record_reasons(record: Json, *, estimated: bool) -> list[str]:
    """Return why a record is labelled stronger than its evidence.

    Args:
        record: Provenance record.
        estimated: Whether the ruleset of its file is ``estimated``.

    Returns:
        One reason per failed requirement; empty for an ``assumed`` or
        ``missing`` record and for a record whose label holds.
    """
    if record.get("status") not in SOURCED:
        return []
    reasons: list[str] = []
    if estimated:
        reasons.append("its ruleset declares source_type 'estimated'")
    text = f"{record.get('note') or ''} {record.get('transformation') or ''}"
    if _ESTIMATE.search(text):
        reasons.append("its note records an estimate")
    if not has_citation(record.get("location")):
        reasons.append("no citation (http(s) url and section or page)")
    return reasons


def is_estimated(data: object) -> bool:
    """Return whether the ruleset of a data file declares an estimate.

    Returns:
        ``True`` when ``ruleset.source_type`` is ``estimated``.
    """
    ruleset = data.get("ruleset") if isinstance(data, dict) else None
    return isinstance(ruleset, dict) and ruleset.get("source_type") == "estimated"


def file_label_errors(data: object) -> list[str]:
    """Return the records of one data file labelled stronger than they are.

    Returns:
        ``"<path>: <status>: <reason>"`` messages.
    """
    estimated = is_estimated(data)
    return [
        f"{path}: {record['status']}: {reason}"
        for path, record in records(data)
        for reason in record_reasons(record, estimated=estimated)
    ]


def label_errors(root: Path = payable_rules.KNOWLEDGE_DIR) -> list[str]:
    """Return the records of the bundle labelled stronger than they are.

    Args:
        root: Knowledge directory to scan; every JSON resource but the
            manifest.

    Returns:
        ``"<file>: <path>: <reason>"`` messages, in file-name order.
    """
    errors: list[str] = []
    for path in sorted(p for p in root.rglob("*.json") if p.name != "manifest.json"):
        file = path.relative_to(root).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))
        errors.extend(f"{file}: {error}" for error in file_label_errors(data))
    return errors


def weak_counts(rules: tuple[PayableRule, ...]) -> dict[str, int]:
    """Count the ``assumed`` and ``missing`` payable rules of each file.

    Returns:
        Data file to its number of weak rules; files without one are left
        out.
    """
    weak: dict[str, int] = {}
    for rule in rules:
        if rule.status in _WEAK:
            weak[rule.file] = weak.get(rule.file, 0) + 1
    return weak


def readiness_errors(
    rules: tuple[PayableRule, ...], root: Path = payable_rules.KNOWLEDGE_DIR
) -> list[str]:
    """Return the CCNLs whose readiness claims a review the data does not hold.

    Args:
        rules: Payable rules of ``root``.
        root: Knowledge directory to scan.

    Returns:
        ``"<file>: <reason>"`` messages, in file-name order.
    """
    weak = weak_counts(rules)
    errors: list[str] = []
    for path in sorted((root / "contract" / "agreement").glob("*.json")):
        file = path.relative_to(root).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))
        verification = data.get("verification") or {}
        readiness = verification.get("readiness", "exploratory")
        if readiness not in CLEARED:
            continue
        if verification.get("confidence") != "verified":
            errors.append(f"{file}: {readiness} without confidence 'verified'")
        if weak.get(file):
            errors.append(
                f"{file}: {readiness} with {weak[file]} assumed or missing "
                "payable rule(s)"
            )
    return errors
