"""CCNL data file loaders.

Provides :func:`load_ccnl` and :func:`load_year_rules` for loading validated
data from the package's bundled JSON files.

All JSON files under ``ccnl_engine/data/`` are CCNL data files; all JSON files
under ``ccnl_engine/tax/data/`` are tax year rule files. Both are included in
the wheel via the ``setuptools.package-data`` configuration in ``pyproject.toml``.
"""

from __future__ import annotations

import importlib.resources

from ccnl_engine.models.ccnl import CCNL
from ccnl_engine.tax.models import YearRules


def load_ccnl(filename: str) -> CCNL:
    """Load and validate a CCNL data file from the package bundle.

    Args:
        filename: JSON filename without directory, e.g.
            ``"commercio-confcommercio.json"``.

    Returns:
        A fully-validated :class:`~ccnl_engine.models.ccnl.CCNL` instance.

    Raises:
        FileNotFoundError: If *filename* does not exist in the bundle.
        pydantic.ValidationError: If the JSON does not conform to the schema.
    """
    raw = (
        importlib.resources.files("ccnl_engine.data")
        .joinpath(filename)
        .read_text(encoding="utf-8")
    )
    return CCNL.model_validate_json(raw)


def load_year_rules(year: int) -> YearRules:
    """Load and validate tax year rules from the package bundle.

    Args:
        year: Four-digit fiscal year, e.g. ``2026``.

    Returns:
        A fully-validated :class:`~ccnl_engine.tax.models.YearRules` instance.

    Raises:
        FileNotFoundError: If no data file exists for *year*.
        pydantic.ValidationError: If the JSON does not conform to the schema.
    """
    raw = (
        importlib.resources.files("ccnl_engine.tax.data")
        .joinpath(f"{year}.json")
        .read_text(encoding="utf-8")
    )
    return YearRules.model_validate_json(raw)
