"""The art. 15 TUIR deduction of the charges via the employer."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.tax_credit.art15.inputs import Art15Expense, Art15Kind
from ccnl_engine.tax_credit.art15.rules import art15_deduction

_INCOME = Decimal(30000)


def _of(**amounts: int) -> tuple[Art15Expense, ...]:
    return tuple(Art15Expense(Art15Kind(k), Decimal(v)) for k, v in amounts.items())


@pytest.mark.parametrize(
    ("expenses", "income", "deduction"),
    [
        # 19% above the 129.11 franchise: 870.89 x 19% = 165.47.
        (_of(health=1000), _INCOME, Decimal("165.47")),
        (_of(health=100), _INCOME, Decimal("0.00")),
        # Life premiums capped at 530: 100.70.
        (_of(life_insurance=900), _INCOME, Decimal("100.70")),
        # Protection raises the cap to 750 with the life premiums: 142.50.
        (
            _of(life_insurance=500, disability_protection_insurance=500),
            _INCOME,
            Decimal("142.50"),
        ),
        # Care up to 1291.14 net of the life premiums: 1291.14 x 19% = 245.32.
        (
            _of(life_insurance=530, long_term_care_insurance=2000),
            _INCOME,
            Decimal("245.32"),
        ),
        # Above 120,000 the premiums take (240,000 - 180,000) / 120,000.
        (_of(life_insurance=530), Decimal(180000), Decimal("50.35")),
        (_of(life_insurance=530), Decimal(240000), Decimal("0.00")),
        # The medical expenses are never reduced.
        (_of(health=1000), Decimal(250000), Decimal("165.47")),
    ],
)
def test_the_deduction_of_each_charge(
    expenses: tuple[Art15Expense, ...], income: Decimal, deduction: Decimal
) -> None:
    """Franchise, caps and the income share of c. 3-bis."""
    assert art15_deduction(expenses, income) == deduction


def test_a_negative_charge_is_rejected() -> None:
    """An amount withheld is non-negative."""
    with pytest.raises(InvalidInputError) as error:
        Art15Expense(Art15Kind.HEALTH, Decimal(-1))
    assert error.value.field == "Art15Expense.amount"
