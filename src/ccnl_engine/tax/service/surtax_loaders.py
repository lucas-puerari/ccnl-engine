"""Surtax rules loader (reads the Knowledge Base bundle)."""

from __future__ import annotations

import json
from functools import cache
from typing import Any

from ccnl_engine.knowledge.service.loader_utils import (
    verify_provenance_labels,
    verify_ruleset_hash,
)
from ccnl_engine.knowledge.service.manifest import read_resource
from ccnl_engine.shared.domain.errors import DataIntegrityError, UnsupportedTaxYearError
from ccnl_engine.tax.domain.surtax_rules import (
    ComunaleRaw,
    RegionaleRaw,
    SurtaxRules,
)
from ccnl_engine.tax.service.tax_resource_reader import supported_tax_years


def load_surtax_rules(year: int) -> SurtaxRules:
    """Load addizionale regionale and comunale rates for the given fiscal year.

    Reads ``surtax/regional/{year}.json`` and ``surtax/municipal/{year}.json``
    of the knowledge manifest. In installed
    wheels the compressed ``.json.gz`` variants are preferred; plain ``.json``
    files are used as fallback for editable installs (mirroring the behaviour
    of :func:`~ccnl_engine.tax.service.tax_annual_assembler.load_year_rules`).

    Each call returns a new :class:`~ccnl_engine.tax.domain.surtax_rules.SurtaxRules`
    whose ``regionale`` and ``comunale`` dicts are freshly allocated, so callers
    may add or remove keys without affecting subsequent loads. The individual
    :class:`~ccnl_engine.tax.domain.surtax_tables.RegionaleEntry` and
    :class:`~ccnl_engine.tax.domain.surtax_tables.ComunaleEntry` values are
    shared with the internal cache; they are frozen and their ``brackets`` tuples
    are immutable, so in-place mutation is not possible.

    Args:
        year: Fiscal year (e.g. ``2026``). A matching pair of data files must
            exist in the bundle.

    Returns:
        A :class:`~ccnl_engine.tax.domain.surtax_rules.SurtaxRules` instance with
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
        The shared, frozen :class:`~ccnl_engine.tax.domain.surtax_rules.SurtaxRules`
        object stored in the cache.

    Raises:
        DataIntegrityError: If a data file's year field doesn't match *year*.
        UnsupportedTaxYearError: If the bundle has no surtax file for *year*.
    """
    reg_file, com_file = f"surtax/regional/{year}.json", f"surtax/municipal/{year}.json"
    try:
        reg_raw = read_resource(reg_file)
        com_raw = read_resource(com_file)
    except FileNotFoundError as exc:
        raise UnsupportedTaxYearError(year, supported=supported_tax_years()) from exc
    reg_payload = json.loads(reg_raw)
    com_payload = json.loads(com_raw)
    _verify_payload(reg_payload, reg_file)
    _verify_payload(com_payload, com_file)
    if reg_payload.get("year") != year:
        msg = (
            f"{reg_file} year={reg_payload.get('year')!r} "
            f"does not match requested year={year!r}"
        )
        raise DataIntegrityError(msg)
    if com_payload.get("year") != year:
        msg = (
            f"{com_file} year={com_payload.get('year')!r} "
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
        regional_provenance=reg.provenance,
        municipal_provenance=com.provenance,
        comunale_rates_are_advance=com.rates_are_advance,
        comunale_advance_fraction=com.advance_fraction,
    )


def _verify_payload(payload: dict[str, Any], filename: str) -> None:
    """Verify the ``ruleset.source_hash`` and the provenance labels.

    Args:
        payload: The full JSON payload dict.
        filename: Source file name, included in any error message.
    """
    verify_ruleset_hash(payload, filename)
    verify_provenance_labels(payload, filename)
