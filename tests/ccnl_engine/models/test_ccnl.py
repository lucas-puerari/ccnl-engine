"""Tests for CCNL domain models.

Covers cross-field validators on CCNL and the Level non-decreasing salary check.
"""

import copy
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.models.ccnl import CCNL

# ---------------------------------------------------------------------------
# Minimal valid CCNL fixture
# ---------------------------------------------------------------------------

_BASE: dict[str, Any] = {
    "schema_version": "0.2",
    "ccnl": {
        "id": "test",
        "name": "Test CCNL",
        "cnel_code": "T001",
        "sector": "test",
        "tax_sector": "terziario",
        "signatories": ["TestOrg"],
        "sources": [{"url": "http://example.com", "type": "table"}],
        "extraction": {
            "method": "manual",
            "timestamp": "2025-01-01T00:00:00",
            "human_reviewed": True,
        },
    },
    "parameters": {
        "hourly_divisor": 168,
        "additional_months": {
            "periods": [
                {"valid_from": "2025-01-01", "valid_until": None, "value": "14"}
            ]
        },
        "seniority_increments": {
            "cadence_months": 36,
            "maximum_count": 10,
            "amount_by_level": {},
        },
    },
    "levels": [
        {
            "code": "1",
            "order": 1,
            "description": "Level 1",
            "base_salary": {
                "periods": [
                    {
                        "valid_from": "2025-01-01",
                        "valid_until": None,
                        "value": "1000.00",
                    }
                ]
            },
        }
    ],
    "apprenticeship": {
        "type": "percentage",
        "destination_level": "1",
        "periods": [{"months_from": 0, "months_until": None, "percentage": "0.80"}],
    },
    "coverage": {
        "layer_1": "implemented",
        "layer_2": "implemented",
        "layer_3": "out_of_scope",
        "notes": [],
    },
}


def _ccnl(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a deep copy of the minimal fixture, with optional overrides merged."""
    data = copy.deepcopy(_BASE)
    if overrides:
        data.update(overrides)
    return data


def _two_level_data(
    salary_low: str = "1000.00",
    salary_high: str = "2000.00",
) -> dict[str, Any]:
    """Minimal two-level CCNL for salary-ordering tests."""
    return _ccnl(
        {
            "levels": [
                {
                    "code": "1",
                    "order": 1,
                    "description": "Level 1 (low)",
                    "base_salary": {
                        "periods": [
                            {
                                "valid_from": "2025-01-01",
                                "valid_until": None,
                                "value": salary_low,
                            }
                        ]
                    },
                },
                {
                    "code": "2",
                    "order": 2,
                    "description": "Level 2 (high)",
                    "base_salary": {
                        "periods": [
                            {
                                "valid_from": "2025-01-01",
                                "valid_until": None,
                                "value": salary_high,
                            }
                        ]
                    },
                },
            ],
            "parameters": {
                "hourly_divisor": 168,
                "additional_months": {
                    "periods": [
                        {
                            "valid_from": "2025-01-01",
                            "valid_until": None,
                            "value": "14",
                        }
                    ]
                },
                "seniority_increments": {
                    "cadence_months": 36,
                    "maximum_count": 10,
                    "amount_by_level": {
                        "1": {
                            "periods": [
                                {
                                    "valid_from": "2025-01-01",
                                    "valid_until": None,
                                    "value": "20.00",
                                }
                            ]
                        },
                        "2": {
                            "periods": [
                                {
                                    "valid_from": "2025-01-01",
                                    "valid_until": None,
                                    "value": "25.00",
                                }
                            ]
                        },
                    },
                },
            },
        }
    )


# ---------------------------------------------------------------------------
# Level — non-decreasing salary validator
# ---------------------------------------------------------------------------


class TestLevelSalaryNonDecreasing:
    """Level.base_salary values must be non-decreasing over time."""

    def test_single_period_valid(self) -> None:
        """Single-period base_salary is always valid."""
        ccnl = CCNL.model_validate(_ccnl())
        assert (
            ccnl.levels[0].base_salary.periods[0].value.__class__.__name__ == "Decimal"
        )

    def test_two_increasing_periods_valid(self) -> None:
        """Two periods where value increases are valid."""
        data = _ccnl()
        data["levels"][0]["base_salary"]["periods"] = [
            {
                "valid_from": "2024-01-01",
                "valid_until": "2025-01-01",
                "value": "900.00",
            },
            {"valid_from": "2025-01-01", "valid_until": None, "value": "1000.00"},
        ]
        ccnl = CCNL.model_validate(data)
        assert len(ccnl.levels[0].base_salary.periods) == 2

    def test_decreasing_periods_raises(self) -> None:
        """A period where value decreases must raise ValidationError."""
        data = _ccnl()
        data["levels"][0]["base_salary"]["periods"] = [
            {
                "valid_from": "2024-01-01",
                "valid_until": "2025-01-01",
                "value": "1200.00",
            },
            {"valid_from": "2025-01-01", "valid_until": None, "value": "1000.00"},
        ]
        with pytest.raises(ValidationError):
            CCNL.model_validate(data)


# ---------------------------------------------------------------------------
# CCNL cross-field: unique orders
# ---------------------------------------------------------------------------


class TestCCNLUniqueOrders:
    """CCNL.levels must have unique order values."""

    def test_duplicate_order_raises(self) -> None:
        """Two levels with the same order must raise ValidationError."""
        data = _two_level_data()
        data["levels"][1]["order"] = 1  # duplicate
        with pytest.raises(ValidationError):
            CCNL.model_validate(data)

    def test_unique_orders_valid(self) -> None:
        """Two levels with distinct orders are valid."""
        ccnl = CCNL.model_validate(_two_level_data())
        orders = [lv.order for lv in ccnl.levels]
        assert len(set(orders)) == len(orders)


# ---------------------------------------------------------------------------
# CCNL cross-field: unique codes
# ---------------------------------------------------------------------------


class TestCCNLUniqueCodes:
    """CCNL.levels must have unique code values."""

    def test_duplicate_code_raises(self) -> None:
        """Two levels with the same code must raise ValidationError."""
        data = _two_level_data()
        data["levels"][1]["code"] = "1"  # duplicate code
        with pytest.raises(ValidationError):
            CCNL.model_validate(data)


# ---------------------------------------------------------------------------
# CCNL cross-field: seniority level codes
# ---------------------------------------------------------------------------


class TestCCNLSeniorityLevelCodes:
    """Keys in seniority_increments.amount_by_level must reference existing levels."""

    def test_unknown_level_code_raises(self) -> None:
        """A seniority entry referencing a missing level must raise ValidationError."""
        data = _ccnl()
        data["parameters"]["seniority_increments"]["amount_by_level"] = {
            "999": {
                "periods": [
                    {"valid_from": "2025-01-01", "valid_until": None, "value": "20.00"}
                ]
            }
        }
        with pytest.raises(ValidationError):
            CCNL.model_validate(data)

    def test_known_level_code_valid(self) -> None:
        """A seniority entry referencing an existing level is valid."""
        data = _ccnl()
        data["parameters"]["seniority_increments"]["amount_by_level"] = {
            "1": {
                "periods": [
                    {"valid_from": "2025-01-01", "valid_until": None, "value": "20.00"}
                ]
            }
        }
        ccnl = CCNL.model_validate(data)
        assert "1" in ccnl.parameters.seniority_increments.amount_by_level


# ---------------------------------------------------------------------------
# CCNL cross-field: salary non-decreasing by order
# ---------------------------------------------------------------------------


class TestCCNLSalaryOrderNonDecreasing:
    """Higher-order levels must earn >= lower-order levels at every date."""

    def test_single_level_skips_check(self) -> None:
        """Single-level CCNL bypasses the pairwise ordering check."""
        ccnl = CCNL.model_validate(_ccnl())
        assert len(ccnl.levels) == 1

    def test_two_levels_ordered_valid(self) -> None:
        """Level 2 salary >= Level 1 salary: valid."""
        ccnl = CCNL.model_validate(_two_level_data("1000.00", "2000.00"))
        assert len(ccnl.levels) == 2

    def test_equal_salaries_valid(self) -> None:
        """Equal salaries across levels satisfy the non-decreasing constraint."""
        ccnl = CCNL.model_validate(_two_level_data("1000.00", "1000.00"))
        assert len(ccnl.levels) == 2

    def test_inverted_order_raises(self) -> None:
        """Level 2 salary < Level 1 salary must raise ValidationError."""
        with pytest.raises(ValidationError):
            CCNL.model_validate(_two_level_data("2000.00", "1000.00"))

    def test_staggered_start_dates(self) -> None:
        """A level whose series starts after another's is skipped on earlier dates."""
        data = _ccnl(
            {
                "levels": [
                    {
                        "code": "1",
                        "order": 1,
                        "description": "Early-starting level",
                        "base_salary": {
                            "periods": [
                                {
                                    "valid_from": "2024-01-01",
                                    "valid_until": None,
                                    "value": "1000.00",
                                }
                            ]
                        },
                    },
                    {
                        "code": "2",
                        "order": 2,
                        "description": "Late-starting level",
                        "base_salary": {
                            "periods": [
                                {
                                    "valid_from": "2025-01-01",
                                    "valid_until": None,
                                    "value": "2000.00",
                                }
                            ]
                        },
                    },
                ],
                "parameters": {
                    "hourly_divisor": 168,
                    "additional_months": {
                        "periods": [
                            {
                                "valid_from": "2024-01-01",
                                "valid_until": None,
                                "value": "14",
                            }
                        ]
                    },
                    "seniority_increments": {
                        "cadence_months": 36,
                        "maximum_count": 10,
                        "amount_by_level": {},
                    },
                },
            }
        )
        # Level 2 starts later; at 2024-01-01 only Level 1 is checked. Valid.
        ccnl = CCNL.model_validate(data)
        assert len(ccnl.levels) == 2
