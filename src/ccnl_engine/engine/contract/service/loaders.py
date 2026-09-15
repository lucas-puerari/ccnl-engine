"""CCNL contract data file loaders (reads the Knowledge Base bundle)."""

from __future__ import annotations

import importlib.resources
import json
from functools import cache
from typing import Any

from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.io.service.bundled import read_bundled
from ccnl_engine.engine.metadata import source_hash


@cache
def load_ccnl(filename: str) -> CCNL:
    """Load and validate a CCNL data file from the package bundle.

    The returned :class:`CCNL` instance is shared across all callers in the
    same process (the result is cached after the first load).  All models in
    the CCNL hierarchy are frozen (``model_config frozen=True``), list fields
    use immutable tuples and dict fields are wrapped in
    ``types.MappingProxyType``, making the entire object graph transitively
    read-only.  Callers must not attempt to modify the returned object.

    Args:
        filename: Name of the JSON data file bundled under
            ``ccnl_engine/knowledge/ccnl/data/``
            (e.g. ``"metalmeccanico-federmeccanica.json"``).

    Returns:
        The validated, immutable CCNL instance.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    raw = read_bundled(pkg, filename)
    payload = json.loads(raw)
    _verify_ruleset_hash(payload)
    return CCNL.model_validate(payload)


def _verify_ruleset_hash(payload: dict[str, Any]) -> None:
    """Verify a recorded ``ruleset.source_hash`` against the payload.

    The check is skipped when the file carries no ``ruleset`` block or no
    ``source_hash``; a stale hash means the data file was hand-modified after
    the provenance backfill.

    Raises:
        ValueError: If the recomputed hash differs from the recorded one.
    """
    ruleset = payload.get("ruleset")
    if not isinstance(ruleset, dict):
        return
    recorded = ruleset.get("source_hash")
    if not isinstance(recorded, str):
        return
    if source_hash(payload) != recorded:
        msg = (
            "CCNL ruleset source_hash mismatch; data file has been modified "
            "without updating its ruleset block."
        )
        raise ValueError(msg)
