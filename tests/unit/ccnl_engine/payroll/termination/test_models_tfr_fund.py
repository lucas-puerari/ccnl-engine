"""TFR fund at 31 December: validated on construction."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import TfrFundBalance


def test_valid_balance_keeps_its_values() -> None:
    """A balance in cents at 31 December of a year is accepted."""
    balance = TfrFundBalance(2025, Decimal("12345.67"))
    assert (balance.year, balance.amount) == (2025, Decimal("12345.67"))


@pytest.mark.parametrize(
    ("year", "amount", "field"),
    [
        ("2025", Decimal(0), "TfrFundBalance.year"),
        (1899, Decimal(0), "TfrFundBalance.year"),
        (2025, Decimal("-0.01"), "TfrFundBalance.amount"),
        (2025, Decimal("1.005"), "TfrFundBalance.amount"),
        (2025, 100, "TfrFundBalance.amount"),
    ],
)
def test_invalid_balance_is_rejected(year: object, amount: object, field: str) -> None:
    """A non-int or early year, a negative, sub-cent or non-Decimal amount."""
    with pytest.raises(InvalidInputError) as raised:
        TfrFundBalance(year, amount)  # type: ignore[arg-type]
    assert raised.value.field == field
