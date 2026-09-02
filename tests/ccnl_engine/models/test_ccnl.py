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
        data["ccnl"]["agreement_date"] = "2024-03-22"
        data["ccnl"]["validity"] = {"valid_from": "2024-04-01", "valid_until": None}
        data["ccnl"]["sources"][0]["notes"] = "salary tables"
        ccnl = _validate(data)
        assert ccnl.ccnl.validity is not None
        assert ccnl.ccnl.validity.valid_until is None


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
        """level_by_code / level_by_order return the level or raise KeyError."""
        ccnl = _validate(make_ccnl_dict())
        assert ccnl.level_by_code("3").order == 3
        assert ccnl.level_by_order(2).code == "2"
        with pytest.raises(KeyError, match="NOPE"):
            ccnl.level_by_code("NOPE")
        with pytest.raises(KeyError, match="order 9"):
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

    def test_maximum_for(self) -> None:
        """maximum_for falls back to maximum_count for unlisted levels."""
        si = SeniorityIncrements(
            cadence_months=36,
            maximum_count=5,
            amount_by_level={},
            maximum_count_by_level={"4": 1},
        )
        assert si.maximum_for("4") == 1
        assert si.maximum_for("3") == 5


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

    def test_destination_in_two_tracks_raises(self) -> None:
        """The same destination level cannot appear in two tracks."""
        data = make_ccnl_dict()
        second = dict(data["apprenticeship"][0], name="other")
        data["apprenticeship"].append(second)
        with pytest.raises(ValidationError, match="appears in both track"):
            _validate(data)

    def test_unresolvable_offset_raises(self) -> None:
        """levels_below pointing below the lowest level must raise at load time."""
        data = make_ccnl_dict(app_type="under_classification")
        data["apprenticeship"][0]["periods"][0]["levels_below"] = 3
        with pytest.raises(ValidationError, match="no level with order 1"):
            _validate(data)

    def test_track_lookup(self) -> None:
        """apprenticeship_track_for returns the track or None."""
        ccnl = _validate(make_ccnl_dict())
        assert ccnl.apprenticeship_track_for("4") is not None
        assert ccnl.apprenticeship_track_for("3") is None


# ---------------------------------------------------------------------------
# Coverage consistency
# ---------------------------------------------------------------------------


class TestCoverage:
    """Note prefixes, MISSING rule and layer_2 <-> tracks consistency."""

    def test_note_without_prefix_raises(self) -> None:
        """Every note must start with an allowed prefix."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = ["Salary model: conglobated."]
        with pytest.raises(ValidationError, match="must start with one of"):
            _validate(data)

    def test_missing_note_requires_partial(self) -> None:
        """A MISSING: note is only allowed while a layer is partial."""
        data = make_ccnl_dict()
        data["coverage"]["notes"] = ["MISSING: Jan 2027 tranche."]
        with pytest.raises(ValidationError, match="MISSING: notes but neither"):
            _validate(data)
        data["coverage"]["layer_1"] = "partial"
        assert _validate(data).coverage.layer_1 == "partial"

    def test_implemented_without_tracks_raises(self) -> None:
        """layer_2 implemented requires at least one apprenticeship track."""
        data = make_ccnl_dict(app_type="none")
        data["coverage"] = {
            "layer_1": "implemented",
            "layer_2": "implemented",
            "layer_3": "out_of_scope",
            "notes": [],
        }
        with pytest.raises(ValidationError, match="no apprenticeship track exists"):
            _validate(data)

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
        fund = EmployerFund.model_validate(
            {
                "code": "ce",
                "description": "Cassa Edile",
                "rate": _series("0.185"),
                "applies_to_categories": ["operaio"],
            }
        )
        assert fund.applies_to("operaio")
        assert not fund.applies_to("impiegato")
        assert not fund.applies_to(None)
        assert fund.rate.value_at(date(2026, 1, 1)) == Decimal("0.185")
        open_fund = EmployerFund.model_validate(
            {"code": "f", "description": "f", "rate": _series("0.01")}
        )
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
