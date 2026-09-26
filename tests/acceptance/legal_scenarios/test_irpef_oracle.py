"""Sanity checks of the independent 2026 IRPEF oracle against hand calculations.

Every expected value below was computed by hand from the formulas cited in
``tests/fixtures/legal_examples/irpef_2026.py`` (26 September 2026).  The
oracle is only trustworthy as an acceptance reference if these pass.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.fixtures.legal_examples.irpef_2026 import (
    employment_deduction,
    further_deduction,
    gross_irpef,
    net_irpef,
)

pytestmark = pytest.mark.legal_scenario


def test_first_bracket_with_further_deduction() -> None:
    """Income 21,182.05 EUR, the final taxable of the Cooperative Sociali case.

    - gross: 21,182.05 * 23% = 4,871.8715, rounded 4,871.87 (art. 11 TUIR);
    - ratio (28,000 - 21,182.05) / 13,000 = 0.524457..., truncated 0.5244;
    - employment deduction: 1,910 + 1,190 * 0.5244 = 2,534.04 (art. 13 TUIR);
    - further deduction: 1,000 (L. 207/2024 art. 1 c. 6, income in 20k-32k);
    - net: 4,871.87 - 2,534.04 - 1,000 = 1,337.83.
    """
    income = Decimal("21182.05")
    assert gross_irpef(income) == Decimal("4871.87")
    assert employment_deduction(income) == Decimal("2534.04")
    assert further_deduction(income) == Decimal("1000.00")
    assert net_irpef(income) == Decimal("1337.83")


def test_second_bracket_with_65_euro_increase() -> None:
    """Income 30,000 EUR.

    - gross: 28,000 * 23% + 2,000 * 33% = 6,440 + 660 = 7,100.00;
    - ratio 20,000 / 22,000 = 0.90909..., truncated 0.9090;
    - employment deduction: 1,910 * 0.9090 + 65 = 1,736.19 + 65 = 1,801.19;
    - further deduction: 1,000;
    - net: 7,100.00 - 1,801.19 - 1,000 = 4,298.81.
    """
    assert net_irpef(Decimal(30_000)) == Decimal("4298.81")


def test_decreasing_further_deduction() -> None:
    """Income 36,000 EUR.

    - gross: 6,440 + 8,000 * 33% = 9,080.00;
    - ratio 14,000 / 22,000 = 0.63636..., truncated 0.6363;
    - employment deduction: 1,910 * 0.6363 = 1,215.33 (no 65, income > 35k);
    - further deduction: 1,000 * 4,000 / 8,000 = 500.00;
    - net: 9,080.00 - 1,215.33 - 500.00 = 7,364.67.
    """
    assert net_irpef(Decimal(36_000)) == Decimal("7364.67")


def test_third_bracket_without_deductions() -> None:
    """Income 60,000 EUR: 6,440 + 7,260 + 10,000 * 43% = 18,000.00, no deductions."""
    assert net_irpef(Decimal(60_000)) == Decimal("18000.00")


def test_low_income_flat_deduction() -> None:
    """Income 10,000 EUR: 2,300.00 gross minus the flat 1,955 = 345.00."""
    assert net_irpef(Decimal(10_000)) == Decimal("345.00")


def test_deductions_are_not_refundable() -> None:
    """Income 5,000 EUR: 1,150.00 gross, 1,955 deduction, net floored at zero."""
    assert net_irpef(Decimal(5_000)) == Decimal("0.00")


@pytest.mark.parametrize("income", [Decimal(-1), Decimal(200_001)])
def test_out_of_scope_income_is_rejected(income: Decimal) -> None:
    """Negative incomes and incomes above 200,000 EUR are outside the oracle."""
    with pytest.raises(ValueError, match="income"):
        net_irpef(income)
