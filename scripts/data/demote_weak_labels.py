"""Demote every label of the knowledge data that outruns its evidence.

Two labels are lowered, never raised:

- a ``derived`` or ``verified`` provenance record that
  :func:`scripts.ci.provenance_labels.record_reasons` rejects (estimated
  ruleset, estimate wording, no citation) becomes ``assumed``.  Its
  location, quote and transformation are kept, and its ``note`` records
  why;
- a ``reviewed`` or ``production`` CCNL whose ``confidence`` is not
  ``verified`` or whose own payable rules include an ``assumed`` or
  ``missing`` one becomes ``exploratory``.  The recorded reviewer and
  review date are kept.

The script is idempotent and rehashes the files it changes, keeping their
indentation.

Usage::

    uv run python scripts/data/demote_weak_labels.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ci import payable_rules, provenance_labels
from scripts.data.assign_rule_provenance import KNOWLEDGE, write_rehashed

_DEMOTED: Final = "Assumed, not derived: {reasons}."


def demote_record(record: dict[str, Any], *, estimated: bool) -> bool:
    """Lower ``record`` to ``assumed`` when its label outruns its evidence.

    Args:
        record: Provenance record, changed in place.
        estimated: Whether the ruleset of its file is ``estimated``.

    Returns:
        Whether the record changed.
    """
    reasons = provenance_labels.record_reasons(record, estimated=estimated)
    if not reasons:
        return False
    record["status"] = "assumed"
    note = _DEMOTED.format(reasons="; ".join(reasons))
    record["note"] = f"{record['note']} {note}" if record.get("note") else note
    return True


def demote_regime(regime: dict[str, Any], *, estimated: bool) -> bool:
    """Lower the ``source_status`` of a regime whose source does not hold.

    Returns:
        Whether the regime changed.
    """
    record = {"status": regime["source_status"], "location": regime.get("source")}
    if not provenance_labels.record_reasons(record, estimated=estimated):
        return False
    regime["source_status"] = "assumed"
    return True


def demote_records(node: object, *, estimated: bool) -> int:
    """Demote every record under ``node`` whose label does not hold.

    Returns:
        The number of records changed.
    """
    if isinstance(node, list):
        return sum(demote_records(item, estimated=estimated) for item in node)
    if not isinstance(node, dict):
        return 0
    changed = 0
    if "source_status" in node:
        changed += demote_regime(node, estimated=estimated)
    for key, value in node.items():
        if (key == "provenance" or key.endswith("_provenance")) and isinstance(
            value, dict
        ):
            changed += demote_record(value, estimated=estimated)
        else:
            changed += demote_records(value, estimated=estimated)
    return changed


def demote_readiness(data: dict[str, Any], *, weak_rules: int) -> bool:
    """Lower a cleared CCNL to ``exploratory`` when the data does not back it.

    Args:
        data: Decoded CCNL file, changed in place.
        weak_rules: Number of ``assumed`` or ``missing`` payable rules of
            the file.

    Returns:
        Whether the readiness changed.
    """
    verification = data.get("verification")
    if not isinstance(verification, dict):
        return False
    cleared = verification.get("readiness") in provenance_labels.CLEARED
    if not cleared or (verification.get("confidence") == "verified" and not weak_rules):
        return False
    verification["readiness"] = "exploratory"
    return True


def main(root: Path = KNOWLEDGE) -> None:
    """Demote the records first, then the readiness they no longer back.

    Args:
        root: Knowledge directory to rewrite.
    """
    records = 0
    for path in sorted(root.glob("*/data/*.json")):
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        changed = demote_records(data, estimated=provenance_labels.is_estimated(data))
        if changed:
            write_rehashed(path, data, text)
            records += changed
    weak = provenance_labels.weak_counts(payable_rules.inventory(root))
    demoted: list[str] = []
    for path in sorted((root / "ccnl" / "data").glob("*.json")):
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        file = path.relative_to(root).as_posix()
        if demote_readiness(data, weak_rules=weak.get(file, 0)):
            write_rehashed(path, data, text)
            demoted.append(file)
    print(f"Records demoted to assumed: {records}")
    print(f"CCNLs demoted to exploratory: {len(demoted)}")
    for file in demoted:
        print(f"  {file}")


if __name__ == "__main__":
    main()
