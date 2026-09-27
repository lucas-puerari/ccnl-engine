"""Tests for the CCNL schema: strict keys, legacy coercion and provenance.

Covers extra-key rejection, schema 0.4 meta coercion, schema 0.5 provenance
completeness and positive constraints on CCNLParameters.
"""

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.compensation import CCNLParameters
from ccnl_engine.contract.domain.identity import CCNL, CCNLMeta
from ccnl_engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.provenance.domain.source import SourceKind
from tests.helpers import TEST_PROV, make_ccnl_dict

_SERIES = {"periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "1"}]}


def _series(value: str, valid_from: str = "2020-01-01") -> dict[str, Any]:
    return {
        "periods": [{"valid_from": valid_from, "valid_until": None, "value": value}]
    }


def _validate(data: dict[str, Any]) -> CCNL:
    return CCNL.model_validate(data)


# ---------------------------------------------------------------------------
# Strict schema
# ---------------------------------------------------------------------------


class TestStrictSchema:
    """extra="forbid" on every model."""

    def test_misplaced_apprenticeship_raises(self) -> None:
        """An apprenticeship block inside parameters is rejected, not ignored."""
        data = make_ccnl_dict()
        data["parameters"]["apprenticeship"] = None
        with pytest.raises(ValidationError, match="Extra inputs"):
            _validate(data)

    def test_unknown_root_key_raises(self) -> None:
        """Unknown root keys are rejected."""
        data = make_ccnl_dict()
        data["foo"] = 1
        with pytest.raises(ValidationError, match="Extra inputs"):
            _validate(data)

    def test_optional_metadata_accepted(self) -> None:
        """agreement_date, validity and source notes are modelled."""
        data = make_ccnl_dict()
        data["meta"]["agreement_date"] = "2024-03-22"
        data["meta"]["validity"] = {"valid_from": "2024-04-01", "valid_until": None}
        data["meta"]["sources"][0]["notes"] = "salary tables"
        ccnl = _validate(data)
        assert ccnl.meta.validity is not None
        assert ccnl.meta.validity.valid_until is None


# ---------------------------------------------------------------------------
# Legacy schema 0.4 coercion
# ---------------------------------------------------------------------------


class TestMetaLegacyCoercion:
    """meta.sources/extraction are coerced from schema 0.4 to StructuredProvenance."""

    def test_non_dict_input_passes_through(self) -> None:
        """A non-dict value is returned untouched by the before-validator."""
        with pytest.raises(ValidationError):
            CCNLMeta.model_validate("not-a-dict")

    def test_structured_sources_are_not_coerced(self) -> None:
        """Sources already carrying a document_id pass through unchanged."""
        data = make_ccnl_dict()
        data["meta"]["sources"] = [
            {
                "document_id": "doc-1",
                "title": "T",
                "kind": "gazzetta",
                "url": "https://example.com",
            }
        ]
        ccnl = _validate(data)
        assert ccnl.meta.sources[0].document_id == "doc-1"
        assert ccnl.meta.sources[0].kind == SourceKind.GAZZETTA
        assert isinstance(ccnl.meta.extraction, ExtractionTrace)

    def test_structured_extraction_is_not_coerced(self) -> None:
        """Extraction traces already carrying a timestamp pass through."""
        data = make_ccnl_dict()
        data["meta"]["extraction"] = {
            "method": "manual",
            "model": None,
            "extraction_timestamp": "2026-01-01T00:00:00",
            "effective_from": "2026-01-01",
            "verification_status": "unverified",
        }
        ccnl = _validate(data)
        assert ccnl.meta.extraction.method.value == "manual"
        assert ccnl.meta.extraction.effective_from == date(2026, 1, 1)

    @pytest.mark.parametrize(
        ("source_type", "expected"),
        [
            ("tabella retributiva", SourceKind.TABELLA_RETRIBUTIVA),
            ("gazzetta ufficiale", SourceKind.GAZZETTA),
            ("cnel", SourceKind.CNEL),
            ("circolare inps", SourceKind.INPS_CIRCOLARE),
            ("legge 81", SourceKind.LEGGE),
            ("dpr", SourceKind.DPR),
            ("decreto", SourceKind.DL),
            ("associazione", SourceKind.ASSOCIAZIONE),
            ("ccnl", SourceKind.ALTRO),
        ],
    )
    def test_legacy_source_type_casts_to_kind(
        self, source_type: str, expected: SourceKind
    ) -> None:
        """Legacy 0.4 source type strings map to the matching SourceKind."""
        data = make_ccnl_dict()
        data["meta"]["sources"] = [{"url": "https://example.com", "type": source_type}]
        ccnl = _validate(data)
        assert ccnl.meta.sources[0].kind == expected


# ---------------------------------------------------------------------------
# Schema 0.5 provenance completeness
# ---------------------------------------------------------------------------

_PROV = TEST_PROV


def _make_v5_dict() -> dict[str, Any]:
    """Minimal schema-0.5 dict with provenance on every required rule.

    Returns:
        A dict suitable for CCNL.model_validate() with schema_version="0.5".
    """
    data = make_ccnl_dict(app_type="")
    data["schema_version"] = "0.5"
    si = data["parameters"]["seniority_increments"]
    si["provenance"] = _PROV
    for level in data["levels"]:
        level["provenance"] = _PROV
        for period in level["base_salary"]["periods"]:
            period["provenance"] = _PROV
    return data


class TestSchema05ProvenanceRequired:
    """schema_version 0.5 requires provenance on every rule."""

    def test_complete_provenance_accepted(self) -> None:
        """A fully-populated 0.5 dict loads without errors."""
        _validate(_make_v5_dict())

    def test_missing_level_provenance_raises(self) -> None:
        """A level without provenance in schema 0.5 raises ValidationError."""
        data = _make_v5_dict()
        del data["levels"][0]["provenance"]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_missing_period_provenance_raises(self) -> None:
        """A salary period without provenance in schema 0.5 raises ValidationError."""
        data = _make_v5_dict()
        del data["levels"][0]["base_salary"]["periods"][0]["provenance"]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_missing_seniority_provenance_raises(self) -> None:
        """Missing seniority_increments.provenance in 0.5 raises ValidationError."""
        data = _make_v5_dict()
        del data["parameters"]["seniority_increments"]["provenance"]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_missing_allowance_provenance_raises(self) -> None:
        """An allowance without provenance in schema 0.5 raises ValidationError."""
        data = _make_v5_dict()
        data["levels"][0]["fixed_allowances"] = [
            {"code": "X", "description": "X", "monthly": _SERIES}
        ]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_schema_04_without_provenance_rejected(self) -> None:
        """schema_version 0.4 files without provenance are also rejected."""
        data = make_ccnl_dict(app_type="")
        assert data["schema_version"] == "0.4"
        # Strip provenance from seniority_increments to trigger the validator.
        data["parameters"]["seniority_increments"].pop("provenance", None)
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_gap_period_needs_no_provenance(self) -> None:
        """A gap period in a 0.5 file is exempt from the provenance requirement."""
        data = _make_v5_dict()
        # Insert a gap before the existing period (all periods have provenance via
        # _make_v5_dict; the gap has none — this must still pass).
        original = data["levels"][0]["base_salary"]["periods"][0]
        data["levels"][0]["base_salary"]["periods"] = [
            {
                "valid_from": "2019-01-01",
                "valid_until": "2020-01-01",
                "gap_kind": "missing",
                # deliberately no provenance
            },
            {**original, "valid_from": "2020-01-01"},
        ]
        _validate(data)  # must not raise


# ---------------------------------------------------------------------------
# CCNLParameters positive constraints
# ---------------------------------------------------------------------------


class TestCCNLParametersPositiveConstraints:
    """CCNLParameters rejects non-positive hourly_divisor or additional_months."""

    def _make_params(
        self,
        hourly_divisor: str = "168",
        additional_months: str = "12",
    ) -> dict[str, Any]:
        si = make_ccnl_dict()["parameters"]["seniority_increments"]
        return {
            "hourly_divisor": _series(hourly_divisor),
            "additional_months": _series(additional_months),
            "seniority_increments": si,
        }

    def test_zero_hourly_divisor_raises(self) -> None:
        """hourly_divisor=0 is rejected."""
        with pytest.raises(ValidationError, match="hourly_divisor"):
            CCNLParameters.model_validate(self._make_params(hourly_divisor="0"))

    def test_negative_hourly_divisor_raises(self) -> None:
        """hourly_divisor < 0 is rejected."""
        with pytest.raises(ValidationError, match="hourly_divisor"):
            CCNLParameters.model_validate(self._make_params(hourly_divisor="-1"))

    def test_zero_additional_months_raises(self) -> None:
        """additional_months=0 is rejected."""
        with pytest.raises(ValidationError, match="additional_months"):
            CCNLParameters.model_validate(self._make_params(additional_months="0"))

    def test_negative_additional_months_raises(self) -> None:
        """additional_months < 0 is rejected."""
        with pytest.raises(ValidationError, match="additional_months"):
            CCNLParameters.model_validate(self._make_params(additional_months="-14"))

    def test_positive_values_accepted(self) -> None:
        """Valid positive values pass validation."""
        params = CCNLParameters.model_validate(
            self._make_params(hourly_divisor="173", additional_months="14")
        )
        assert params.hourly_divisor is not None
        assert params.additional_months is not None
