"""Shared pytest fixtures and configuration."""

from __future__ import annotations

from typing import Any

import pytest

from ccnl_engine.models.ccnl import CCNL
from ccnl_engine.tax.models import YearRules

# ---------------------------------------------------------------------------
# Shared raw data — canonical source for inline fixtures across the test suite
# ---------------------------------------------------------------------------

#: 2026 IRPEF marginal tax brackets (Art. 11 TUIR post L. 207/2024).
IRPEF_BRACKETS_2026: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]

#: Standard Art. 13 TUIR work-income deduction breakpoints for 2026.
WORK_DEDUCTIONS_2026: list[dict[str, Any]] = [
    {"income_up_to": "8500.00", "deduction": "1955.00"},
    {"income_up_to": "28000.00", "deduction": "700.00"},
    {"income_up_to": "50000.00", "deduction": "0.00"},
    {"income_up_to": None, "deduction": "0.00"},
]

#: INPS rates for terziario sector (no ceiling, simplified).
INPS_RATES_TERZIARIO: dict[str, Any] = {
    "employee_rate": "0.0919",
    "employer_rate": "0.2898",
    "ceiling": None,
}


def make_year_rules(
    brackets: list[dict[str, Any]] | None = None,
    deductions: list[dict[str, Any]] | None = None,
    inps: dict[str, Any] | None = None,
) -> YearRules:
    """Build a YearRules instance for testing. Defaults to the 2026 terziario values."""
    return YearRules.model_validate(
        {
            "year": 2026,
            "irpef_brackets": brackets or IRPEF_BRACKETS_2026,
            "work_deduction_breakpoints": deductions or WORK_DEDUCTIONS_2026,
            "fixed_term_additional_rate": "0.014",
            "inps": inps or INPS_RATES_TERZIARIO,
            "tfr": {"accrual_divisor": "13.5"},
        }
    )


def make_minimal_ccnl(*, app_type: str = "percentage") -> CCNL:
    """Build a minimal two-level CCNL with configurable apprenticeship type."""
    _period_l4 = {
        "periods": [
            {"valid_from": "2020-01-01", "valid_until": None, "value": "1000.00"}
        ]
    }
    _period_l3 = {
        "periods": [
            {"valid_from": "2020-01-01", "valid_until": None, "value": "800.00"}
        ]
    }
    _months_12 = {
        "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "12"}]
    }
    _seniority_amount = {
        "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "20.00"}]
    }
    apprenticeship: dict[str, Any]
    if app_type == "percentage":
        apprenticeship = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [{"months_from": 0, "months_until": None, "percentage": "0.80"}],
        }
    else:
        apprenticeship = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [
                {"months_from": 0, "months_until": None, "pay_level_code": "3"}
            ],
        }
    return CCNL.model_validate(
        {
            "schema_version": "0.2",
            "ccnl": {
                "id": "test",
                "name": "Test CCNL",
                "cnel_code": "X001",
                "sector": "test",
                "tax_sector": "terziario",
                "signatories": ["A", "B"],
                "sources": [{"url": "https://example.com", "type": "ccnl"}],
                "extraction": {
                    "method": "manual",
                    "model": None,
                    "timestamp": "2026-01-01T00:00:00Z",
                    "human_reviewed": True,
                },
            },
            "parameters": {
                "hourly_divisor": 168,
                "additional_months": _months_12,
                "seniority_increments": {
                    "cadence_months": 36,
                    "maximum_count": 10,
                    "amount_by_level": {"4": _seniority_amount},
                },
            },
            "levels": [
                {
                    "code": "3",
                    "order": 3,
                    "description": "Level 3",
                    "base_salary": _period_l3,
                    "fixed_allowances": [],
                },
                {
                    "code": "4",
                    "order": 4,
                    "description": "Level 4",
                    "base_salary": _period_l4,
                    "fixed_allowances": [],
                },
            ],
            "apprenticeship": apprenticeship,
            "coverage": {
                "layer_1": "implemented",
                "layer_2": "implemented",
                "layer_3": "out_of_scope",
                "notes": [],
            },
        }
    )


@pytest.fixture(scope="session")
def minimal_ccnl() -> CCNL:
    """Return a minimal two-level percentage-apprenticeship CCNL for engine tests."""
    return make_minimal_ccnl()


@pytest.fixture(scope="session")
def standard_year_rules() -> YearRules:
    """Return standard 2026 terziario YearRules for engine tests."""
    return make_year_rules()
