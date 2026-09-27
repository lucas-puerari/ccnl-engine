"""Tests for CCNL domain models: levels and seniority.

Covers the Level non-decreasing salary check and the cross-field validators
on levels, seniority increments and tiered seniority ladders.
"""

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.domain.identity import CCNL
from ccnl_engine.contract.domain.seniority import SeniorityIncrements
from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.payroll.service.seniority import (
    seniority_first_cadence,
    seniority_maximum,
)
from tests.helpers import TEST_PROV, _series_with_prov, make_ccnl_dict

_SERIES = {"periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "1"}]}


def _series(value: str, valid_from: str = "2020-01-01") -> dict[str, Any]:
    return {
        "periods": [{"valid_from": valid_from, "valid_until": None, "value": value}]
    }


def _ts(value: str) -> TimeSeries:
    """Return a single-period TimeSeries — typed for use in direct constructors.

    Returns:
        A TimeSeries with one open-ended period starting 2020-01-01.
    """
    return TimeSeries(
        periods=(
            ValidityPeriod(
                valid_from=date(2020, 1, 1),
                valid_until=None,
                value=Decimal(value),
            ),
        )
    )


def _validate(data: dict[str, Any]) -> CCNL:
    return CCNL.model_validate(data)


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
                "provenance": TEST_PROV,
            },
            {
                "valid_from": "2020-01-01",
                "valid_until": None,
                "value": "1000.00",
                "provenance": TEST_PROV,
            },
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
                "provenance": TEST_PROV,
            },
            {
                "valid_from": "2020-01-01",
                "valid_until": None,
                "value": "1000.00",
                "provenance": TEST_PROV,
            },
        ]
        with pytest.raises(ValidationError, match="non-decreasing over time"):
            _validate(data)

    def test_gap_between_real_periods_is_skipped(self) -> None:
        """A gap period flanked by valid values is not compared; no error raised."""
        data = make_ccnl_dict()
        data["levels"][2]["base_salary"]["periods"] = [
            {
                "valid_from": "2019-01-01",
                "valid_until": "2020-01-01",
                "value": "900.00",
                "provenance": TEST_PROV,
            },
            {
                "valid_from": "2020-01-01",
                "valid_until": "2021-01-01",
                "gap_kind": "missing",
            },
            {
                "valid_from": "2021-01-01",
                "valid_until": None,
                "value": "1000.00",
                "provenance": TEST_PROV,
            },
        ]
        ccnl = _validate(data)
        assert ccnl.levels[2].base_salary.periods[1].is_gap


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
        data["levels"][1]["base_salary"] = _series_with_prov("1000.00")
        assert len(_validate(data).levels) == 3

    def test_inverted_order_raises(self) -> None:
        """A higher-order level earning less must raise ValidationError."""
        data = make_ccnl_dict()
        data["levels"][1]["base_salary"] = _series_with_prov("1200.00")
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
        data["levels"][2]["base_salary"] = _series_with_prov("1000.00", "2021-01-01")
        assert len(_validate(data).levels) == 3

    def test_cross_level_gap_not_applicable_is_skipped(self) -> None:
        """A not_applicable gap on an earlier date is skipped in ordering check."""
        data = make_ccnl_dict()
        # Level with order=3 has a not_applicable gap before its real salary.
        data["levels"][2]["base_salary"]["periods"] = [
            {
                "valid_from": "2020-01-01",
                "valid_until": "2021-01-01",
                "gap_kind": "not_applicable",
            },
            {
                "valid_from": "2021-01-01",
                "valid_until": None,
                "value": "1000.00",
                "provenance": TEST_PROV,
            },
        ]
        assert len(_validate(data).levels) == 3

    def test_cross_level_gap_missing_is_skipped(self) -> None:
        """A missing gap on an earlier date is skipped in ordering check."""
        data = make_ccnl_dict()
        data["levels"][2]["base_salary"]["periods"] = [
            {
                "valid_from": "2020-01-01",
                "valid_until": "2021-01-01",
                "gap_kind": "missing",
            },
            {
                "valid_from": "2021-01-01",
                "valid_until": None,
                "value": "1000.00",
                "provenance": TEST_PROV,
            },
        ]
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
                amount_by_level={"4": _ts("1.00")},
                first_cadence_months=24,
            )

    def test_negative_level_maximum_raises(self) -> None:
        """maximum_count_by_level values must be >= 0."""
        with pytest.raises(ValidationError, match="must be >= 0"):
            SeniorityIncrements(
                cadence_months=36,
                maximum_count=5,
                amount_by_level={"4": _ts("1.00")},
                maximum_count_by_level={"4": -1},
            )

    def test_per_level_lookups(self) -> None:
        """maximum_for / first_cadence_for fall back to contract-wide values."""
        si = SeniorityIncrements(
            cadence_months=24,
            maximum_count=5,
            amount_by_level={"3": _ts("1.00"), "4": _ts("1.00")},
            maximum_count_by_level={"4": 1},
            first_cadence_months_by_level={"4": 48},
        )
        assert seniority_maximum(si, "4", None) == 1
        assert seniority_maximum(si, "3", None) == 5
        assert seniority_first_cadence(si, "4", None) == 48
        assert seniority_first_cadence(si, "3", None) == 24
        si_first = SeniorityIncrements(
            cadence_months=36,
            maximum_count=5,
            amount_by_level={"3": _ts("1.00")},
            first_cadence_months=48,
        )
        assert seniority_first_cadence(si_first, "3") == 48

    def test_first_cadence_by_level_below_cadence_raises(self) -> None:
        """Per-level first cadence must also be >= cadence_months."""
        with pytest.raises(
            ValidationError, match=r"first_cadence_months_by_level\['4'\]"
        ):
            SeniorityIncrements(
                cadence_months=36,
                maximum_count=5,
                amount_by_level={"4": _ts("1.00")},
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
                amount_by_level={"2": _ts("1.00")},
                maximum_count_by_category={WorkerCategory.OPERAIO: -1},
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
            amount_by_level={"2": _ts("1.00")},
            first_cadence_months=48,
            first_cadence_months_by_category={WorkerCategory.OPERAIO: 24},
        )
        assert seniority_first_cadence(si, "2", WorkerCategory.OPERAIO) == 24
        assert seniority_first_cadence(si, "2", WorkerCategory.IMPIEGATO) == 48
        assert seniority_first_cadence(si, "2") == 48

    def test_flat_no_amounts_with_positive_max_raises(self) -> None:
        """Flat mode with maximum_count > 0 and no amounts defined is rejected."""
        with pytest.raises(ValidationError, match="amount_by_level"):
            SeniorityIncrements(
                cadence_months=24,
                maximum_count=5,
                amount_by_level={},
            )

    def test_flat_no_amounts_zero_maximum_accepted(self) -> None:
        """maximum_count=0 with no amounts is valid (seniority disabled)."""
        si = SeniorityIncrements(
            cadence_months=24,
            maximum_count=0,
            amount_by_level={},
        )
        assert si.maximum_count == 0

    def test_flat_category_amounts_without_level_amounts_accepted(self) -> None:
        """amount_by_level_by_category alone satisfies the amounts requirement."""
        si = SeniorityIncrements(
            cadence_months=24,
            maximum_count=10,
            amount_by_level={},
            amount_by_level_by_category={WorkerCategory.OPERAIO: {"2": _ts("1.00")}},
        )
        assert si.maximum_count == 10


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
            "maximum_count": 5,  # must equal sum of tier maximum_count (3 + 2)
            "amount_by_level": {},
            "provenance": TEST_PROV,
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
        assert seniority_maximum(si, "4") == 5  # 3 + 2

    def test_tiered_maximum_count_mismatch_raises(self) -> None:
        """maximum_count must equal the sum of tier maximum_count values."""
        data = self._tiered_data()
        data["parameters"]["seniority_increments"]["maximum_count"] = 99
        with pytest.raises(ValidationError, match="must equal the sum of tier"):
            _validate(data)

    def test_tiered_with_flat_only_field_raises(self) -> None:
        """Flat-mode fields are rejected when tiers is set."""
        data = self._tiered_data()
        data["parameters"]["seniority_increments"]["first_cadence_months"] = 48
        with pytest.raises(ValidationError, match="not allowed in tiered mode"):
            _validate(data)

    def test_tiered_with_maximum_count_by_level_raises(self) -> None:
        """maximum_count_by_level is a flat-mode field; rejected in tiered mode."""
        data = self._tiered_data()
        data["parameters"]["seniority_increments"]["maximum_count_by_level"] = {"4": 2}
        with pytest.raises(ValidationError, match="not allowed in tiered mode"):
            _validate(data)

    def test_tiered_with_amount_by_level_by_category_raises(self) -> None:
        """amount_by_level_by_category is flat-mode only; rejected in tiered mode."""
        data = self._tiered_data()
        data["parameters"]["seniority_increments"]["amount_by_level_by_category"] = {
            "operaio": {"4": _series("5.00")}
        }
        with pytest.raises(ValidationError, match="not allowed in tiered mode"):
            _validate(data)
