"""Capability registry loader: reads versioned JSON from the knowledge bundle.

The loader rejects an entry whose fields contradict each other (see
:class:`~ccnl_engine.payroll.capability.models_catalog.CapabilityEntry`).
That every implemented capability has a registered handler that the run
traces is checked where the handlers live, before the first report of a
run (:mod:`~ccnl_engine.payroll.capability.services_registry`).
"""

from __future__ import annotations

import json
from functools import cache
from typing import Any

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.knowledge.loaders_manifest import read_resource
from ccnl_engine.payroll.assurance.models import EvidenceStatus
from ccnl_engine.payroll.capability.models_catalog import (
    CapabilityApplicability,
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityHandler,
    CapabilityImplementation,
    CapabilityLayer,
)

_SCHEMA_VERSION = 2


def load_capability_catalog(year: int) -> CapabilityCatalog:
    """Load the capability registry for *year* from the bundled data files.

    Reads ``capability/{year}/catalog.json`` of the knowledge manifest.
    In installed wheels the compressed ``.json.gz`` variant is preferred.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        A :class:`~ccnl_engine.payroll.capability.models_catalog.CapabilityCatalog`
        with all declared capabilities for the requested year; a missing,
        malformed or inconsistent file raises
        :class:`~ccnl_engine.errors.DataIntegrityError`.
    """
    return _load_cached(year)


@cache
def _load_cached(year: int) -> CapabilityCatalog:
    try:
        raw = read_resource(f"capability/{year}/catalog.json")
    except FileNotFoundError as exc:
        msg = f"Capability catalog for {year} not found in bundle"
        raise DataIntegrityError(msg) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = f"Capability catalog for {year} is not valid JSON: {exc}"
        raise DataIntegrityError(msg) from exc
    return parse_capability_catalog(year, data)


def parse_capability_catalog(year: int, data: object) -> CapabilityCatalog:
    """Build the registry of *year* from its decoded JSON document.

    Returns:
        The capability catalog.

    Raises:
        DataIntegrityError: When the document or one of its entries is
            malformed or inconsistent.
    """
    if not isinstance(data, dict):
        msg = (
            f"Capability catalog for {year}: expected object, got {type(data).__name__}"
        )
        raise DataIntegrityError(msg)
    if data.get("schema_version") != _SCHEMA_VERSION:
        msg = (
            f"Capability catalog for {year}: schema_version must be "
            f"{_SCHEMA_VERSION}, got {data.get('schema_version')!r}"
        )
        raise DataIntegrityError(msg)
    raw_caps = data.get("capabilities")
    if not isinstance(raw_caps, list):
        msg = f"Capability catalog for {year}: 'capabilities' must be a list"
        raise DataIntegrityError(msg)
    entries = tuple(_entry(year, i, cap) for i, cap in enumerate(raw_caps))
    try:
        return CapabilityCatalog(year=year, capabilities=entries)
    except ValueError as exc:
        raise DataIntegrityError(str(exc)) from exc


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        msg = f"expected a list of strings, got {value!r}"
        raise TypeError(msg)
    return tuple(value)


def _entry(year: int, index: int, cap: object) -> CapabilityEntry:
    where = f"Capability catalog for {year}: entry {index}"
    if not isinstance(cap, dict):
        msg = f"{where} is not an object"
        raise DataIntegrityError(msg)
    feature = cap.get("feature")
    if not isinstance(feature, str) or not feature:
        msg = f"{where} missing 'feature'"
        raise DataIntegrityError(msg)
    try:
        return _build_entry(feature, cap)
    except (KeyError, TypeError, ValueError) as exc:
        msg = f"{where} ({feature}): {exc}"
        raise DataIntegrityError(msg) from exc


def _build_entry(feature: str, cap: dict[str, Any]) -> CapabilityEntry:
    handler = cap["handler"]
    return CapabilityEntry(
        feature=feature,
        layer=CapabilityLayer(cap["layer"]),
        implementation=CapabilityImplementation(cap["implementation"]),
        applies_when=CapabilityApplicability(cap["applies_when"]),
        handler=None if handler is None else CapabilityHandler(handler),
        evidence=EvidenceStatus(cap["evidence"]),
        description=str(cap.get("description", "")),
        variants=_strings(cap.get("variants", [])),
        required_facts=_strings(cap.get("required_facts", [])),
        applicability_facts=_strings(cap.get("applicability_facts", [])),
    )
