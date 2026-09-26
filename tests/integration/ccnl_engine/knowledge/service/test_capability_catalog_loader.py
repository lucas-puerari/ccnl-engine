"""Tests for the capability catalog loader and CapabilityCatalog domain types."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

import ccnl_engine.knowledge.service.capability_catalog_loader as _catalog_mod
from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityGap,
    CapabilityGapKind,
    CapabilityReport,
    CapabilityStatus,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError

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


class TestCapabilityGapKind:
    """CapabilityGapKind StrEnum coverage."""

    def test_values(self) -> None:
        """All members expose their string value."""
        assert CapabilityGapKind.NOT_COMPUTED.value == "not_computed"
        assert CapabilityGapKind.FEATURE_ABSENT.value == "feature_absent"
        assert CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL.value == (
            "promised_computed_got_partial"
        )
        assert CapabilityGapKind.WRONG_YEAR.value == "wrong_year"
        assert CapabilityGapKind.UNRESOLVED.value == "unresolved"

    def test_from_string(self) -> None:
        """Constructing from string returns the enum member."""
        assert CapabilityGapKind("feature_absent") is CapabilityGapKind.FEATURE_ABSENT


class TestCapabilityGap:
    """CapabilityGap frozen dataclass."""

    def test_fields(self) -> None:
        """Gap stores feature, declared, observed, and defaults kind to NOT_COMPUTED."""
        gap = CapabilityGap(
            feature="irpef",
            declared=CapabilityStatus.COMPUTED,
            observed="not_computed",
        )
        assert gap.feature == "irpef"
        assert gap.declared == CapabilityStatus.COMPUTED
        assert gap.observed == "not_computed"
        assert gap.kind == CapabilityGapKind.NOT_COMPUTED

    def test_explicit_kind(self) -> None:
        """An explicit kind overrides the default."""
        gap = CapabilityGap(
            feature="overtime",
            declared=CapabilityStatus.COMPUTED,
            observed="absent",
            kind=CapabilityGapKind.FEATURE_ABSENT,
        )
        assert gap.kind == CapabilityGapKind.FEATURE_ABSENT


# ---------------------------------------------------------------------------
# CapabilityReport
# ---------------------------------------------------------------------------


class TestCapabilityReport:
    """CapabilityReport dataclass: empty factory, status, confidence."""

    def test_empty_is_complete(self) -> None:
        """An empty report has status 'complete' and confidence 'high'."""
        report = CapabilityReport.empty(2026)
        assert report.catalog_year == 2026
        assert report.gaps == ()
        assert report.status == "complete"
        assert report.confidence == "high"

    def test_only_partial_gaps_is_partial(self) -> None:
        """A report with only PROMISED_COMPUTED_GOT_PARTIAL gaps is 'partial'."""
        gap = CapabilityGap(
            feature="irpef",
            declared=CapabilityStatus.COMPUTED,
            observed="partially_computed",
            kind=CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL,
        )
        report = CapabilityReport(catalog_year=2026, gaps=(gap,))
        assert report.status == "partial"
        assert report.confidence == "medium"

    def test_feature_absent_gap_is_incomplete(self) -> None:
        """A report with FEATURE_ABSENT gaps is 'incomplete' / 'low' confidence."""
        gap = CapabilityGap(
            feature="overtime",
            declared=CapabilityStatus.COMPUTED,
            observed="absent",
            kind=CapabilityGapKind.FEATURE_ABSENT,
        )
        report = CapabilityReport(catalog_year=2026, gaps=(gap,))
        assert report.status == "incomplete"
        assert report.confidence == "low"

    def test_mixed_gaps_is_incomplete(self) -> None:
        """Mixed gap kinds result in 'incomplete' status."""
        gaps = (
            CapabilityGap(
                feature="irpef",
                declared=CapabilityStatus.COMPUTED,
                observed="partially_computed",
                kind=CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL,
            ),
            CapabilityGap(
                feature="overtime",
                declared=CapabilityStatus.COMPUTED,
                observed="absent",
                kind=CapabilityGapKind.FEATURE_ABSENT,
            ),
        )
        report = CapabilityReport(catalog_year=2026, gaps=gaps)
        assert report.status == "incomplete"

    def test_frozen(self) -> None:
        """CapabilityReport is immutable."""
        report = CapabilityReport.empty(2026)
        with pytest.raises(FrozenInstanceError):
            report.catalog_year = 2027  # type: ignore[misc]


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

    def test_gaps_detect_absent_reports_missing_features(self) -> None:
        """detect_absent=True reports absent features as FEATURE_ABSENT."""
        cat = self._make()
        gaps = cat.gaps({}, detect_absent=True)
        features = {g.feature for g in gaps}
        assert "base_salary" in features
        assert "irpef" in features
        assert "art15_deductions" in features
        for gap in gaps:
            assert gap.kind == CapabilityGapKind.FEATURE_ABSENT
            assert gap.observed == "absent"

    def test_gaps_detect_absent_false_skips_missing(self) -> None:
        """detect_absent=False (default) does not report absent features."""
        cat = self._make()
        assert cat.gaps({}, detect_absent=False) == ()

    def test_gaps_wrong_year_prepended(self) -> None:
        """Passing a year differing from catalog.year prepends a WRONG_YEAR gap."""
        cat = self._make()
        gaps = cat.gaps({}, year=2025)
        assert len(gaps) >= 1
        first = gaps[0]
        assert first.kind == CapabilityGapKind.WRONG_YEAR
        assert first.feature == "__catalog__"
        assert first.observed == "2025"

    def test_gaps_matching_year_no_wrong_year_gap(self) -> None:
        """Passing the correct year does not produce a WRONG_YEAR gap."""
        cat = self._make()
        gaps = cat.gaps({"base_salary": "computed", "irpef": "computed"}, year=2026)
        assert not any(g.kind == CapabilityGapKind.WRONG_YEAR for g in gaps)

    def test_gaps_promised_computed_got_partial(self) -> None:
        """A computed entry observed as partially_computed gets that gap kind."""
        cat = self._make()
        gaps = cat.gaps({"irpef": "partially_computed"})
        assert len(gaps) == 1
        assert gaps[0].kind == CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL
        assert gaps[0].observed == "partially_computed"

    def test_gaps_partially_computed_entry_observed_partial_no_gap(self) -> None:
        """A partially_computed entry observed as partially_computed is not a gap."""
        cat = self._make()
        gaps = cat.gaps({"art15_deductions": "partially_computed"})
        assert gaps == ()

    def test_gaps_not_computed_kind_on_not_computed_observed(self) -> None:
        """A computed entry observed as not_computed has kind NOT_COMPUTED."""
        cat = self._make()
        gaps = cat.gaps({"base_salary": "not_computed"})
        assert len(gaps) == 1
        assert gaps[0].kind == CapabilityGapKind.NOT_COMPUTED


class TestCapabilityCatalogTraceStates:
    """Gaps classify the trace states a run reports for each feature."""

    def _make(self) -> CapabilityCatalog:
        return CapabilityCatalog(
            year=2026,
            capabilities=(
                CapabilityEntry("irpef", CapabilityStatus.COMPUTED),
                CapabilityEntry(
                    "art15_deductions", CapabilityStatus.PARTIALLY_COMPUTED
                ),
                CapabilityEntry("bonus_pdr", CapabilityStatus.NOT_APPLICABLE),
            ),
        )

    @pytest.mark.parametrize("feature", ["irpef", "art15_deductions"])
    def test_gaps_unresolved_is_a_gap(self, feature: str) -> None:
        """A promised feature that ran but could not decide is an UNRESOLVED gap."""
        (gap,) = self._make().gaps({feature: "unresolved"})
        assert gap.feature == feature
        assert gap.kind is CapabilityGapKind.UNRESOLVED
        assert gap.observed == "unresolved"

    def test_gaps_unresolved_on_not_applicable_entry_no_gap(self) -> None:
        """A feature the catalog does not promise is never a gap."""
        assert self._make().gaps({"bonus_pdr": "unresolved"}) == ()

    def test_gaps_trace_partial_is_promised_computed_got_partial(self) -> None:
        """The trace state ``partial`` breaks a ``computed`` promise."""
        (gap,) = self._make().gaps({"irpef": "partial"})
        assert gap.kind is CapabilityGapKind.PROMISED_COMPUTED_GOT_PARTIAL
        assert gap.observed == "partial"

    def test_gaps_trace_partial_keeps_partially_computed_promise(self) -> None:
        """The trace state ``partial`` keeps a ``partially_computed`` promise."""
        assert self._make().gaps({"art15_deductions": "partial"}) == ()

    @pytest.mark.parametrize("state", ["skipped", "not_applicable", "computed"])
    def test_gaps_other_trace_states_are_not_gaps(self, state: str) -> None:
        """Skipped, not applicable and computed keep the promise."""
        assert self._make().gaps({"irpef": state}) == ()


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
