"""CCNL contract data file loaders (reads the Knowledge Base bundle)."""

from __future__ import annotations

import importlib.resources

from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.io.bundled import read_bundled


def load_ccnl(filename: str) -> CCNL:
    """Load and validate a CCNL data file from the package bundle.

    Args:
        filename: Name of the JSON data file bundled under
            ``ccnl_engine/knowledge/ccnl/data/``
            (e.g. ``"metalmeccanico-federmeccanica.json"``).

    Returns:
        The validated CCNL instance.
    """
    pkg = importlib.resources.files("ccnl_engine.knowledge.ccnl.data")
    raw = read_bundled(pkg, filename)
    return CCNL.model_validate_json(raw)
