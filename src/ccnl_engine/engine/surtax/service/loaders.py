"""Surtax rules loader (reads the Knowledge Base bundle)."""

from __future__ import annotations

import importlib.resources
import json
from typing import Any

from ccnl_engine.engine.io.bundled import read_bundled
from ccnl_engine.engine.metadata import source_hash
from ccnl_engine.engine.surtax.domain.rules import (
    ComunaleRaw,
    RegionaleRaw,
    SurtaxRules,
)


def load_surtax_rules(year: int) -> SurtaxRules:
    """Load addizionale regionale and comunale rates for the given fiscal year.

    Reads ``regionale-{year}.json`` and ``comunale-{year}.json`` from the
    package bundle (``ccnl_engine/knowledge/surtax/data/``). In installed
    wheels the compressed ``.json.gz`` variants are preferred; plain ``.json``
    files are used as fallback for editable installs (mirroring the behaviour
    of :func:`~ccnl_engine.engine.tax.service.loaders.load_year_rules`).

    Args:
        year: Fiscal year (e.g. ``2026``). A matching pair of data files must
            exist in the bundle.

    Returns:
        A :class:`~ccnl_engine.engine.surtax.domain.SurtaxRules` instance with
        ``regionale`` and ``comunale`` rate tables for the requested year.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.surtax.data")
    reg_raw = read_bundled(pkg, f"regionale-{year}.json")
    com_raw = read_bundled(pkg, f"comunale-{year}.json")
    reg_payload = json.loads(reg_raw)
    com_payload = json.loads(com_raw)
    _verify_ruleset_hash(reg_payload, f"regionale-{year}.json")
    _verify_ruleset_hash(com_payload, f"comunale-{year}.json")
    reg = RegionaleRaw.model_validate(reg_payload)
    com = ComunaleRaw.model_validate(com_payload)
    ruleset = reg.ruleset or com.ruleset
    return SurtaxRules(
        year=year,
        ruleset=ruleset,
        regionale=reg.rates,
        comunale=com.rates,
    )


def _verify_ruleset_hash(payload: dict[str, Any], filename: str) -> None:
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
            f"ruleset source_hash mismatch in {filename}; data file has been "
            "modified without updating its ruleset block."
        )
        raise ValueError(msg)
