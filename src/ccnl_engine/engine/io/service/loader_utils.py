"""Shared utilities for loading and verifying bundled data files."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity, source_hash


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
                "Re-run scripts/ci/rehash_ccnl.py to regenerate the "
                "source_hash for the modified file."
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
