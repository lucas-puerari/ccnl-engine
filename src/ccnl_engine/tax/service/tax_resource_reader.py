"""Tax knowledge-base resource reader: raw JSON loaders and ruleset helpers."""

from __future__ import annotations

import json
from functools import cache
from typing import TYPE_CHECKING, Any

from ccnl_engine.knowledge.service.loader_utils import (
    as_ruleset,
    try_ruleset,
    verify_provenance_labels,
    verify_ruleset_hash,
)
from ccnl_engine.knowledge.service.manifest import read_resource, resources
from ccnl_engine.shared.domain.errors import UnsupportedTaxYearError

if TYPE_CHECKING:
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


def _verify_payload(payload: dict[str, Any], filename: str) -> None:
    """Verify the ``ruleset.source_hash`` and the provenance labels.

    Args:
        payload: The full JSON payload dict.
        filename: Source file name, included in any error message.
    """
    verify_ruleset_hash(payload, filename)
    verify_provenance_labels(payload, filename)


#: Datasets of the sector tax and INPS files of a year.
ANNUAL = "taxation/annual"
CONTRIBUTION = "social_security/contribution"


def _years(dataset: str) -> set[int]:
    return {
        r.year
        for r in resources(dataset)
        if r.year is not None and r.scope == "terziario"
    }


@cache
def supported_tax_years() -> tuple[int, ...]:
    """Return the tax years whose tax and INPS tables the bundle ships.

    Returns:
        The years, ascending, that have both a sector tax file and a sector
        INPS file.
    """
    return tuple(sorted(_years(ANNUAL) & _years(CONTRIBUTION)))


def _read_json(path: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(read_resource(path))
    _verify_payload(data, path)
    return data


def read_year_json(path: str, year: int, sector: str | None = None) -> dict[str, Any]:
    """Read the year-keyed resource at *path* of the knowledge manifest.

    Args:
        path: Path of the resource, relative to the knowledge bundle.
        year: Tax year the file belongs to.
        sector: Tax sector of the file, or ``None`` when it covers all.

    Returns:
        The JSON payload, with its ruleset hash verified.

    Raises:
        UnsupportedTaxYearError: When the bundle has no such file.
    """
    try:
        return _read_json(path)
    except FileNotFoundError as exc:
        raise UnsupportedTaxYearError(
            year, sector=sector, supported=supported_tax_years()
        ) from exc


def _read_year_json(dataset: str, year: int, sector: TaxSector) -> dict[str, Any]:
    path = f"{dataset}/{year}/{sector.value}.json"
    return read_year_json(path, year, sector.value)


def read_tax_rules_raw(year: int, sector: TaxSector) -> dict[str, Any]:
    """Read the IRPEF/TFR block of a tax year file as a raw dict.

    Args:
        year: Tax year.
        sector: INPS sector classification.

    A year missing from the bundle raises
    :class:`~ccnl_engine.shared.domain.errors.UnsupportedTaxYearError`.

    Returns:
        The ``knowledge/taxation/annual/<year>/<sector>.json`` payload.
    """
    return _read_year_json(ANNUAL, year, sector)


def read_inps_rules_raw(year: int, sector: TaxSector) -> dict[str, Any]:
    """Read the INPS contribution block of a year/sector file as a raw dict.

    Args:
        year: Tax year.
        sector: INPS sector classification.

    Returns:
        The ``knowledge/social_security/contribution/<year>/<sector>.json``
        payload.
    """
    return _read_year_json(CONTRIBUTION, year, sector)
