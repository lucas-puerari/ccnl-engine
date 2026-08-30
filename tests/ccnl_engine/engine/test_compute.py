"""Tests for engine.compute — compute() and private helper functions.

100% branch coverage:
* all validation error paths
* permanent / fixed-term / apprentice employment dispatches
* ApprenticeshipPercentage and ApprenticeshipUnderClassification branches
* negotiated_ral override paths
* level without a seniority entry
* IRPEF net floored at zero
* private helper ValueError paths (called directly to reach unreachable branches)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.engine.compute import (
    _find_apprenticeship_percentage,
    _find_under_classification_code,
    compute,
)
from ccnl_engine.models.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.models.ccnl import CCNL
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.tax.models import YearRules

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DATE = date(2026, 6, 1)
_D = Decimal

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

_META = {
    "id": "test",
    "name": "Test CCNL",
    "cnel_code": "X001",
    "sector": "test",
    "signatories": ["A", "B"],
    "sources": [{"url": "https://example.com", "type": "ccnl"}],
    "extraction": {
        "method": "manual",
        "model": None,
        "timestamp": "2026-01-01T00:00:00Z",
        "human_reviewed": True,
    },
}

_PERIOD_L4 = {
    "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "1000.00"}]
}
_PERIOD_L3 = {
    "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "800.00"}]
}
_MONTHS_12 = {
    "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "12"}]
}
_SENIORITY_AMOUNT = {
    "periods": [{"valid_from": "2020-01-01", "valid_until": None, "value": "20.00"}]
}


def _make_ccnl(*, app_type: str = "percentage") -> CCNL:
    """Build a minimal valid CCNL with two levels and configurable apprenticeship."""
    if app_type == "percentage":
        apprenticeship: dict[str, Any] = {
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
            "ccnl": _META,
            "parameters": {
                "hourly_divisor": 168,
                "additional_months": _MONTHS_12,
                "seniority_increments": {
                    "cadence_months": 36,
                    "maximum_count": 10,
                    # only level "4" has a seniority entry; "3" does not
                    "amount_by_level": {"4": _SENIORITY_AMOUNT},
                },
            },
            "levels": [
                {
                    "code": "3",
                    "order": 3,
                    "description": "Level 3",
                    "base_salary": _PERIOD_L3,
                    "fixed_allowances": [],
                },
                {
                    "code": "4",
                    "order": 4,
                    "description": "Level 4",
                    "base_salary": _PERIOD_L4,
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


_VALID_BRACKETS = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]
_VALID_DEDUCTIONS = [
    {"income_up_to": "8500.00", "deduction": "1955.00"},
    {"income_up_to": "28000.00", "deduction": "700.00"},
    {"income_up_to": "50000.00", "deduction": "0.00"},
    {"income_up_to": None, "deduction": "0.00"},
]


def _make_rules() -> YearRules:
    """Build standard 2026 YearRules."""
    return YearRules.model_validate(
        {
            "year": 2026,
            "irpef_brackets": _VALID_BRACKETS,
            "work_deduction_breakpoints": _VALID_DEDUCTIONS,
            "fixed_term_additional_rate": "0.014",
            "inps": {
                "employee_rate": "0.0919",
                "employer_rate": "0.2898",
                "ceiling": None,
            },
            "tfr": {"accrual_divisor": "13.5"},
        }
    )


# Pre-built fixtures shared by most tests
_CCNL = _make_ccnl()
_CCNL_UC = _make_ccnl(app_type="under_classification")
_RULES = _make_rules()
_PERMANENT = Permanent(type="permanent")
_FIXED_TERM = FixedTerm(type="fixed_term")


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


class TestComputeValidation:
    """Guard-clause branches at the top of compute()."""

    def test_part_time_pct_zero_raises(self) -> None:
        """part_time_pct=0 is not in (0, 1] — must raise ValueError."""
        with pytest.raises(ValueError, match="part_time_pct"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, part_time_pct=_D(0))

    def test_part_time_pct_negative_raises(self) -> None:
        """Negative part_time_pct must raise ValueError."""
        with pytest.raises(ValueError, match="part_time_pct"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, part_time_pct=_D("-0.1"))

    def test_part_time_pct_above_one_raises(self) -> None:
        """part_time_pct > 1 must raise ValueError."""
        with pytest.raises(ValueError, match="part_time_pct"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, part_time_pct=_D("1.01"))

    def test_seniority_count_negative_raises(self) -> None:
        """Negative seniority_count must raise ValueError."""
        with pytest.raises(ValueError, match="seniority_count"):
            compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_count=-1)

    def test_unknown_level_code_raises(self) -> None:
        """Unknown level_code must raise KeyError."""
        with pytest.raises(KeyError, match="NOPE"):
            compute(_CCNL, "NOPE", _DATE, _RULES, _PERMANENT)


# ---------------------------------------------------------------------------
# Permanent employment
# ---------------------------------------------------------------------------


class TestComputePermanent:
    """Permanent contract paths in compute()."""

    def test_full_time_no_seniority(self) -> None:
        """Permanent, full-time, no seniority: standard salary chain."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT)

        assert r.ccnl_id == "test"
        assert r.level_code == "4"
        assert r.employment_type == "permanent"
        assert r.part_time_pct == _D(1)
        assert r.as_of == _DATE
        assert r.year == 2026

        assert r.base_monthly == _D("1000.00")
        assert r.seniority_monthly == _D("0.00")
        assert r.allowances_monthly == _D("0.00")
        assert r.gross_monthly == _D("1000.00")
        assert r.gross_annual == _D("12000.00")

        assert r.apprenticeship_pct is None
        assert r.apprenticeship_under_level_code is None

        # Relational invariants
        assert r.taxable_income == r.gross_annual - r.inps_employee_annual
        assert r.irpef_net == max(_D(0), r.irpef_gross - r.work_income_deduction)
        assert r.net_annual == r.gross_annual - r.inps_employee_annual - r.irpef_net
        assert r.employer_cost_annual == (
            r.gross_annual + r.inps_employer_annual + r.tfr_annual
        )

    def test_with_seniority(self) -> None:
        """Seniority_count=2 adds 2 * 20 = 40 to monthly gross."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, seniority_count=2)

        assert r.seniority_monthly == _D("40.00")
        assert r.gross_monthly == _D("1040.00")
        assert r.gross_annual == _D("12480.00")

    def test_part_time(self) -> None:
        """part_time_pct=0.5 halves gross_monthly and gross_annual."""
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, part_time_pct=_D("0.50"))

        assert r.gross_monthly == _D("500.00")
        assert r.gross_annual == _D("6000.00")

    def test_negotiated_ral(self) -> None:
        """negotiated_ral overrides the CCNL-derived gross_annual."""
        ral = _D("20000.00")
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, negotiated_ral=ral)

        assert r.gross_annual == ral

    def test_level_without_seniority_entry(self) -> None:
        """Level '3' has no seniority in amount_by_level — seniority stays zero."""
        r = compute(_CCNL, "3", _DATE, _RULES, _PERMANENT, seniority_count=5)

        assert r.seniority_monthly == _D("0.00")
        assert r.base_monthly == _D("800.00")
        assert r.gross_annual == _D("9600.00")


# ---------------------------------------------------------------------------
# Fixed-term employment
# ---------------------------------------------------------------------------


class TestComputeFixedTerm:
    """Fixed-term contract adds NASpI addizionale to employer INPS."""

    def test_fixed_term_naspi_addizionale(self) -> None:
        """Employer INPS for fixed-term must exceed permanent by 1.4% of gross."""
        r_fixed = compute(_CCNL, "4", _DATE, _RULES, _FIXED_TERM)
        r_perm = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT)

        # NASpI addizionale = 1.4% of gross_annual
        expected_diff = r_fixed.gross_annual * _D("0.014")
        actual_diff = r_fixed.inps_employer_annual - r_perm.inps_employer_annual
        # Both are money()-rounded; allow for rounding artefact of at most 1 cent
        assert abs(actual_diff - expected_diff) <= _D("0.01")
        assert r_fixed.employment_type == "fixed_term"


# ---------------------------------------------------------------------------
# IRPEF floor
# ---------------------------------------------------------------------------


class TestComputeIrpefFloor:
    """net = gross - inps when deduction exceeds gross IRPEF."""

    def test_irpef_net_floored_at_zero(self) -> None:
        """Low income: deduction > irpef_gross → irpef_net == 0."""
        # gross_annual=5000 → taxable~4540 → irpef_gross~1044 < deduction 1955
        r = compute(_CCNL, "4", _DATE, _RULES, _PERMANENT, negotiated_ral=_D("5000.00"))

        assert r.irpef_net == _D("0.00")
        assert r.net_annual == r.gross_annual - r.inps_employee_annual


# ---------------------------------------------------------------------------
# Apprentice — percentage
# ---------------------------------------------------------------------------


class TestComputeApprenticePercentage:
    """ApprenticeshipPercentage dispatch."""

    def test_basic(self) -> None:
        """Apprentice salary = destination-level salary * pct (0.80)."""
        apprentice = Apprentice(type="apprentice", months_elapsed=0)
        r = compute(_CCNL, "4", _DATE, _RULES, apprentice)

        # base_gross = 1000 * 12 = 12000; gross_annual = money(12000 * 0.80)
        assert r.apprenticeship_pct == _D("0.80")
        assert r.apprenticeship_under_level_code is None
        assert r.gross_annual == _D("9600.00")
        assert r.employment_type == "apprentice"

    def test_negotiated_ral(self) -> None:
        """negotiated_ral is applied as base before percentage multiplication."""
        apprentice = Apprentice(type="apprentice", months_elapsed=0)
        ral = _D("20000.00")
        r = compute(_CCNL, "4", _DATE, _RULES, apprentice, negotiated_ral=ral)

        assert r.gross_annual == _D("16000.00")


# ---------------------------------------------------------------------------
# Apprentice — under-classification
# ---------------------------------------------------------------------------


class TestComputeApprenticeUnderClassification:
    """ApprenticeshipUnderClassification dispatch."""

    def test_basic(self) -> None:
        """Apprentice paid at level '3' (800/month * 12 = 9600 annual)."""
        apprentice = Apprentice(type="apprentice", months_elapsed=0)
        r = compute(_CCNL_UC, "4", _DATE, _RULES, apprentice)

        assert r.apprenticeship_under_level_code == "3"
        assert r.apprenticeship_pct is None
        assert r.gross_annual == _D("9600.00")

    def test_negotiated_ral(self) -> None:
        """negotiated_ral overrides the under-classification pay computation."""
        apprentice = Apprentice(type="apprentice", months_elapsed=0)
        ral = _D("20000.00")
        r = compute(_CCNL_UC, "4", _DATE, _RULES, apprentice, negotiated_ral=ral)

        assert r.gross_annual == ral


# ---------------------------------------------------------------------------
# Private helpers — not-found paths
# ---------------------------------------------------------------------------


class TestFindApprenticeshipPercentage:
    """Direct unit tests for _find_apprenticeship_percentage()."""

    def test_found(self) -> None:
        """Period that covers months_elapsed is returned."""
        app = ApprenticeshipPercentage.model_validate(
            {
                "type": "percentage",
                "destination_level": "4",
                "periods": [
                    {"months_from": 0, "months_until": None, "percentage": "0.75"}
                ],
            }
        )
        assert _find_apprenticeship_percentage(app, 0) == _D("0.75")

    def test_not_found_raises(self) -> None:
        """months_elapsed before the first period raises ValueError."""
        app = ApprenticeshipPercentage.model_validate(
            {
                "type": "percentage",
                "destination_level": "4",
                "periods": [
                    {"months_from": 10, "months_until": None, "percentage": "0.80"}
                ],
            }
        )
        with pytest.raises(ValueError, match="months_elapsed"):
            _find_apprenticeship_percentage(app, months_elapsed=5)


class TestFindUnderClassificationCode:
    """Direct unit tests for _find_under_classification_code()."""

    def test_found(self) -> None:
        """Period that covers months_elapsed is returned."""
        app = ApprenticeshipUnderClassification.model_validate(
            {
                "type": "under_classification",
                "destination_level": "4",
                "periods": [
                    {
                        "months_from": 0,
                        "months_until": None,
                        "pay_level_code": "3",
                    }
                ],
            }
        )
        assert _find_under_classification_code(app, 0) == "3"

    def test_not_found_raises(self) -> None:
        """months_elapsed before the first period raises ValueError."""
        app = ApprenticeshipUnderClassification.model_validate(
            {
                "type": "under_classification",
                "destination_level": "4",
                "periods": [
                    {
                        "months_from": 10,
                        "months_until": None,
                        "pay_level_code": "3",
                    }
                ],
            }
        )
        with pytest.raises(ValueError, match="months_elapsed"):
            _find_under_classification_code(app, months_elapsed=5)
