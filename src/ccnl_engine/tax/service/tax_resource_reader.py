"""Tax knowledge-base resource reader: raw JSON loaders and ruleset helpers."""

from __future__ import annotations

import importlib.resources
import json
from typing import TYPE_CHECKING, Any

from ccnl_engine.knowledge.service.bundled import read_bundled
from ccnl_engine.knowledge.service.loader_utils import (
    as_ruleset,
    try_ruleset,
    verify_ruleset_hash,
)
from ccnl_engine.shared.domain.errors import UnsupportedTaxYearError

if TYPE_CHECKING:
    from importlib.abc import Traversable

    from ccnl_engine.contract.domain.identity import TaxSector
    from ccnl_engine.provenance.domain.ruleset_identity import RulesetIdentity


def _as_ruleset(raw: dict[str, Any]) -> RulesetIdentity | None:
    """Delegate to :func:`~ccnl_engine.knowledge.service.loader_utils.as_ruleset`.

    Returns:
        The parsed :class:`~ccnl_engine.provenance.domain.ruleset_identity\
.RulesetIdentity`,
        or ``None`` when the dict carries no ``ruleset`` block.
    """
    return as_ruleset(raw)


def _try_ruleset(raw: dict[str, Any]) -> RulesetIdentity | None:
    """Delegate to :func:`~ccnl_engine.knowledge.service.loader_utils.try_ruleset`.

    Returns:
        The parsed :class:`~ccnl_engine.provenance.domain.ruleset_identity\
.RulesetIdentity`,
        or ``None`` when absent or invalid.
    """
    return try_ruleset(raw)


def _verify_ruleset_hash(payload: dict[str, Any], filename: str) -> None:
    """Verify the payload's ``ruleset.source_hash``.

    Args:
        payload: The full JSON payload dict.
        filename: Source file name, included in any error message.
    """
    verify_ruleset_hash(payload, filename)


def _read_json(pkg: Traversable, filename: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(read_bundled(pkg, filename))
    _verify_ruleset_hash(data, filename)
    return data


def read_year_json(
    pkg: Traversable, filename: str, year: int, sector: str | None = None
) -> dict[str, Any]:
    """Read the year-keyed data file *filename* from *pkg*.

    Args:
        pkg: Package data directory.
        filename: File name for *year*.
        year: Tax year the file belongs to.
        sector: Tax sector of the file, or ``None`` when it covers all.

    Returns:
        The JSON payload, with its ruleset hash verified.

    Raises:
        UnsupportedTaxYearError: When the bundle has no such file.
    """
    try:
        return _read_json(pkg, filename)
    except FileNotFoundError as exc:
        raise UnsupportedTaxYearError(year, sector=sector) from exc


def _read_year_json(package: str, year: int, sector: TaxSector) -> dict[str, Any]:
    pkg = importlib.resources.files(package)
    return read_year_json(pkg, f"{year}-{sector.value}.json", year, sector.value)


def read_tax_rules_raw(year: int, sector: TaxSector) -> dict[str, Any]:
    """Read the IRPEF/TFR block of a tax year file as a raw dict.

    Args:
        year: Tax year.
        sector: INPS sector classification.

    A year missing from the bundle raises
    :class:`~ccnl_engine.shared.domain.errors.UnsupportedTaxYearError`.

    Returns:
        The ``knowledge/tax/data/<year>-<sector>.json`` payload.
    """
    return _read_year_json("ccnl_engine.knowledge.tax.data", year, sector)


def read_inps_rules_raw(year: int, sector: TaxSector) -> dict[str, Any]:
    """Read the INPS contribution block of a year/sector file as a raw dict.

    Args:
        year: Tax year.
        sector: INPS sector classification.

    Returns:
        The ``knowledge/inps/data/<year>-<sector>.json`` payload.
    """
    return _read_year_json("ccnl_engine.knowledge.inps.data", year, sector)
