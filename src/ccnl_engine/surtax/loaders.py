"""Surtax rules loader: addizionale regionale e comunale IRPEF."""

from __future__ import annotations

import importlib.resources

from ccnl_engine.io.bundled import read_bundled
from ccnl_engine.surtax.models import (
    SurtaxRules,
    _ComunaleRaw,
    _RegionaleRaw,
)


def load_surtax_rules(year: int) -> SurtaxRules:
    """Load addizionale regionale and comunale rates for the given fiscal year.

    Reads ``regionale-{year}.json`` and ``comunale-{year}.json`` from the
    package bundle (``ccnl_engine/surtax/data/``). In installed wheels the
    compressed ``.json.gz`` variants are preferred; plain ``.json`` files are
    used as fallback for editable installs (mirroring the behaviour of
    :func:`~ccnl_engine.tax.loaders.load_year_rules`).

    Args:
        year: Fiscal year (e.g. ``2026``). A matching pair of data files must
            exist in the bundle.

    Returns:
        A :class:`~ccnl_engine.surtax.models.SurtaxRules` instance with
        ``regionale`` and ``comunale`` rate tables for the requested year.

    """
    pkg = importlib.resources.files("ccnl_engine.surtax.data")
    reg_raw = read_bundled(pkg, f"regionale-{year}.json")
    com_raw = read_bundled(pkg, f"comunale-{year}.json")
    reg = _RegionaleRaw.model_validate_json(reg_raw)
    com = _ComunaleRaw.model_validate_json(com_raw)
    return SurtaxRules(
        year=year,
        regionale=reg.rates,
        comunale=com.rates,
    )
