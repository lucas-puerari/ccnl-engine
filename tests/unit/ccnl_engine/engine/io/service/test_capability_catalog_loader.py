"""Tests for the capability catalog loader and CapabilityCatalog domain types."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

import ccnl_engine.engine.io.service.capability_catalog_loader as _catalog_mod
from ccnl_engine.engine.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityStatus,
)
from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.io.service.capability_catalog_loader import (
    load_capability_catalog,
)

# ---------------------------------------------------------------------------
# CapabilityStatus enum
# ---------------------------------------------------------------------------


class TestCapabilityStatus:
    """CapabilityStatus StrEnum coverage."""

    def test_values_are_strings(self) -> None:
        """All enum members expose their string value via .value."""
        assert CapabilityStatus.COMPUTED.value == "computed"
        assert CapabilityStatus.NOT_COMPUTED.value == "not_computed"
        assert CapabilityStatus.PARTIALLY_COMPUTED.value == "partially_computed"
        assert CapabilityStatus.NOT_APPLICABLE.value == "not_applicable"
        assert CapabilityStatus.BLOCKED.value == "blocked"

    def test_from_string(self) -> None:
        """Constructing from string returns the enum member."""
        assert CapabilityStatus("computed") is CapabilityStatus.COMPUTED


# ---------------------------------------------------------------------------
# CapabilityEntry
# ---------------------------------------------------------------------------


class TestCapabilityEntry:
    """CapabilityEntry frozen dataclass."""

    def test_defaults(self) -> None:
        """Description defaults to empty string."""
        entry = CapabilityEntry(feature="base_salary", status=CapabilityStatus.COMPUTED)
        assert not entry.description

    def test_with_description(self) -> None:
        """All fields are stored correctly."""
        entry = CapabilityEntry(
            feature="irpef",
            status=CapabilityStatus.PARTIALLY_COMPUTED,
            description="IRPEF sostituto",
        )
        assert entry.feature == "irpef"
        assert entry.status == CapabilityStatus.PARTIALLY_COMPUTED
        assert entry.description == "IRPEF sostituto"

    def test_frozen(self) -> None:
        """Assigning to a field raises FrozenInstanceError."""
        entry = CapabilityEntry(feature="f", status=CapabilityStatus.COMPUTED)
        with pytest.raises(FrozenInstanceError):
            entry.feature = "g"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# CapabilityGap
# ---------------------------------------------------------------------------


class TestCapabilityGap:
    """CapabilityGap frozen dataclass."""

    def test_fields(self) -> None:
        """Gap stores feature, declared, and observed."""
        gap = CapabilityGap(
            feature="irpef",
            declared=CapabilityStatus.COMPUTED,
            observed="not_computed",
        )
        assert gap.feature == "irpef"
        assert gap.declared == CapabilityStatus.COMPUTED
        assert gap.observed == "not_computed"


# ---------------------------------------------------------------------------
# CapabilityCatalog
# ---------------------------------------------------------------------------


class TestCapabilityCatalog:
    """CapabilityCatalog frozen dataclass with by_feature and gaps."""

    def _make(self) -> CapabilityCatalog:
        return CapabilityCatalog(
            year=2026,
            capabilities=(
                CapabilityEntry("base_salary", CapabilityStatus.COMPUTED),
                CapabilityEntry("irpef", CapabilityStatus.COMPUTED),
                CapabilityEntry(
                    "art15_deductions", CapabilityStatus.PARTIALLY_COMPUTED
                ),
                CapabilityEntry("bonus_pdr", CapabilityStatus.NOT_APPLICABLE),
                CapabilityEntry("blocked_feat", CapabilityStatus.BLOCKED),
            ),
        )

    def test_by_feature_found(self) -> None:
        """by_feature returns the entry when the feature is present."""
        cat = self._make()
        entry = cat.by_feature("irpef")
        assert entry is not None
        assert entry.feature == "irpef"

    def test_by_feature_not_found(self) -> None:
        """by_feature returns None when the feature is absent."""
        cat = self._make()
        assert cat.by_feature("unknown_feature") is None

    def test_gaps_empty_when_all_computed(self) -> None:
        """No gaps when observed status matches or exceeds declared."""
        cat = self._make()
        observed = {"base_salary": "computed", "irpef": "computed"}
        assert cat.gaps(observed) == ()

    def test_gaps_reports_not_computed(self) -> None:
        """A computed entry with observed not_computed is a gap."""
        cat = self._make()
        observed = {"base_salary": "computed", "irpef": "not_computed"}
        gaps = cat.gaps(observed)
        assert len(gaps) == 1
        assert gaps[0].feature == "irpef"
        assert gaps[0].declared == CapabilityStatus.COMPUTED
        assert gaps[0].observed == "not_computed"

    def test_gaps_partially_computed_entry_also_checked(self) -> None:
        """A partially_computed entry with observed not_computed is a gap."""
        cat = self._make()
        observed = {"art15_deductions": "not_computed"}
        gaps = cat.gaps(observed)
        assert len(gaps) == 1
        assert gaps[0].feature == "art15_deductions"

    def test_gaps_skips_not_applicable(self) -> None:
        """Not_applicable entries are not reported as gaps."""
        cat = self._make()
        assert cat.gaps({"bonus_pdr": "not_computed"}) == ()

    def test_gaps_skips_blocked(self) -> None:
        """Blocked entries are not reported as gaps."""
        cat = self._make()
        assert cat.gaps({"blocked_feat": "not_computed"}) == ()

    def test_gaps_feature_absent_from_observed(self) -> None:
        """A feature absent from observed is not a gap (None != not_computed)."""
        cat = self._make()
        assert cat.gaps({}) == ()

    def test_gaps_multiple(self) -> None:
        """Multiple gaps are returned in declaration order."""
        cat = self._make()
        observed = {
            "base_salary": "not_computed",
            "irpef": "not_computed",
            "art15_deductions": "computed",
        }
        gaps = cat.gaps(observed)
        assert len(gaps) == 2
        assert {g.feature for g in gaps} == {"base_salary", "irpef"}


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
            "base_salary", "seniority", "inps_employee", "inps_employer",
            "tfr", "irpef", "trattamento_integrativo", "ulteriore_detrazione_lavoro",
            "addizionale_regionale", "addizionale_comunale",
            "family_deductions", "art15_deductions",
            "overtime", "night_work", "holiday_work",
            "absence", "leave", "sickness",
            "fringe_benefit", "welfare", "bonus_pdr", "bilateral_funds",
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
    with patch.object(_catalog_mod, "importlib") as mock_importlib, patch.object(
        _catalog_mod, "read_bundled", return_value=raw
    ):
        mock_importlib.resources.files.return_value = MagicMock()
        return _catalog_mod._load_cached.__wrapped__(year)


def _call_uncached_file_not_found(year: int = 8888) -> None:
    with patch.object(_catalog_mod, "importlib") as mock_importlib, patch.object(
        _catalog_mod, "read_bundled", side_effect=FileNotFoundError
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
