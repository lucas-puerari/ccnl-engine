"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import copy
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

#: Apprentice rates for a large firm (L. 296/2006 art. 1 c. 773 + NASpI).
APPRENTICE_RATES_LARGE_FIRM: dict[str, Any] = {
    "employee_rate": "0.0584",
    "employer_rate_months_0_11": "0.1161",
    "employer_rate_months_12_23": "0.1161",
    "employer_rate_after": "0.1161",
}


def make_year_rules(
    brackets: list[dict[str, Any]] | None = None,
    deductions: list[dict[str, Any]] | None = None,
    inps: dict[str, Any] | None = None,
    apprentice: dict[str, Any] | None = None,
) -> YearRules:
    """Build a YearRules instance for testing. Defaults to the 2026 terziario values."""
    return YearRules.model_validate(
        {
            "year": 2026,
            "irpef_brackets": brackets or IRPEF_BRACKETS_2026,
            "work_deduction_breakpoints": deductions or WORK_DEDUCTIONS_2026,
            "fixed_term_additional_rate": "0.014",
            "inps": inps or INPS_RATES_TERZIARIO,
            "apprentice": apprentice or APPRENTICE_RATES_LARGE_FIRM,
            "tfr": {"accrual_divisor": "13.5"},
        }
    )


def _series(value: str, valid_from: str = "2020-01-01") -> dict[str, Any]:
    return {
        "periods": [{"valid_from": valid_from, "valid_until": None, "value": value}]
    }


def _level(code: str, order: int, salary: str) -> dict[str, Any]:
    return {
        "code": code,
        "order": order,
        "description": f"Level {code}",
        "base_salary": _series(salary),
        "fixed_allowances": [],
    }


#: Percentage track: destination level 4 paid at 80% throughout.
TRACK_PERCENTAGE: dict[str, Any] = {
    "type": "percentage",
    "name": "standard",
    "destination_levels": ["4"],
    "periods": [{"months_from": 0, "months_until": None, "percentage": "0.80"}],
}

#: Under-classification track: destination level 4 paid one level below.
TRACK_UNDER_CLASSIFICATION: dict[str, Any] = {
    "type": "under_classification",
    "name": "standard",
    "destination_levels": ["4"],
    "periods": [{"months_from": 0, "months_until": None, "levels_below": 1}],
}


def make_ccnl_dict(*, app_type: str = "percentage") -> dict[str, Any]:
    """Return a minimal three-level CCNL dict (levels 2, 3, 4) as raw data.

    Level 4 has a seniority increment of 20.00; levels 2 and 3 have none.
    """
    if app_type == "percentage":
        tracks = [copy.deepcopy(TRACK_PERCENTAGE)]
    elif app_type == "under_classification":
        tracks = [copy.deepcopy(TRACK_UNDER_CLASSIFICATION)]
    else:
        tracks = []
    return {
        "schema_version": "0.3",
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
        "coverage": {
            "layer_1": "implemented",
            "layer_2": "implemented" if tracks else "partial",
            "layer_3": "out_of_scope",
            "notes": [] if tracks else ["MISSING: apprenticeship not modelled."],
        },
        "parameters": {
            "hourly_divisor": _series("168"),
            "additional_months": _series("12"),
            "seniority_increments": {
                "cadence_months": 36,
                "maximum_count": 10,
                "amount_by_level": {"4": _series("20.00")},
            },
        },
        "levels": [
            _level("2", 2, "600.00"),
            _level("3", 3, "800.00"),
            _level("4", 4, "1000.00"),
        ],
        "apprenticeship": tracks,
    }


def make_minimal_ccnl(*, app_type: str = "percentage") -> CCNL:
    """Build a minimal three-level CCNL with configurable apprenticeship type."""
    return CCNL.model_validate(make_ccnl_dict(app_type=app_type))


@pytest.fixture(scope="session")
def minimal_ccnl() -> CCNL:
    """Return a minimal percentage-apprenticeship CCNL for engine tests."""
    return make_minimal_ccnl()


@pytest.fixture(scope="session")
def standard_year_rules() -> YearRules:
    """Return standard 2026 terziario YearRules for engine tests."""
    return make_year_rules()
