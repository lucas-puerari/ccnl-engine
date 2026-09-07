"""Surtax rules loader (reads the Knowledge Base bundle)."""

from __future__ import annotations

import importlib.resources

from ccnl_engine.engine.io.bundled import read_bundled
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
    reg = RegionaleRaw.model_validate_json(reg_raw)
    com = ComunaleRaw.model_validate_json(com_raw)
    return SurtaxRules(
        year=year,
        regionale=reg.rates,
        comunale=com.rates,
    )
