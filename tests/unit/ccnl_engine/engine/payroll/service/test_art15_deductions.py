"""Unit tests for Art. 15 TUIR oneri detraibili service function."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.service.art15_deductions import compute_art15_deductions
from ccnl_engine.engine.tax.domain.art15 import (
    Art15DeductionRules,
    MortgageInterestRules,
)
from ccnl_engine.engine.tax.service.loaders import load_art15_deduction_rules

_D = Decimal
_RULES = load_art15_deduction_rules(2026)


def _rules(ceiling: str = "4000", rate: str = "0.19") -> Art15DeductionRules:
    """Build an Art15DeductionRules with the given mortgage_interest parameters.

    Returns:
        An :class:`Art15DeductionRules` configured with the given ceiling/rate.
    """
    return Art15DeductionRules(
        year=2026,
        mortgage_interest=MortgageInterestRules(
            ceiling=_D(ceiling),
            rate=_D(rate),
        ),
    )


class TestComputeArt15Deductions:
    """compute_art15_deductions — mortgage interest credit computation."""

    def test_below_ceiling_credit_is_rate_times_amount(self) -> None:
        """Interest below ceiling: credit = rate * interest."""
        ded = Art15Deductions(mortgage_interest=_D("3000"))
        result = compute_art15_deductions(ded, _rules())
        assert result == _D("570.00")  # 3000 * 0.19

    def test_at_ceiling_credit_is_rate_times_ceiling(self) -> None:
        """Interest exactly at ceiling: credit = rate * ceiling."""
        ded = Art15Deductions(mortgage_interest=_D("4000"))
        result = compute_art15_deductions(ded, _rules())
        assert result == _D("760.00")  # 4000 * 0.19

    def test_above_ceiling_credit_capped_at_max(self) -> None:
        """Interest above ceiling: credit capped at rate * ceiling."""
        ded = Art15Deductions(mortgage_interest=_D("5000"))
        result = compute_art15_deductions(ded, _rules())
        assert result == _D("760.00")  # min(5000, 4000) * 0.19

    def test_zero_interest_yields_zero_credit(self) -> None:
        """Zero interest: no credit."""
        ded = Art15Deductions(mortgage_interest=_D("0"))
        result = compute_art15_deductions(ded, _rules())
        assert result == _D("0.00")

    def test_custom_ceiling_and_rate(self) -> None:
        """Custom ceiling and rate applied correctly."""
        ded = Art15Deductions(mortgage_interest=_D("2000"))
        result = compute_art15_deductions(ded, _rules(ceiling="3000", rate="0.20"))
        assert result == _D("400.00")  # 2000 * 0.20

    def test_rounding_to_two_decimal_places(self) -> None:
        """Result is rounded to 2 decimal places via money()."""
        ded = Art15Deductions(mortgage_interest=_D("1"))
        result = compute_art15_deductions(ded, _rules(ceiling="4000", rate="0.19"))
        # 1 * 0.19 = 0.19 — exact, no rounding needed
        assert result == _D("0.19")


class TestLoadArt15DeductionRules:
    """load_art15_deduction_rules — knowledge-base file loading."""

    def test_loads_year_2026(self) -> None:
        """Rules for year 2026 load without error."""
        rules = load_art15_deduction_rules(2026)
        assert rules.year == 2026

    def test_mortgage_interest_ceiling_2026(self) -> None:
        """2026 mortgage interest ceiling is EUR 4 000."""
        rules = load_art15_deduction_rules(2026)
        assert rules.mortgage_interest.ceiling == _D("4000.00")

    def test_mortgage_interest_rate_2026(self) -> None:
        """2026 mortgage interest deduction rate is 19 %."""
        rules = load_art15_deduction_rules(2026)
        assert rules.mortgage_interest.rate == _D("0.19")

    def test_wrong_year_raises(self) -> None:
        """Requesting a year not in the bundle raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_art15_deduction_rules(1900)
