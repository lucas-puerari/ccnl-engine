"""Tests for the CCNL schema: strict keys, legacy coercion and provenance.

Covers extra-key rejection, schema 0.4 meta coercion, schema 0.6 provenance
completeness and positive constraints on CCNLParameters.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.compensation.models import CCNLParameters
from tests.unit.ccnl_engine.builders import TEST_PROV, make_ccnl_dict

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
        """agreement_date and validity are modelled."""
        data = make_ccnl_dict()
        data["meta"]["agreement_date"] = "2024-03-22"
        data["meta"]["validity"] = {"valid_from": "2024-04-01", "valid_until": None}
        ccnl = _validate(data)
        assert ccnl.meta.validity is not None
        assert ccnl.meta.validity.valid_until is None

    def test_public_pension_fund_is_for_the_public_administrations(self) -> None:
        """A fund of the Gestione Dipendenti Pubblici needs that sector."""
        data = make_ccnl_dict()
        data["meta"]["public_pension_fund"] = "cpdel"
        with pytest.raises(ValidationError, match="public administrations only"):
            _validate(data)
        data["meta"]["tax_sector"] = "pubblica-amministrazione"
        assert _validate(data).meta.public_pension_fund == "cpdel"

    def test_inps_sectors_hold_the_tax_sector(self) -> None:
        """The sectors of the employers include the one the CCNL reads."""
        data = make_ccnl_dict()
        data["meta"]["inps_sectors"] = ["industria", "credito"]
        with pytest.raises(ValidationError, match="must include the tax_sector"):
            _validate(data)
        data["meta"]["inps_sectors"] = [data["meta"]["tax_sector"], "industria"]
        assert "industria" in _validate(data).meta.inps_sectors  # type: ignore[operator]

    def test_contribution_relevant_false_is_rejected(self) -> None:
        """The engine never takes an allowance out of the INPS base."""
        data = make_ccnl_dict()
        data["levels"][0]["fixed_allowances"] = [
            {
                "code": "X",
                "description": "x",
                "monthly": _SERIES,
                "contribution_relevant": False,
            }
        ]
        with pytest.raises(ValidationError, match="contribution_relevant"):
            _validate(data)


# ---------------------------------------------------------------------------
# Legacy schema 0.4 coercion
# ---------------------------------------------------------------------------


class TestMetaLegacySchema:
    """Schema 0.4 metadata is rejected: the bundle was migrated, no coercion."""

    def test_a_legacy_source_is_rejected(self) -> None:
        """A source with ``url`` and ``type`` only is not a SourceDocument."""
        data = make_ccnl_dict()
        data["meta"]["sources"] = [{"url": "https://example.com", "type": "cnel"}]
        with pytest.raises(ValidationError, match="document_id"):
            _validate(data)

    def test_a_legacy_extraction_is_rejected(self) -> None:
        """An extraction with ``timestamp`` and ``human_reviewed`` is rejected."""
        data = make_ccnl_dict()
        data["meta"]["extraction"] = {
            "method": "ai",
            "timestamp": "2026-09-02",
            "human_reviewed": False,
        }
        with pytest.raises(ValidationError, match="extraction_timestamp"):
            _validate(data)

    def test_an_extraction_may_state_no_effective_date(self) -> None:
        """A source without a date leaves ``effective_from`` unknown."""
        data = make_ccnl_dict()
        data["meta"]["extraction"].pop("effective_from", None)
        assert _validate(data).meta.extraction.effective_from is None


_PROV = TEST_PROV


def _make_dict() -> dict[str, Any]:
    """Minimal schema-0.6 dict with provenance on every required rule.

    Returns:
        A dict suitable for CCNL.model_validate() with schema_version="0.6".
    """
    data = make_ccnl_dict(app_type="")
    data["schema_version"] = "0.6"
    si = data["parameters"]["seniority_increments"]
    si["provenance"] = _PROV
    for level in data["levels"]:
        level["provenance"] = _PROV
        for period in level["base_salary"]["periods"]:
            period["provenance"] = _PROV
    return data


class TestProvenanceRequired:
    """schema_version 0.6 requires provenance on every rule."""

    def test_complete_provenance_accepted(self) -> None:
        """A fully-populated 0.6 dict loads without errors."""
        _validate(_make_dict())

    def test_missing_level_provenance_raises(self) -> None:
        """A level without provenance in schema 0.6 raises ValidationError."""
        data = _make_dict()
        del data["levels"][0]["provenance"]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_missing_period_provenance_raises(self) -> None:
        """A salary period without provenance in schema 0.6 raises ValidationError."""
        data = _make_dict()
        del data["levels"][0]["base_salary"]["periods"][0]["provenance"]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_missing_seniority_provenance_raises(self) -> None:
        """Missing seniority_increments.provenance in 0.6 raises ValidationError."""
        data = _make_dict()
        del data["parameters"]["seniority_increments"]["provenance"]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_missing_allowance_provenance_raises(self) -> None:
        """An allowance without provenance in schema 0.6 raises ValidationError."""
        data = _make_dict()
        data["levels"][0]["fixed_allowances"] = [
            {"code": "X", "description": "X", "monthly": _SERIES}
        ]
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_builder_dict_without_provenance_rejected(self) -> None:
        """The minimal builder dict without provenance is also rejected."""
        data = make_ccnl_dict(app_type="")
        # Strip provenance from seniority_increments to trigger the validator.
        data["parameters"]["seniority_increments"].pop("provenance", None)
        with pytest.raises(ValidationError, match="provenance is required"):
            _validate(data)

    def test_gap_period_needs_no_provenance(self) -> None:
        """A gap period in a 0.6 file is exempt from the provenance requirement."""
        data = _make_dict()
        # Insert a gap before the existing period (all periods have provenance via
        # _make_dict; the gap has none — this must still pass).
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


# ---------------------------------------------------------------------------
# Contract family
# ---------------------------------------------------------------------------


class TestMetaFamily:
    """``meta.family`` is required and names families of the catalog."""

    def test_a_missing_family_is_rejected(self) -> None:
        """Schema 0.6 requires the family."""
        data = make_ccnl_dict()
        del data["meta"]["family"]
        with pytest.raises(ValidationError, match=r"meta\.family"):
            _validate(data)

    @pytest.mark.parametrize(
        "family",
        [
            {"id": "edile", "reason": "Unknown main family."},
            {"id": "commercio", "reason": "Unknown related.", "related": ["edile"]},
        ],
    )
    def test_an_unknown_family_is_rejected(self, family: dict[str, Any]) -> None:
        """A main or related family the catalog does not hold fails the load."""
        data = make_ccnl_dict()
        data["meta"]["family"] = family
        with pytest.raises(ValidationError, match=r"\['edile'\] that the catalog"):
            _validate(data)

    def test_an_earlier_schema_is_rejected(self) -> None:
        """A 0.5 file predates the family and is not loaded."""
        data = make_ccnl_dict()
        data["schema_version"] = "0.5"
        with pytest.raises(ValidationError, match="schema_version"):
            _validate(data)
