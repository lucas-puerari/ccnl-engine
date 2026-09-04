"""CCNL contract data file loaders."""

from __future__ import annotations

import importlib.resources

from ccnl_engine.models.ccnl import CCNL


def load_ccnl(filename: str) -> CCNL:
    """Load and validate a CCNL data file from the package bundle.

    Args:
        filename: Name of the JSON data file bundled under
            ``ccnl_engine/contracts/data/``
            (e.g. ``"metalmeccanico-federmeccanica.json"``).

    Returns:
        The validated CCNL instance.
    """
    raw = (
        importlib.resources
        .files("ccnl_engine.contracts.data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    return CCNL.model_validate_json(raw)
