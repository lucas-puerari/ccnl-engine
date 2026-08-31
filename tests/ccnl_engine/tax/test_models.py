"""Tests for ccnl_engine.tax.models.

Covers every branch in YearRules validators and tests that the canonical
2026-terziario.json data file loads correctly via load_year_rules.
"""

from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.data.loaders import load_year_rules
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.tax.models import (
    DeductionBreakpoint,
    InpsRates,
    IrpefBracket,
    TfrRules,
    YearRules,
)

# ---------------------------------------------------------------------------
# Minimal valid fixture helpers
# ---------------------------------------------------------------------------

_VALID_BRACKETS: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]

_VALID_DEDUCTIONS: list[dict[str, Any]] = [
    {"income_up_to": "8500.00", "deduction": "1955.00"},
    {"income_up_to": "28000.00", "deduction": "700.00"},
    {"income_up_to": "50000.00", "deduction": "0.00"},
    {"income_up_to": None, "deduction": "0.00"},
]

_VALID_INPS: dict[str, Any] = {
    "employee_rate": "0.0919",
    "employer_rate": "0.2898",
    "ceiling": None,
}


def _year_rules(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a minimal valid YearRules dict, with optional field overrides."""
    base: dict[str, Any] = {
        "year": 2026,
        "irpef_brackets": _VALID_BRACKETS,
        "work_deduction_breakpoints": _VALID_DEDUCTIONS,
        "fixed_term_additional_rate": "0.014",
        "inps": _VALID_INPS,
        "tfr": {"accrual_divisor": "13.5"},
    }
    if overrides:
        base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# IrpefBracket
# ---------------------------------------------------------------------------


class TestIrpefBracket:
    """Unit tests for IrpefBracket construction."""

    def test_bounded_bracket(self) -> None:
        """A bracket with a finite up_to is accepted."""
        b = IrpefBracket(up_to=Decimal(28000), rate=Decimal("0.23"))
        assert b.up_to == Decimal(28000)

    def test_unbounded_bracket(self) -> None:
        """A bracket with up_to=None (unbounded) is accepted."""
        b = IrpefBracket(up_to=None, rate=Decimal("0.43"))
        assert b.up_to is None


# ---------------------------------------------------------------------------
# DeductionBreakpoint
# ---------------------------------------------------------------------------


class TestDeductionBreakpoint:
    """Unit tests for DeductionBreakpoint construction."""

    def test_finite_breakpoint(self) -> None:
        """A breakpoint with a finite income_up_to is accepted."""
        p = DeductionBreakpoint(income_up_to=Decimal(8500), deduction=Decimal(1955))
        assert p.income_up_to == Decimal(8500)

    def test_open_ended_breakpoint(self) -> None:
        """A breakpoint with income_up_to=None (open-ended) is accepted."""
        p = DeductionBreakpoint(income_up_to=None, deduction=Decimal(0))
        assert p.income_up_to is None


# ---------------------------------------------------------------------------
# InpsRates
# ---------------------------------------------------------------------------


class TestInpsRates:
    """Unit tests for InpsRates construction."""

    def test_uncapped(self) -> None:
        """ceiling=None (no cap) is accepted."""
        r = InpsRates(
            employee_rate=Decimal("0.0919"),
            employer_rate=Decimal("0.2898"),
            ceiling=None,
        )
        assert r.ceiling is None

    def test_with_ceiling(self) -> None:
        """A finite ceiling is accepted."""
        r = InpsRates(
            employee_rate=Decimal("0.09"),
            employer_rate=Decimal("0.28"),
            ceiling=Decimal(105014),
        )
        assert r.ceiling == Decimal(105014)


# ---------------------------------------------------------------------------
# YearRules — IRPEF bracket validators
# ---------------------------------------------------------------------------


class TestYearRulesIrpefBrackets:
    """YearRules validation for irpef_brackets."""

    def test_valid_three_brackets(self) -> None:
        """Three brackets with ascending up_to and open-ended last are valid."""
        yr = YearRules.model_validate(_year_rules())
        assert len(yr.irpef_brackets) == 3
        assert yr.irpef_brackets[-1].up_to is None

    def test_empty_brackets_raises(self) -> None:
        """An empty irpef_brackets list must raise ValidationError."""
        with pytest.raises(ValidationError, match="irpef_brackets must not be empty"):
            YearRules.model_validate(_year_rules({"irpef_brackets": []}))

    def test_non_last_bracket_open_ended_raises(self) -> None:
        """An intermediate bracket with up_to=None must raise ValidationError."""
        bad = [
            {"up_to": None, "rate": "0.23"},
            {"up_to": None, "rate": "0.43"},
        ]
        with pytest.raises(ValidationError, match="only the last irpef_bracket"):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_non_ascending_up_to_raises(self) -> None:
        """Non-ascending up_to values must raise ValidationError."""
        bad = [
            {"up_to": "50000.00", "rate": "0.23"},
            {"up_to": "28000.00", "rate": "0.33"},
            {"up_to": None, "rate": "0.43"},
        ]
        with pytest.raises(ValidationError, match="strictly ascending up_to"):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_last_bracket_not_open_ended_raises(self) -> None:
        """A last bracket with finite up_to must raise ValidationError."""
        bad = [
            {"up_to": "28000.00", "rate": "0.23"},
            {"up_to": "50000.00", "rate": "0.43"},
        ]
        with pytest.raises(
            ValidationError, match="last irpef_bracket must be unbounded"
        ):
            YearRules.model_validate(_year_rules({"irpef_brackets": bad}))

    def test_single_open_ended_bracket_valid(self) -> None:
        """A single unbounded bracket is valid (loop body never executes)."""
        single = [{"up_to": None, "rate": "0.23"}]
        yr = YearRules.model_validate(_year_rules({"irpef_brackets": single}))
        assert len(yr.irpef_brackets) == 1

    def test_two_brackets_second_open_ended_skips_ascending_check(self) -> None:
        """With two brackets, the ascending check is skipped for the last pair."""
        two = [
            {"up_to": "28000.00", "rate": "0.23"},
            {"up_to": None, "rate": "0.43"},
        ]
        yr = YearRules.model_validate(_year_rules({"irpef_brackets": two}))
        assert len(yr.irpef_brackets) == 2


# ---------------------------------------------------------------------------
# YearRules — deduction breakpoint validators
# ---------------------------------------------------------------------------


class TestYearRulesDeductionBreakpoints:
    """YearRules validation for work_deduction_breakpoints."""

    def test_valid_four_breakpoints(self) -> None:
        """Four breakpoints with ascending income_up_to are valid."""
        yr = YearRules.model_validate(_year_rules())
        assert len(yr.work_deduction_breakpoints) == 4
        assert yr.work_deduction_breakpoints[-1].income_up_to is None

    def test_empty_breakpoints_raises(self) -> None:
        """An empty work_deduction_breakpoints list must raise ValidationError."""
        with pytest.raises(
            ValidationError, match="work_deduction_breakpoints must not be empty"
        ):
            YearRules.model_validate(_year_rules({"work_deduction_breakpoints": []}))

    def test_non_last_breakpoint_open_ended_raises(self) -> None:
        """An intermediate breakpoint with income_up_to=None must raise."""
        bad = [
            {"income_up_to": None, "deduction": "1955.00"},
            {"income_up_to": None, "deduction": "0.00"},
        ]
        with pytest.raises(ValidationError, match="only the last deduction breakpoint"):
            YearRules.model_validate(_year_rules({"work_deduction_breakpoints": bad}))

    def test_non_ascending_income_up_to_raises(self) -> None:
        """Non-ascending income_up_to values must raise ValidationError."""
        bad = [
            {"income_up_to": "50000.00", "deduction": "1955.00"},
            {"income_up_to": "28000.00", "deduction": "700.00"},
            {"income_up_to": None, "deduction": "0.00"},
        ]
        with pytest.raises(ValidationError, match="strictly ascending income_up_to"):
            YearRules.model_validate(_year_rules({"work_deduction_breakpoints": bad}))

    def test_last_breakpoint_not_open_ended_raises(self) -> None:
        """Last breakpoint with finite income_up_to must raise ValidationError."""
        bad = [
            {"income_up_to": "8500.00", "deduction": "1955.00"},
            {"income_up_to": "50000.00", "deduction": "0.00"},
        ]
        with pytest.raises(
            ValidationError, match="last deduction breakpoint must be unbounded"
        ):
            YearRules.model_validate(_year_rules({"work_deduction_breakpoints": bad}))

    def test_single_open_ended_breakpoint_valid(self) -> None:
        """A single unbounded breakpoint is valid."""
        single = [{"income_up_to": None, "deduction": "1955.00"}]
        yr = YearRules.model_validate(
            _year_rules({"work_deduction_breakpoints": single})
        )
        assert len(yr.work_deduction_breakpoints) == 1

    def test_two_breakpoints_second_open_ended_skips_ascending_check(self) -> None:
        """Ascending check is skipped when next entry is the open-ended last."""
        two = [
            {"income_up_to": "8500.00", "deduction": "1955.00"},
            {"income_up_to": None, "deduction": "0.00"},
        ]
        yr = YearRules.model_validate(_year_rules({"work_deduction_breakpoints": two}))
        assert len(yr.work_deduction_breakpoints) == 2


# ---------------------------------------------------------------------------
# YearRules — 2026.json round-trip
# ---------------------------------------------------------------------------


class TestYearRules2026Json:
    """Validates that the 2026-terziario.json data file loads via load_year_rules."""

    def test_2026_json_loads(self) -> None:
        """load_year_rules(2026, terziario, 50) must return correct YearRules."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert yr.year == 2026
        assert len(yr.irpef_brackets) == 3
        assert yr.irpef_brackets[0].rate == Decimal("0.23")
        assert yr.irpef_brackets[1].rate == Decimal("0.33")
        assert yr.irpef_brackets[2].rate == Decimal("0.43")
        assert yr.inps.employee_rate == Decimal("0.0919")
        assert yr.inps.employer_rate == Decimal("0.2898")
        assert yr.inps.ceiling is None
        assert yr.fixed_term_additional_rate == Decimal("0.014")
        assert yr.tfr.accrual_divisor == Decimal("13.5")

    def test_tfr_rules(self) -> None:
        """TfrRules accrual_divisor is parsed as Decimal."""
        tfr = TfrRules(accrual_divisor=Decimal("13.5"))
        assert tfr.accrual_divisor == Decimal("13.5")
