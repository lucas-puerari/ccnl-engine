"""Sanity checks of the independent 2026 IRPEF oracle against hand calculations.

Every expected value below was computed by hand from the formulas cited in
``tests/fixtures/legal_examples/irpef_2026.py`` (26 September 2026).  The
oracle is only trustworthy as an acceptance reference if these pass.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.tax.service.tax_annual_assembler import load_year_rules
from ccnl_engine.payroll.service.irpef_net import net_irpef as engine_net_irpef
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


def test_part_year_deductions_follow_the_days() -> None:
    """Income 30,438.68 EUR over 292 days (hired 15 March 2026).

    - gross: 6,440 + 2,438.68 * 33% = 7,244.76;
    - ratio 19,561.32 / 22,000 = 0.88915..., truncated 0.8891;
    - full-year employment deduction: 1,910 * 0.8891 + 65 = 1,763.18;
    - 292 / 365 = 0.8 exactly: employment deduction 1,410.54, further
      deduction 1,000 * 0.8 = 800.00;
    - net: 7,244.76 - 1,410.54 - 800.00 = 5,034.22.
    """
    income = Decimal("30438.68")
    assert employment_deduction(income, 292) == Decimal("1410.54")
    assert further_deduction(income, 292) == Decimal("800.00")
    assert net_irpef(income, 292) == Decimal("5034.22")


@pytest.mark.parametrize("days", [0, 366])
def test_out_of_scope_days_are_rejected(days: int) -> None:
    """An employment has 1 to 365 days in the year."""
    with pytest.raises(ValueError, match="days"):
        net_irpef(Decimal(30_000), days)


@pytest.mark.parametrize("income", [Decimal(-1), Decimal(200_001)])
def test_out_of_scope_income_is_rejected(income: Decimal) -> None:
    """Negative incomes and incomes above 200,000 EUR are outside the oracle."""
    with pytest.raises(ValueError, match="income"):
        net_irpef(income)


def test_taper_ratio_is_not_truncated() -> None:
    """Income 33,333.33 EUR: the c. 6 taper keeps its full precision.

    - taper ratio 6,666.67 / 8,000 = 0.83333375, not truncated (L. 207/2024
      art. 1 c. 6 lett. b) has no four-decimal rule);
    - further deduction: 1,000 * 0.83333375 = 833.33375, in cents 833.33.
      Truncating the ratio to 0.8333 would give 833.30.
    """
    assert further_deduction(Decimal("33333.33")) == Decimal("833.33")


def test_day_ratio_is_not_truncated() -> None:
    """Income 10,000 EUR over 92 days: 1,955 * 92 / 365 = 492.7671..., 492.77.

    Truncating 92 / 365 to 0.2520 would give 492.66.
    """
    assert employment_deduction(Decimal(10_000), 92) == Decimal("492.77")


_RULES = load_year_rules(2026, TaxSector.TERZIARIO, 50)


@pytest.mark.parametrize(
    "income",
    [
        Decimal(10000),
        Decimal("21182.05"),
        Decimal("30438.68"),
        Decimal("33333.33"),
        Decimal("36123.45"),
        Decimal("39999.99"),
        Decimal(45000),
    ],
)
@pytest.mark.parametrize("days", [92, 182, 292, 365])
def test_engine_matches_the_oracle(income: Decimal, days: int) -> None:
    """The engine net IRPEF equals the oracle for part-year and taper cases."""
    engine = engine_net_irpef(
        income, _RULES, family_deductions=Decimal(0), eligible_work_days=days
    )
    assert engine.net == net_irpef(income, days)
