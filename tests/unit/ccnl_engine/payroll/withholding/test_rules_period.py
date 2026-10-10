"""period_tax: IRPEF of one pay period under art. 23 c. 2 DPR 600/1973.

The 2026 brackets of art. 11 TUIR (23% to 28,000, 33% to 50,000, 43%
above) divided by twelve: 2,333.33... and 4,166.66...
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.taxation.rules_irpef import period_irpef_gross
from ccnl_engine.payroll.taxation.rules_irpef_credit import CreditOutcome
from ccnl_engine.payroll.taxation.rules_irpef_net import NetIrpef
from ccnl_engine.payroll.withholding.rules_period import (
    NO_PAY,
    PayPeriod,
    PeriodTax,
    period_tax,
)
from tests.unit.ccnl_engine.builders import make_year_rules

_ZERO = Decimal(0)
_RULES = make_year_rules()
_SHARE = Decimal(31) / 365


def _annual(work: str, ulteriore: str | None = None) -> NetIrpef:
    outcome = (
        None
        if ulteriore is None
        else CreditOutcome(amount=Decimal(ulteriore), reason_code="full_amount")
    )
    return NetIrpef(
        gross=_ZERO,
        work_deduction=Decimal(work),
        family_deductions=_ZERO,
        ulteriore=outcome,
    )


def test_period_brackets_are_the_annual_ones_over_twelve() -> None:
    """5,000 a month: 23% of 2,333.33 + 33% to 4,166.67 + 43% of the rest.

    536.67 + 605.00 + 358.33 = 1,500.00, the annual tax of 60,000 over 12.
    """
    assert period_irpef_gross(Decimal(5000), _RULES) == Decimal("1500.00")
    assert period_irpef_gross(_ZERO, _RULES) == _ZERO


def test_regular_pay_takes_the_deductions_of_the_period() -> None:
    """1,953.45 taxed 23% = 449.29; 2,213.48 x 31/365 = 187.99; 84.93 more.

    The ulteriore detrazione of 1,000 for 31 days is 84.93: 449.29 - 187.99
    - 84.93 = 176.37 with it, 261.30 without it.
    """
    period = PayPeriod(regular_taxable=Decimal("1953.45"), day_share=_SHARE)
    tax = period_tax(period, _annual("2213.48", "1000.00"), _RULES)
    assert tax == PeriodTax(Decimal("176.37"), Decimal("261.30"))


def test_additional_month_takes_no_deduction() -> None:
    """Lett. b): 809.92 taxed 23% = 186.28, whatever the annual deductions."""
    period = PayPeriod(separate_taxable=Decimal("809.92"))
    tax = period_tax(period, _annual("2213.48", "1000.00"), _RULES)
    assert tax == PeriodTax(Decimal("186.28"), Decimal("186.28"))


def test_deductions_above_the_tax_floor_the_period_at_zero() -> None:
    """143.25 taxed 23% = 32.95, below the deductions of the month.

    A premium of 1,000 on the same run keeps its lett. b) tax, 230.00.
    """
    period = PayPeriod(
        regular_taxable=Decimal("143.25"),
        separate_taxable=Decimal(1000),
        day_share=_SHARE,
        family=Decimal("57.50"),
    )
    tax = period_tax(period, _annual("1955.00"), _RULES)
    assert tax == PeriodTax(Decimal("230.00"), Decimal("230.00"))


def test_no_pay_withholds_nothing() -> None:
    """A run that pays nothing has no tax of its period."""
    assert period_tax(NO_PAY, _annual("1955.00"), _RULES) == PeriodTax(_ZERO, _ZERO)
