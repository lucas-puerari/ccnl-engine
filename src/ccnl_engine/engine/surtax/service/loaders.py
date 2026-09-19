"""Surtax rules loader (reads the Knowledge Base bundle)."""

from __future__ import annotations

import importlib.resources
import json
from functools import cache
from typing import Any

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.io.service.bundled import read_bundled
from ccnl_engine.engine.io.service.loader_utils import verify_ruleset_hash
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

    Each call returns a new :class:`~ccnl_engine.engine.surtax.domain.SurtaxRules`
    whose ``regionale`` and ``comunale`` dicts are freshly allocated, so callers
    may add or remove keys without affecting subsequent loads. The individual
    :class:`~ccnl_engine.engine.surtax.domain.rules.RegionaleEntry` and
    :class:`~ccnl_engine.engine.surtax.domain.rules.ComunaleEntry` values are
    shared with the internal cache; they are frozen and their ``brackets`` tuples
    are immutable, so in-place mutation is not possible.

    Args:
        year: Fiscal year (e.g. ``2026``). A matching pair of data files must
            exist in the bundle.

    Returns:
        A :class:`~ccnl_engine.engine.surtax.domain.SurtaxRules` instance with
        ``regionale`` and ``comunale`` rate tables for the requested year.
    """
    cached = _load_surtax_rules_cached(year)
    return cached.model_copy(
        update={
            "regionale": dict(cached.regionale),
            "comunale": dict(cached.comunale),
        }
    )


@cache
def _load_surtax_rules_cached(year: int) -> SurtaxRules:
    """Parse, validate and cache surtax rules for *year* (internal use only).

    Callers must use :func:`load_surtax_rules`, which shallow-copies the
    top-level dicts before returning so each caller gets isolated containers.

    Returns:
        The shared, frozen :class:`~ccnl_engine.engine.surtax.domain.SurtaxRules`
        object stored in the cache.

    Raises:
        DataIntegrityError: If a data file's year field doesn't match *year*.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.surtax.data")
    reg_raw = read_bundled(pkg, f"regionale-{year}.json")
    com_raw = read_bundled(pkg, f"comunale-{year}.json")
    reg_payload = json.loads(reg_raw)
    com_payload = json.loads(com_raw)
    _verify_ruleset_hash(reg_payload, f"regionale-{year}.json")
    _verify_ruleset_hash(com_payload, f"comunale-{year}.json")
    if reg_payload.get("year") != year:
        msg = (
            f"regionale-{year}.json year={reg_payload.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    if com_payload.get("year") != year:
        msg = (
            f"comunale-{year}.json year={com_payload.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    reg = RegionaleRaw.model_validate(reg_payload)
    com = ComunaleRaw.model_validate(com_payload)
    return SurtaxRules(
        year=year,
        regional_ruleset=reg.ruleset,
        municipal_ruleset=com.ruleset,
        regionale=reg.rates,
        comunale=com.rates,
        comunale_rates_are_advance=com.rates_are_advance,
        comunale_advance_fraction=com.advance_fraction,
    )


def _verify_ruleset_hash(payload: dict[str, Any], filename: str) -> None:
    """Verify a recorded ``ruleset.source_hash`` against the payload.

    Delegates to :func:`~ccnl_engine.engine.io.service.loader_utils\
.verify_ruleset_hash`.
    """
    verify_ruleset_hash(payload, filename)
