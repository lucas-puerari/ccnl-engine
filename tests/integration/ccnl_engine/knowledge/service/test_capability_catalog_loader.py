"""Tests for the capability catalog loader: bundled catalog and error branches."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

import ccnl_engine.knowledge.service.capability_catalog_loader as _catalog_mod
from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityCatalog,
    CapabilityStatus,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError

# ---------------------------------------------------------------------------
# load_capability_catalog (loader) — happy path
# ---------------------------------------------------------------------------


def _raw(capabilities: list[dict]) -> str:  # type: ignore[type-arg]
    return json.dumps({"year": 2026, "schema_version": 1, "capabilities": capabilities})


class TestLoadCapabilityCatalog:
    """Happy path: 2026 catalog loads and parses correctly."""

    def test_loads_2026(self) -> None:
        """The 2026 catalog is present in the bundle and parses without error."""
        cat = load_capability_catalog(2026)
        assert cat.year == 2026
        assert len(cat.capabilities) > 0
        entry = cat.by_feature("base_salary")
        assert entry is not None
        assert entry.status == CapabilityStatus.COMPUTED

    def test_2026_has_all_fiscal_features(self) -> None:
        """The 2026 catalog covers every feature emitted by scope.py."""
        cat = load_capability_catalog(2026)
        expected = {
            "base_salary",
            "seniority",
            "inps_employee",
            "inps_employer",
            "tfr",
            "irpef",
            "trattamento_integrativo",
            "ulteriore_detrazione_lavoro",
            "addizionale_regionale",
            "addizionale_comunale",
            "family_deductions",
            "art15_deductions",
            "overtime",
            "night_work",
            "holiday_work",
            "absence",
            "leave",
            "sickness",
            "fringe_benefit",
            "welfare",
            "bonus_pdr",
            "bilateral_funds",
        }
        found = {e.feature for e in cat.capabilities}
        assert expected <= found

    def test_cached_returns_same_object(self) -> None:
        """Repeated calls for the same year return the identical object."""
        a = load_capability_catalog(2026)
        b = load_capability_catalog(2026)
        assert a is b


# ---------------------------------------------------------------------------
# load_capability_catalog (loader) — error branches
# Bypass @cache using __wrapped__ (set by functools.lru_cache via functools.wraps)
# ---------------------------------------------------------------------------


def _call_uncached(raw: str, year: int = 9999) -> CapabilityCatalog:
    with (
        patch.object(_catalog_mod, "importlib") as mock_importlib,
        patch.object(_catalog_mod, "read_bundled", return_value=raw),
    ):
        mock_importlib.resources.files.return_value = MagicMock()
        return _catalog_mod._load_cached.__wrapped__(year)


def _call_uncached_file_not_found(year: int = 8888) -> None:
    with (
        patch.object(_catalog_mod, "importlib") as mock_importlib,
        patch.object(_catalog_mod, "read_bundled", side_effect=FileNotFoundError),
    ):
        mock_importlib.resources.files.return_value = MagicMock()
        _catalog_mod._load_cached.__wrapped__(year)


class TestLoadCapabilityCatalogErrors:
    """Error branches in the loader."""

    def test_missing_file_raises(self) -> None:
        """FileNotFoundError from read_bundled is wrapped in DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="not found"):
            _call_uncached_file_not_found()

    def test_invalid_json_raises(self) -> None:
        """Invalid JSON content raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="not valid JSON"):
            _call_uncached("NOT JSON{{")

    def test_non_dict_raises(self) -> None:
        """A JSON array at the top level raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="expected object"):
            _call_uncached("[1, 2]")

    def test_missing_capabilities_key_raises(self) -> None:
        """Missing 'capabilities' key raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="'capabilities' must be a list"):
            _call_uncached(json.dumps({"year": 9999}))

    def test_capabilities_not_list_raises(self) -> None:
        """Non-list 'capabilities' value raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="'capabilities' must be a list"):
            _call_uncached(json.dumps({"capabilities": "oops"}))

    def test_entry_not_dict_raises(self) -> None:
        """A capabilities entry that is not a dict raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="not an object"):
            _call_uncached(_raw(["not-a-dict"]))  # type: ignore[list-item]

    def test_entry_missing_feature_raises(self) -> None:
        """A capabilities entry without 'feature' raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="missing 'feature'"):
            _call_uncached(_raw([{"status": "computed"}]))

    def test_entry_empty_feature_raises(self) -> None:
        """An empty 'feature' string raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="missing 'feature'"):
            _call_uncached(_raw([{"feature": "", "status": "computed"}]))

    def test_unknown_status_raises(self) -> None:
        """An unrecognised string status value raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="unknown status"):
            _call_uncached(_raw([{"feature": "irpef", "status": "totally_unknown"}]))

    def test_non_string_status_raises(self) -> None:
        """A non-string status value raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="unknown status"):
            _call_uncached(_raw([{"feature": "irpef", "status": 42}]))

    def test_valid_entry_no_description(self) -> None:
        """An entry without 'description' defaults to empty string."""
        cat = _call_uncached(_raw([{"feature": "irpef", "status": "computed"}]))
        assert not cat.capabilities[0].description
