"""Capability catalog loader: reads versioned JSON from the knowledge bundle."""

from __future__ import annotations

import importlib.resources
import json
from functools import cache

from ccnl_engine.knowledge.service.bundled import read_bundled
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityStatus,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError


def load_capability_catalog(year: int) -> CapabilityCatalog:
    """Load the capability catalog for *year* from the bundled data files.

    Reads ``{year}.json`` from ``ccnl_engine/knowledge/capabilities/data/``.
    In installed wheels the compressed ``.json.gz`` variant is preferred.

    Args:
        year: Fiscal year (e.g. ``2026``).

    Returns:
        A :class:`~ccnl_engine.payroll.domain.capability_catalog.CapabilityCatalog`
        with all declared capabilities for the requested year.
    """
    return _load_cached(year)


@cache
def _load_cached(year: int) -> CapabilityCatalog:
    try:
        pkg = importlib.resources.files("ccnl_engine.knowledge.capabilities.data")
        raw = read_bundled(pkg, f"{year}.json")
    except FileNotFoundError as exc:
        msg = f"Capability catalog for {year} not found in bundle"
        raise DataIntegrityError(msg) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = f"Capability catalog for {year} is not valid JSON: {exc}"
        raise DataIntegrityError(msg) from exc

    if not isinstance(data, dict):
        msg = (
            f"Capability catalog for {year}: expected object, got {type(data).__name__}"
        )
        raise DataIntegrityError(msg)

    raw_caps = data.get("capabilities")
    if not isinstance(raw_caps, list):
        msg = f"Capability catalog for {year}: 'capabilities' must be a list"
        raise DataIntegrityError(msg)

    entries: list[CapabilityEntry] = []
    for i, cap in enumerate(raw_caps):
        if not isinstance(cap, dict):
            msg = f"Capability catalog for {year}: entry {i} is not an object"
            raise DataIntegrityError(msg)
        feature = cap.get("feature")
        status_raw = cap.get("status")
        if not isinstance(feature, str) or not feature:
            msg = f"Capability catalog for {year}: entry {i} missing 'feature'"
            raise DataIntegrityError(msg)
        if not isinstance(status_raw, str):
            msg = (
                f"Capability catalog for {year}: entry {i} "
                f"unknown status {status_raw!r}"
            )
            raise DataIntegrityError(msg)
        try:
            status = CapabilityStatus(status_raw)
        except ValueError as exc:
            msg = (
                f"Capability catalog for {year}: entry {i} "
                f"unknown status {status_raw!r}"
            )
            raise DataIntegrityError(msg) from exc
        entries.append(
            CapabilityEntry(
                feature=feature,
                status=status,
                description=cap.get("description", ""),
            )
        )

    return CapabilityCatalog(year=year, capabilities=tuple(entries))
