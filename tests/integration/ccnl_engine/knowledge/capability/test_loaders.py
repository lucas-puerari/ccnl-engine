"""Capability registry loader: the bundled registry and the rejected documents."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

import ccnl_engine.knowledge.capability.loaders as _catalog_mod
from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
    parse_capability_catalog,
)
from ccnl_engine.payroll.assurance.models import EvidenceStatus
from ccnl_engine.payroll.capability.models_catalog import (
    CapabilityApplicability,
    CapabilityCatalog,
    CapabilityHandler,
    CapabilityImplementation,
    CapabilityLayer,
)

_IRPEF: dict[str, Any] = {
    "feature": "irpef",
    "layer": "net",
    "implementation": "native",
    "applies_when": "always",
    "handler": "pipeline",
    "evidence": "derived",
}

#: The capabilities no 2026 run computes, each with its predicate.
_UNSUPPORTED_2026 = {
    "inail": "outside_input",
    "contribution_exemption": "outside_input",
    "fiscal_adjustment": "outside_input",
    "maternity_leave": "outside_input",
    "workplace_injury": "outside_input",
    "termination_residual_leave": "termination_run",
    "una_tantum": "outside_input",
    "personal_withholdings": "outside_input",
    "additional_irpef_base": "outside_input",
    "health_fund_employee": "outside_input",
    "health_fund_employer": "outside_input",
    "territorial_supplement": "outside_input",
    "company_supplement": "outside_input",
    "art15_deductions": "outside_input",
    "leave": "outside_input",
}


def _doc(*entries: object, schema_version: int = 2) -> dict[str, object]:
    return {"year": 2026, "schema_version": schema_version, "capabilities": [*entries]}


class TestBundledRegistry:
    """The 2026 registry loads with every field of an entry."""

    def test_entry_fields(self) -> None:
        """An entry carries layer, implementation, predicate and handler."""
        entry = load_capability_catalog(2026).by_feature("family_deductions")
        assert entry is not None
        assert entry.layer is CapabilityLayer.NET
        assert entry.implementation is CapabilityImplementation.NATIVE
        assert entry.applies_when is CapabilityApplicability.DECIDED
        assert entry.handler is CapabilityHandler.DECISION
        assert entry.evidence is EvidenceStatus.DERIVED
        assert entry.required_facts == ("facts.family_composition", "current_year")
        assert entry.applicability_facts == ("facts.family_composition",)
        assert "spouse_increase_bands" in entry.variants

    def test_unsupported_capabilities_and_predicates(self) -> None:
        """The fifteen unsupported capabilities name when they apply."""
        catalog = load_capability_catalog(2026)
        unsupported = {
            e.feature: e.applies_when.value
            for e in catalog.capabilities
            if e.implementation is CapabilityImplementation.UNSUPPORTED
        }
        assert unsupported == _UNSUPPORTED_2026

    def test_sickness_is_native(self) -> None:
        """Sickness episodes are computed from the bundle rules."""
        entry = load_capability_catalog(2026).by_feature("sickness")
        assert entry is not None
        assert entry.implementation is CapabilityImplementation.NATIVE

    def test_cached_returns_same_object(self) -> None:
        """Repeated calls for the same year return the identical object."""
        assert load_capability_catalog(2026) is load_capability_catalog(2026)


def _call_uncached(raw: str, year: int = 9999) -> CapabilityCatalog:
    with patch.object(_catalog_mod, "read_resource", return_value=raw):
        return _catalog_mod._load_cached.__wrapped__(year)


class TestReadErrors:
    """A missing or unreadable file is a data integrity error."""

    def test_missing_file_raises(self) -> None:
        """FileNotFoundError from read_resource is wrapped in DataIntegrityError."""
        with (
            patch.object(_catalog_mod, "read_resource", side_effect=FileNotFoundError),
            pytest.raises(DataIntegrityError, match="not found"),
        ):
            _catalog_mod._load_cached.__wrapped__(8888)

    def test_invalid_json_raises(self) -> None:
        """Invalid JSON content raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="not valid JSON"):
            _call_uncached("NOT JSON{{")

    def test_valid_document_loads(self) -> None:
        """A valid document read from the bundle becomes a catalog."""
        catalog = _call_uncached(json.dumps(_doc(_IRPEF)))
        assert catalog.year == 9999
        assert not catalog.capabilities[0].description


class TestRejectedDocuments:
    """The loader rejects a malformed or contradictory registry."""

    @pytest.mark.parametrize(
        ("data", "match"),
        [
            ([1, 2], "expected object"),
            (_doc(schema_version=1), "schema_version must be 2"),
            ({"schema_version": 2, "capabilities": "oops"}, "must be a list"),
            (_doc("not-a-dict"), "not an object"),
            (_doc({"layer": "net"}), "missing 'feature'"),
            (_doc({**_IRPEF, "feature": ""}), "missing 'feature'"),
            (_doc({**_IRPEF, "implementation": "computed"}), "irpef"),
            (_doc({**_IRPEF, "applies_when": "sometimes"}), "irpef"),
            (_doc({k: v for k, v in _IRPEF.items() if k != "handler"}), "handler"),
            (_doc({**_IRPEF, "variants": "all"}), "list of strings"),
            (_doc({**_IRPEF, "required_facts": [1]}), "list of strings"),
            (_doc(_IRPEF, _IRPEF), "duplicate features"),
        ],
    )
    def test_malformed(self, data: object, match: str) -> None:
        """Each malformation names what is wrong."""
        with pytest.raises(DataIntegrityError, match=match):
            parse_capability_catalog(2026, data)

    def test_unsupported_with_handler(self) -> None:
        """A handler would claim a decision the engine does not take."""
        entry = {**_IRPEF, "implementation": "unsupported"}
        with pytest.raises(DataIntegrityError, match="unsupported capability"):
            parse_capability_catalog(2026, _doc(entry))

    def test_computed_without_handler(self) -> None:
        """A computed capability without a handler is rejected at load."""
        entry = {**_IRPEF, "handler": None}
        with pytest.raises(DataIntegrityError, match="every other one has one"):
            parse_capability_catalog(2026, _doc(entry))
