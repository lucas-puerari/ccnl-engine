"""Tests for CCNL cross-field rules outside levels and seniority.

Covers apprenticeship tracks, coverage notes, verification, employer funds
and allowances.
"""

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.domain.compensation import EmployerFund
from ccnl_engine.contract.domain.identity import CCNL
from tests.helpers import TEST_PROV, make_ccnl_dict

_SERIES = {"periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "1"}]}


def _series(value: str, valid_from: str = "2020-01-01") -> dict[str, Any]:
    return {
        "periods": [{"valid_from": valid_from, "valid_until": None, "value": value}]
    }


def _validate(data: dict[str, Any]) -> CCNL:
    return CCNL.model_validate(data)


# ---------------------------------------------------------------------------
# CCNL cross-field: apprenticeship tracks
# ---------------------------------------------------------------------------


class TestCCNLApprenticeshipTracks:
    """Destination levels exist, are unique across tracks, offsets resolve."""

    def test_unknown_destination_raises(self) -> None:
        """A destination level that does not exist must raise."""
        data = make_ccnl_dict()
        data["apprenticeship"][0]["destination_levels"] = ["9"]
        with pytest.raises(
            ValidationError, match="destination level '9' which does not"
        ):
            _validate(data)

    def test_duplicate_track_name_raises(self) -> None:
        """Track names must be unique."""
        data = make_ccnl_dict()
        data["apprenticeship"].append(dict(data["apprenticeship"][0]))
        with pytest.raises(ValidationError, match="track names must be unique"):
            _validate(data)

    def test_unresolvable_offset_raises(self) -> None:
        """levels_below pointing below the lowest level must raise at load time."""
        data = make_ccnl_dict(app_type="under_classification")
        data["apprenticeship"][0]["periods"][0]["levels_below"] = 3
        with pytest.raises(ValidationError, match="no level with order 1"):
            _validate(data)

    def test_invalid_reference_level_raises(self) -> None:
        """reference_level pointing to a non-existent level must raise at load time."""
        data = make_ccnl_dict()
        data["apprenticeship"][0]["reference_level"] = "NONEXISTENT"
        with pytest.raises(ValidationError, match="reference_level 'NONEXISTENT'"):
            _validate(data)

    def test_track_lookups(self) -> None:
        """apprenticeship_tracks_for / apprenticeship_track_named helpers."""
        ccnl = _validate(make_ccnl_dict())
        assert [t.name for t in ccnl.apprenticeship_tracks_for("4")] == ["standard"]
        assert ccnl.apprenticeship_tracks_for("3") == []
        assert ccnl.apprenticeship_track_named("standard").name == "standard"
        with pytest.raises(ValueError, match="no apprenticeship track named 'x'"):
            ccnl.apprenticeship_track_named("x")


# ---------------------------------------------------------------------------
# Coverage consistency
# ---------------------------------------------------------------------------


class TestCoverage:
    """CoverageNote kind and the capability a MISSING note names."""

    def test_note_invalid_kind_raises(self) -> None:
        """A note with an unknown kind must be rejected."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = [{"kind": "unknown", "text": "something"}]
        with pytest.raises(ValidationError):
            _validate(data)

    def test_note_missing_text_raises(self) -> None:
        """A note missing the text field must be rejected."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = [{"kind": "info"}]
        with pytest.raises(ValidationError):
            _validate(data)

    def test_missing_note_names_its_capability(self) -> None:
        """A 'missing' note must name the capability it leaves partial."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = [{"kind": "missing", "text": "Jan 2027 tranche."}]
        with pytest.raises(ValidationError, match="must name the capability"):
            _validate(data)
        data["coverage"]["notes"][0]["capability"] = "base_salary"
        result = _validate(data)
        assert result.coverage.notes[0].capability == "base_salary"
        assert result.coverage.notes[0].kind.value == "missing"

    def test_all_note_kinds_accepted(self) -> None:
        """All four NoteKind values are valid."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = [
            {"kind": "source", "text": "example.com"},
            {"kind": "info", "text": "some context"},
            {"kind": "simplification", "text": "approximation applied"},
        ]
        result = _validate(data)
        assert len(result.coverage.notes) == 3

    @pytest.mark.parametrize(
        "flag", ["gross", "net", "work_rules", "work_rules_features"]
    )
    def test_coverage_flags_are_rejected(self, flag: str) -> None:
        """Coverage derives from the registry: a file cannot declare a flag."""
        data = make_ccnl_dict()
        data["coverage"][flag] = "implemented"
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            _validate(data)


class TestVerification:
    """CCNLVerification: defaults, field acceptance, and legacy coercion."""

    def test_confidence_defaults_to_unverified(self) -> None:
        """verification.confidence defaults to 'unverified' when block is absent."""
        data = make_ccnl_dict()
        result = _validate(data)
        assert result.verification.confidence == "unverified"

    def test_confidence_accepted(self) -> None:
        """An explicit confidence value is stored as-is."""
        data = make_ccnl_dict()
        data["verification"] = {"confidence": "needs_review"}
        result = _validate(data)
        assert result.verification.confidence == "needs_review"

    def test_verified_cases_defaults_to_zero(self) -> None:
        """verified_cases defaults to 0 when not supplied."""
        data = make_ccnl_dict()
        result = _validate(data)
        assert result.verification.verified_cases == 0

    def test_verified_cases_accepted(self) -> None:
        """An explicit verified_cases count is stored."""
        data = make_ccnl_dict()
        data["verification"] = {"verified_cases": 3}
        result = _validate(data)
        assert result.verification.verified_cases == 3

    def test_last_reviewed_defaults_to_none(self) -> None:
        """last_reviewed defaults to None when not supplied."""
        data = make_ccnl_dict()
        result = _validate(data)
        assert result.verification.last_reviewed is None

    def test_last_reviewed_accepted(self) -> None:
        """An ISO date string is accepted for last_reviewed."""
        data = make_ccnl_dict()
        data["verification"] = {"last_reviewed": "2025-06-01"}
        result = _validate(data)
        assert result.verification.last_reviewed is not None
        assert str(result.verification.last_reviewed) == "2025-06-01"

    def test_human_reviewed_by_defaults_to_none(self) -> None:
        """human_reviewed_by defaults to None when not supplied."""
        data = make_ccnl_dict()
        result = _validate(data)
        assert result.verification.human_reviewed_by is None

    def test_human_reviewed_by_accepted(self) -> None:
        """A free-form string is accepted for human_reviewed_by."""
        data = make_ccnl_dict()
        data["verification"] = {"human_reviewed_by": "alice@example.com"}
        result = _validate(data)
        assert result.verification.human_reviewed_by == "alice@example.com"


# ---------------------------------------------------------------------------
# Employer funds and allowances
# ---------------------------------------------------------------------------


class TestEmployerFundsAndAllowances:
    """EmployerFund category restriction and allowance field constraints."""

    def test_applies_to(self) -> None:
        """Category restriction is parsed; an unrestricted fund carries None."""
        fund = EmployerFund.model_validate({
            "code": "ce",
            "description": "Cassa Edile",
            "rate": _series("0.185"),
            "applies_to_categories": ["operaio"],
        })
        assert fund.applies_to_categories == (WorkerCategory.OPERAIO,)
        assert fund.rate.value_at(date(2026, 1, 1)) == Decimal("0.185")
        open_fund = EmployerFund.model_validate({
            "code": "f",
            "description": "f",
            "rate": _series("0.01"),
        })
        assert open_fund.applies_to_categories is None

    def test_invalid_category_raises(self) -> None:
        """Categories are a closed vocabulary."""
        data = make_ccnl_dict()
        data["levels"][0]["category"] = "manager"
        with pytest.raises(ValidationError):
            _validate(data)

    def test_months_per_year_positive(self) -> None:
        """months_per_year must be >= 1."""
        data = make_ccnl_dict()
        data["levels"][0]["fixed_allowances"] = [
            {
                "code": "x",
                "description": "x",
                "monthly": _SERIES,
                "months_per_year": 0,
                "provenance": TEST_PROV,
            }
        ]
        with pytest.raises(ValidationError):
            _validate(data)


class TestServiceMonthsThreshold:
    """Tests for Allowance.service_months_threshold field validation."""

    def test_negative_threshold_raises(self) -> None:
        """service_months_threshold must be >= 0."""
        data = make_ccnl_dict(app_type="")
        data["levels"][0]["fixed_allowances"] = [
            {
                "code": "X",
                "description": "X",
                "monthly": _SERIES,
                "service_months_threshold": -1,
                "provenance": TEST_PROV,
            }
        ]
        with pytest.raises(ValidationError):
            _validate(data)

    def test_zero_threshold_accepted(self) -> None:
        """service_months_threshold=0 is accepted (always active)."""
        data = make_ccnl_dict(app_type="")
        data["levels"][0]["fixed_allowances"] = [
            {
                "code": "X",
                "description": "X",
                "monthly": _SERIES,
                "service_months_threshold": 0,
                "provenance": TEST_PROV,
            }
        ]
        _validate(data)
