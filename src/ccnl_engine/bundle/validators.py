"""Shared utilities for loading and verifying bundled data files."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Final

from pydantic import ValidationError

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.provenance.ruleset.models import RulesetIdentity, source_hash

if TYPE_CHECKING:
    from collections.abc import Iterator

#: Statuses that claim a located source.
_SOURCED: Final = frozenset({"verified", "derived"})
#: Wording of a note or transformation that records an estimate.
_ESTIMATE: Final = re.compile(r"\bestimat(?:e|ed|es|ion)\b", re.IGNORECASE)


def verify_ruleset_hash(payload: dict[str, Any], filename: str = "<unknown>") -> None:
    """Verify a recorded ``ruleset.source_hash`` against the payload.

    The check is skipped when the file carries no ``ruleset`` block or no
    ``source_hash``; a stale hash means the data file was hand-modified after
    the provenance backfill.

    Raises:
        DataIntegrityError: If the recomputed hash differs from the recorded one.
    """
    ruleset = payload.get("ruleset")
    if not isinstance(ruleset, dict):
        return
    recorded = ruleset.get("source_hash")
    if not isinstance(recorded, str):
        return
    if source_hash(payload) != recorded:
        msg = (
            f"ruleset source_hash mismatch in {filename}; data file has been "
            "modified without updating its ruleset block."
        )
        raise DataIntegrityError(
            msg,
            remediation=(
                "Regenerate the source_hash of the modified file: run "
                "scripts/docs/rehash_ccnl.py for the CCNL files, "
                "scripts/data/assign_rule_provenance.py for the fiscal files "
                "it lists, or set it to "
                "ccnl_engine.provenance.ruleset.models.source_hash "
                "of the payload."
            ),
        )


def as_ruleset(raw: dict[str, Any]) -> RulesetIdentity | None:
    """Parse a raw dict's ``ruleset`` block into a :class:`RulesetIdentity`.

    Returns:
        The parsed identity, or ``None`` when the dict carries no ``ruleset``.
    """
    block = raw.get("ruleset")
    if not isinstance(block, dict):
        return None
    return RulesetIdentity.model_validate(block)


def try_ruleset(raw: dict[str, Any]) -> RulesetIdentity | None:
    """Parse a raw dict's ``ruleset`` block, returning ``None`` on any error.

    Unlike :func:`as_ruleset`, silently returns ``None`` when the block is
    present but incomplete.  Used for optional-feature loaders whose JSON files
    may carry partial provenance metadata.

    Returns:
        The parsed identity, or ``None`` when absent or invalid.
    """
    block = raw.get("ruleset")
    if not isinstance(block, dict):
        return None
    try:
        return RulesetIdentity.model_validate(block)
    except ValidationError:
        return None


def provenance_label_errors(payload: dict[str, Any]) -> list[str]:
    """Return the records of ``payload`` labelled stronger than they are.

    A ``derived`` or ``verified`` record claims a located source, so it is
    rejected when the ruleset declares ``source_type`` ``estimated``, when
    its ``note`` or ``transformation`` records an estimate, or when it has
    no citation: an http(s) ``location.source_document.url`` and a
    ``location.section`` or ``location.page``.  A regime records its
    status in ``source_status`` and its location in ``source``.

    Args:
        payload: Decoded data file.

    Returns:
        ``"<path>: <status>: <reason>"`` messages; empty when every label
        holds.
    """
    ruleset = payload.get("ruleset")
    estimated = isinstance(ruleset, dict) and ruleset.get("source_type") == "estimated"
    return [
        f"{path}: {reason}"
        for path, record in _records(payload, "")
        if record.get("status") in _SOURCED
        for reason in _label_reasons(record, estimated=estimated)
    ]


def verify_provenance_labels(
    payload: dict[str, Any], filename: str = "<unknown>"
) -> None:
    """Reject a data file whose provenance labels outrun their evidence.

    Raises:
        DataIntegrityError: When :func:`provenance_label_errors` finds one.
    """
    errors = provenance_label_errors(payload)
    if errors:
        msg = f"provenance labels stronger than their evidence in {filename}: " + (
            "; ".join(errors)
        )
        raise DataIntegrityError(
            msg,
            remediation=(
                "Label the rule 'assumed' (scripts/data/demote_weak_labels.py) "
                "or cite the article and the URL of the source it is read from."
            ),
        )


def _records(node: object, path: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield every provenance record under ``node`` with its path.

    Yields:
        ``(path, record)``; a regime yields its ``source_status`` as the
        status and its ``source`` as the location.
    """
    if isinstance(node, list):
        for index, item in enumerate(node):
            yield from _records(item, f"{path}[{index}]")
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
            yield from _records(value, child)


def _label_reasons(record: dict[str, Any], *, estimated: bool) -> Iterator[str]:
    """Yield why a ``derived`` or ``verified`` record does not hold.

    Yields:
        One reason per failed requirement.
    """
    status = record["status"]
    if estimated:
        yield f"{status}: its ruleset declares source_type 'estimated'"
    text = f"{record.get('note') or ''} {record.get('transformation') or ''}"
    if _ESTIMATE.search(text):
        yield f"{status}: its note records an estimate"
    if not has_citation(record.get("location")):
        yield f"{status}: no citation (http(s) url and section or page)"


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
