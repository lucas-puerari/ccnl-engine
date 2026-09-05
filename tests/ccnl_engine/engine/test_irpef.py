"""Tests for engine.irpef — irpef_gross() and work_income_deduction().

Covers every branch: zero/negative income, income in each bracket, spanning
multiple brackets, income above the last finite breakpoint, and the single-
open-ended-breakpoint edge case for the fallback return path.
"""

from decimal import Decimal
from typing import Any

from ccnl_engine.engine.irpef import (
    irpef_gross,
    surtax_from_brackets,
    work_income_deduction,
)
from ccnl_engine.surtax.models import SurtaxBracket
from ccnl_engine.tax.models import YearRules
from tests.conftest import make_year_rules

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_IRPEF_BRACKETS_2026: list[dict[str, Any]] = [
    {"up_to": "28000.00", "rate": "0.23"},
    {"up_to": "50000.00", "rate": "0.33"},
    {"up_to": None, "rate": "0.43"},
]

_STANDARD_DEDUCTIONS = [
    {"income_up_to": "8500.00", "deduction": "1955.00"},
    {"income_up_to": "28000.00", "deduction": "700.00"},
    {"income_up_to": "50000.00", "deduction": "0.00"},
    {"income_up_to": None, "deduction": "0.00"},
]


def _rules(deductions: list[dict[str, Any]] | None = None) -> YearRules:
    """Minimal YearRules with the 2026 IRPEF brackets and configurable deductions.

    Returns:
        A YearRules instance with the specified deduction breakpoints.
    """
    return make_year_rules(brackets=_IRPEF_BRACKETS_2026, deductions=deductions)


# ---------------------------------------------------------------------------
# irpef_gross
# ---------------------------------------------------------------------------


class TestIrpefGross:
    """Unit tests for irpef_gross()."""

    def test_zero_income(self) -> None:
        """Zero income yields zero tax (early return branch)."""
        assert irpef_gross(Decimal(0), _rules()) == Decimal("0.00")

    def test_negative_income(self) -> None:
        """Negative income yields zero tax (early return branch)."""
        assert irpef_gross(Decimal(-100), _rules()) == Decimal("0.00")

    def test_income_in_first_bracket(self) -> None:
        """Income fully inside the first bracket: only 23% applies.

        10,000 * 0.23 = 2,300.00. The break path (taxable_income <= prev_limit)
        is exercised on the second bracket iteration.
        """
        result = irpef_gross(Decimal("10000.00"), _rules())
        assert result == Decimal("2300.00")

    def test_income_at_first_bracket_boundary(self) -> None:
        """Income exactly at the first bracket boundary (28,000)."""
        result = irpef_gross(Decimal("28000.00"), _rules())
        assert result == Decimal("6440.00")  # 28000 * 0.23

    def test_income_spanning_two_brackets(self) -> None:
        """Income in the second bracket: 23% on first 28k + 33% on excess.

        35,000: 28,000 * 0.23 = 6,440 + 7,000 * 0.33 = 2,310 = 8,750.
        The unbounded bracket branch (taxable_income > prev_limit = False) is
        exercised on the third iteration.
        """
        result = irpef_gross(Decimal("35000.00"), _rules())
        assert result == Decimal("8750.00")

    def test_income_in_third_bracket(self) -> None:
        """Income above 50k: all three brackets apply.

        60,000:
          28,000 * 0.23 = 6,440.00
          22,000 * 0.33 = 7,260.00
          10,000 * 0.43 = 4,300.00
          Total = 18,000.00
        """
        result = irpef_gross(Decimal("60000.00"), _rules())
        assert result == Decimal("18000.00")


# ---------------------------------------------------------------------------
# work_income_deduction
# ---------------------------------------------------------------------------


class TestWorkIncomeDeduction:
    """Unit tests for work_income_deduction()."""

    def test_zero_income(self) -> None:
        """Zero income returns zero deduction (early return branch)."""
        assert work_income_deduction(Decimal(0), _rules()) == Decimal("0.00")

    def test_negative_income(self) -> None:
        """Negative income returns zero deduction."""
        assert work_income_deduction(Decimal(-1), _rules()) == Decimal("0.00")

    def test_income_at_flat_segment_top(self) -> None:
        """Income exactly at 8,500 returns the flat deduction of EUR 1,955."""
        assert work_income_deduction(Decimal(8500), _rules()) == Decimal("1955.00")

    def test_income_below_flat_segment(self) -> None:
        """Income below 8,500 also returns the flat deduction of EUR 1,955."""
        assert work_income_deduction(Decimal(5000), _rules()) == Decimal("1955.00")

    def test_income_in_first_tapered_segment(self) -> None:
        """Income in (8,500, 28,000]: linear interpolation toward EUR 700.

        At 18,250 (midpoint): fraction = (18250-8500)/(28000-8500) = 0.5.
        deduction = 1955 + 0.5*(700-1955) = 1955 - 627.5 = 1327.50.
        """
        result = work_income_deduction(Decimal(18250), _rules())
        assert result == Decimal("1327.50")

    def test_income_at_segment_boundary_28000(self) -> None:
        """Income exactly at 28,000 returns EUR 700 (boundary interpolation)."""
        result = work_income_deduction(Decimal(28000), _rules())
        assert result == Decimal("700.00")

    def test_income_in_second_tapered_segment(self) -> None:
        """Income in (28,000, 50,000]: linear interpolation toward zero.

        At 39,000 (midpoint): fraction = (39000-28000)/(50000-28000) = 0.5.
        deduction = 700 + 0.5*(0-700) = 350.00.
        """
        result = work_income_deduction(Decimal(39000), _rules())
        assert result == Decimal("350.00")

    def test_income_above_all_finite_breakpoints(self) -> None:
        """Income > 50,000 hits the hi_income is None branch, deduction = 0."""
        result = work_income_deduction(Decimal(55000), _rules())
        assert result == Decimal("0.00")

    def test_single_open_ended_breakpoint_fallback(self) -> None:
        """Single open-ended breakpoint: loop is empty, fallback return fires.

        This covers the ``return money(points[-1].deduction)`` path after the
        for-loop when the loop body never executes.
        """
        single_deduction = [{"income_up_to": None, "deduction": "1955.00"}]
        rules = _rules(deductions=single_deduction)
        # first.income_up_to is None → flat-segment if-condition is False;
        # loop range is empty → falls through to final return
        result = work_income_deduction(Decimal(10000), rules)
        assert result == Decimal("1955.00")


# ---------------------------------------------------------------------------
# surtax_from_brackets
# ---------------------------------------------------------------------------


def _brackets(*specs: tuple[float | None, str]) -> list[SurtaxBracket]:
    """Build a SurtaxBracket list from (up_to, rate) tuples.

    Returns:
        A list of SurtaxBracket instances.
    """
    return [
        SurtaxBracket(
            up_to=Decimal(str(up_to)) if up_to is not None else None,
            rate=Decimal(rate),
        )
        for up_to, rate in specs
    ]


class TestSurtaxFromBrackets:
    """Unit tests for surtax_from_brackets()."""

    def test_zero_income(self) -> None:
        """Zero income → zero surtax."""
        bs = _brackets((None, "0.0123"))
        assert surtax_from_brackets(Decimal(0), bs) == Decimal("0.00")

    def test_negative_income(self) -> None:
        """Negative income → zero surtax."""
        bs = _brackets((None, "0.0123"))
        assert surtax_from_brackets(Decimal(-100), bs) == Decimal("0.00")

    def test_flat_rate(self) -> None:
        """Single unbounded bracket: flat rate on full income."""
        bs = _brackets((None, "0.0123"))
        # 30 000 * 1.23% = 369.00
        assert surtax_from_brackets(Decimal(30000), bs) == Decimal("369.00")

    def test_marginal_brackets(self) -> None:
        """Multiple brackets: marginal computation across slices.

        Lazio-style: 1.62% ≤15k, 2.68% ≤28k, 3.31% ≤50k, 3.33%+.
        Income 30000: 15000*1.62%+13000*2.68%+2000*3.31% = 657.60.
        """
        bs = _brackets(
            (15000, "0.0162"),
            (28000, "0.0268"),
            (50000, "0.0331"),
            (None, "0.0333"),
        )
        assert surtax_from_brackets(Decimal(30000), bs) == Decimal("657.60")

    def test_income_within_first_bracket(self) -> None:
        """Income inside the first finite bracket: 10000 * 1.67% = 167.00."""
        bs = _brackets((28000, "0.0167"), (50000, "0.0287"), (None, "0.0333"))
        assert surtax_from_brackets(Decimal(10000), bs) == Decimal("167.00")

    def test_income_exactly_at_bracket_boundary(self) -> None:
        """Income at a bracket upper bound: 15000 * 1.33% = 199.50."""
        bs = _brackets((15000, "0.0133"), (None, "0.0193"))
        assert surtax_from_brackets(Decimal(15000), bs) == Decimal("199.50")

    def test_income_above_all_brackets(self) -> None:
        """Income above all finite brackets: 28k*1.67%+22k*2.87%+10k*3.33% = 1432."""
        bs = _brackets((28000, "0.0167"), (50000, "0.0287"), (None, "0.0333"))
        assert surtax_from_brackets(Decimal(60000), bs) == Decimal("1432.00")

    def test_soglia_below_income_no_effect(self) -> None:
        """Soglia below taxable income: full income taxed. 20000 * 0.8% = 160.00."""
        bs = _brackets((None, "0.008"))
        assert surtax_from_brackets(Decimal(20000), bs, Decimal(5000)) == Decimal(
            "160.00"
        )

    def test_soglia_equal_to_income(self) -> None:
        """Income exactly equal to soglia → zero surtax."""
        bs = _brackets((None, "0.008"))
        assert surtax_from_brackets(Decimal(12000), bs, Decimal(12000)) == Decimal(
            "0.00"
        )

    def test_soglia_above_income(self) -> None:
        """Income below soglia → zero surtax."""
        bs = _brackets((None, "0.008"))
        assert surtax_from_brackets(Decimal(8000), bs, Decimal(12000)) == Decimal(
            "0.00"
        )

    def test_zero_rate_bracket(self) -> None:
        """A zero-rate flat bracket yields zero."""
        bs = _brackets((None, "0"))
        assert surtax_from_brackets(Decimal(30000), bs) == Decimal("0.00")
