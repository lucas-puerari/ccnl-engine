"""Tests for CCNL domain models.

Covers cross-field validators on CCNL, the Level non-decreasing salary check,
coverage note rules, seniority rules, employer funds and strict extra-key
rejection.
"""

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.models.ccnl import CCNL, EmployerFund, SeniorityIncrements
from tests.conftest import make_ccnl_dict

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
# Level — non-decreasing salary validator
# ---------------------------------------------------------------------------


class TestLevelSalaryNonDecreasing:
    """Level.base_salary values must be non-decreasing over time."""

    def test_two_increasing_periods_valid(self) -> None:
        """Two periods where value increases are valid."""
        data = make_ccnl_dict()
        data["levels"][2]["base_salary"]["periods"] = [
            {
                "valid_from": "2019-01-01",
                "valid_until": "2020-01-01",
                "value": "900.00",
            },
            {"valid_from": "2020-01-01", "valid_until": None, "value": "1000.00"},
        ]
        assert len(_validate(data).levels[2].base_salary.periods) == 2

    def test_decreasing_periods_raises(self) -> None:
        """A period where value decreases must raise ValidationError."""
        data = make_ccnl_dict()
        data["levels"][2]["base_salary"]["periods"] = [
            {
                "valid_from": "2019-01-01",
                "valid_until": "2020-01-01",
                "value": "1200.00",
            },
            {"valid_from": "2020-01-01", "valid_until": None, "value": "1000.00"},
        ]
        with pytest.raises(ValidationError, match="non-decreasing over time"):
            _validate(data)


# ---------------------------------------------------------------------------
# CCNL cross-field: levels
# ---------------------------------------------------------------------------


class TestCCNLLevels:
    """Unique orders/codes and salary ordering across levels."""

    def test_duplicate_order_raises(self) -> None:
        """Two levels with the same order must raise ValidationError."""
        data = make_ccnl_dict()
        data["levels"][1]["order"] = 4
        with pytest.raises(ValidationError, match="order values must be unique"):
            _validate(data)

    def test_duplicate_code_raises(self) -> None:
        """Two levels with the same code must raise ValidationError."""
        data = make_ccnl_dict()
        data["levels"][1]["code"] = "4"
        with pytest.raises(ValidationError, match="code values must be unique"):
            _validate(data)

    def test_equal_salaries_valid(self) -> None:
        """Equal salaries across levels satisfy the non-decreasing constraint."""
        data = make_ccnl_dict()
        data["levels"][1]["base_salary"] = _series("1000.00")
        assert len(_validate(data).levels) == 3

    def test_inverted_order_raises(self) -> None:
        """A higher-order level earning less must raise ValidationError."""
        data = make_ccnl_dict()
        data["levels"][1]["base_salary"] = _series("1200.00")
        with pytest.raises(ValidationError, match="salary ordering violated"):
            _validate(data)

    def test_single_level_skips_check(self) -> None:
        """Single-level CCNL bypasses the pairwise ordering check."""
        data = make_ccnl_dict(app_type="none")
        data["levels"] = [data["levels"][2]]
        assert len(_validate(data).levels) == 1

    def test_staggered_start_dates(self) -> None:
        """A level whose series starts after another's is skipped on earlier dates."""
        data = make_ccnl_dict()
        data["levels"][2]["base_salary"] = _series("1000.00", "2021-01-01")
        assert len(_validate(data).levels) == 3

    def test_level_lookup_helpers(self) -> None:
        """level_by_code / level_by_order return the level or raise ValueError."""
        ccnl = _validate(make_ccnl_dict())
        assert ccnl.level_by_code("3").order == 3
        assert ccnl.level_by_order(2).code == "2"
        with pytest.raises(ValueError, match="NOPE"):
            ccnl.level_by_code("NOPE")
        with pytest.raises(ValueError, match="order 9"):
            ccnl.level_by_order(9)


# ---------------------------------------------------------------------------
# CCNL cross-field: seniority
# ---------------------------------------------------------------------------


class TestCCNLSeniority:
    """Seniority level references and cadence rules."""

    def test_unknown_amount_level_raises(self) -> None:
        """amount_by_level referencing a missing level must raise."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"]["amount_by_level"]["999"] = _SERIES
        with pytest.raises(ValidationError, match="amount_by_level references"):
            _validate(data)

    def test_unknown_maximum_level_raises(self) -> None:
        """maximum_count_by_level referencing a missing level must raise."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"]["maximum_count_by_level"] = {"9": 1}
        with pytest.raises(ValidationError, match="maximum_count_by_level references"):
            _validate(data)

    def test_first_cadence_below_cadence_raises(self) -> None:
        """first_cadence_months must be >= cadence_months."""
        with pytest.raises(ValidationError, match="first_cadence_months"):
            SeniorityIncrements(
                cadence_months=36,
                maximum_count=5,
                amount_by_level={},
                first_cadence_months=24,
            )

    def test_negative_level_maximum_raises(self) -> None:
        """maximum_count_by_level values must be >= 0."""
        with pytest.raises(ValidationError, match="must be >= 0"):
            SeniorityIncrements(
                cadence_months=36,
                maximum_count=5,
                amount_by_level={},
                maximum_count_by_level={"4": -1},
            )

    def test_per_level_lookups(self) -> None:
        """maximum_for / first_cadence_for fall back to contract-wide values."""
        si = SeniorityIncrements(
            cadence_months=24,
            maximum_count=5,
            amount_by_level={},
            maximum_count_by_level={"4": 1},
            first_cadence_months_by_level={"4": 48},
        )
        assert si.maximum_for("4", None) == 1
        assert si.maximum_for("3", None) == 5
        assert si.first_cadence_for("4", None) == 48
        assert si.first_cadence_for("3", None) == 24
        si_first = SeniorityIncrements(
            cadence_months=36,
            maximum_count=5,
            amount_by_level={},
            first_cadence_months=48,
        )
        assert si_first.first_cadence_for("3") == 48

    def test_first_cadence_by_level_below_cadence_raises(self) -> None:
        """Per-level first cadence must also be >= cadence_months."""
        with pytest.raises(
            ValidationError, match=r"first_cadence_months_by_level\['4'\]"
        ):
            SeniorityIncrements(
                cadence_months=36,
                maximum_count=5,
                amount_by_level={},
                first_cadence_months_by_level={"4": 24},
            )

    def test_unknown_first_cadence_level_raises(self) -> None:
        """first_cadence_months_by_level referencing a missing level must raise."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"]["first_cadence_months_by_level"] = {
            "9": 48
        }
        with pytest.raises(ValidationError, match="first_cadence_months_by_level ref"):
            _validate(data)

    def test_negative_category_maximum_raises(self) -> None:
        """maximum_count_by_category values must be >= 0."""
        with pytest.raises(ValidationError, match="must be >= 0"):
            SeniorityIncrements(
                cadence_months=24,
                maximum_count=10,
                amount_by_level={},
                maximum_count_by_category={"operaio": -1},
            )

    def test_unknown_amount_by_level_by_category_raises(self) -> None:
        """amount_by_level_by_category referencing a missing level must raise."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"]["amount_by_level_by_category"] = {
            "operaio": {"999": _SERIES}
        }
        with pytest.raises(ValidationError, match="amount_by_level_by_category"):
            _validate(data)

    def test_first_cadence_for_by_category(self) -> None:
        """first_cadence_for returns category override when present."""
        si = SeniorityIncrements(
            cadence_months=24,
            maximum_count=10,
            amount_by_level={},
            first_cadence_months=48,
            first_cadence_months_by_category={"operaio": 24},
        )
        assert si.first_cadence_for("2", "operaio") == 24
        assert si.first_cadence_for("2", "impiegato") == 48
        assert si.first_cadence_for("2") == 48


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
    """CoverageNote kind, MISSING rule and layer_2 <-> tracks consistency."""

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

    def test_missing_note_requires_partial(self) -> None:
        """A 'missing' note is only allowed while a layer is partial."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = [{"kind": "missing", "text": "Jan 2027 tranche."}]
        with pytest.raises(ValidationError, match="'missing' notes but neither"):
            _validate(data)
        data["coverage"]["layer_1"] = "partial"
        result = _validate(data)
        assert result.coverage.layer_1 == "partial"
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

    def test_implemented_without_tracks_allowed(self) -> None:
        """layer_2 implemented is valid even with no apprenticeship tracks.

        Some sectors (e.g. PA/ARAN) correctly have no apprenticeship tracks;
        layer_2=implemented still models part-time and fixed-term correctly.
        """
        data = make_ccnl_dict(app_type="none")
        data["coverage"] = {
            "layer_1": "implemented",
            "layer_2": "implemented",
            "notes": [],
        }
        result = _validate(data)
        assert result.coverage.layer_2 == "implemented"

    def test_out_of_scope_with_tracks_raises(self) -> None:
        """layer_2 out_of_scope is inconsistent with apprenticeship tracks."""
        data = make_ccnl_dict()
        data["coverage"]["layer_2"] = "out_of_scope"
        with pytest.raises(ValidationError, match="but apprenticeship tracks exist"):
            _validate(data)


# ---------------------------------------------------------------------------
# Employer funds and allowances
# ---------------------------------------------------------------------------


class TestEmployerFundsAndAllowances:
    """EmployerFund.applies_to and allowance field constraints."""

    def test_applies_to(self) -> None:
        """Category restriction semantics."""
        fund = EmployerFund.model_validate({
            "code": "ce",
            "description": "Cassa Edile",
            "rate": _series("0.185"),
            "applies_to_categories": ["operaio"],
        })
        assert fund.applies_to("operaio")
        assert not fund.applies_to("impiegato")
        assert not fund.applies_to(None)
        assert fund.rate.value_at(date(2026, 1, 1)) == Decimal("0.185")
        open_fund = EmployerFund.model_validate({
            "code": "f",
            "description": "f",
            "rate": _series("0.01"),
        })
        assert open_fund.applies_to(None)

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
            {"code": "x", "description": "x", "monthly": _SERIES, "months_per_year": 0}
        ]
        with pytest.raises(ValidationError):
            _validate(data)


class TestSeniorityTiers:
    """Tests for the SeniorityTier / tiered seniority ladder."""

    def _tiered_data(self) -> dict[str, Any]:
        """Return a minimal CCNL dict with a 2-tier seniority ladder.

        Returns:
            Raw dict suitable for CCNL.model_validate().
        """
        data = make_ccnl_dict(app_type="")
        data["parameters"]["seniority_increments"] = {
            "cadence_months": 24,
            "maximum_count": 0,
            "amount_by_level": {},
            "tiers": [
                {
                    "cadence_months": 24,
                    "maximum_count": 3,
                    "amount_by_level": {"4": _series("10.00")},
                },
                {
                    "cadence_months": 48,
                    "maximum_count": 2,
                    "amount_by_level": {"4": _series("15.00")},
                },
            ],
        }
        return data

    def test_tiered_ccnl_validates(self) -> None:
        """A CCNL with tiers loads without error."""
        _validate(self._tiered_data())

    def test_tiers_and_amount_by_level_mutually_exclusive(self) -> None:
        """Providing both tiers and amount_by_level is rejected."""
        data = self._tiered_data()
        data["parameters"]["seniority_increments"]["amount_by_level"] = {
            "4": _series("5.00")
        }
        with pytest.raises(ValidationError):
            _validate(data)

    def test_tier_unknown_level_code_raises(self) -> None:
        """A tier referencing a non-existent level code is rejected."""
        data = self._tiered_data()
        data["parameters"]["seniority_increments"]["tiers"][0]["amount_by_level"] = {
            "NONEXISTENT": _series("10.00")
        }
        with pytest.raises(ValueError, match=r"tiers.*NONEXISTENT.*does not exist"):
            _validate(data)

    def test_maximum_for_sums_tiers(self) -> None:
        """maximum_for returns the sum of all tier maximums."""
        ccnl = _validate(self._tiered_data())
        si = ccnl.parameters.seniority_increments
        assert si.maximum_for("4") == 5  # 3 + 2


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
            }
        ]
        _validate(data)
