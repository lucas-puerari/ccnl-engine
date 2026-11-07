"""TFR fund at 31 December and quotas of a year: validated on construction."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import TfrFundBalance, TfrQuotaYtd


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


def test_a_balance_states_its_revaluations_and_advances() -> None:
    """The revaluations it holds and the advances paid out of it."""
    balance = TfrFundBalance(2025, Decimal("100.00"), Decimal("4.50"), Decimal(0))
    assert (balance.revaluations, balance.advances) == (Decimal("4.50"), Decimal(0))


@pytest.mark.parametrize(
    ("revaluations", "advances", "field"),
    [
        (Decimal("100.01"), None, "TfrFundBalance.revaluations"),
        (Decimal("-1.00"), None, "TfrFundBalance.revaluations"),
        (None, Decimal("0.001"), "TfrFundBalance.advances"),
    ],
)
def test_invalid_revaluations_or_advances_are_rejected(
    revaluations: Decimal | None, advances: Decimal | None, field: str
) -> None:
    """Revaluations above the fund, a negative or a sub-cent amount."""
    with pytest.raises(InvalidInputError) as raised:
        TfrFundBalance(2025, Decimal("100.00"), revaluations, advances)
    assert raised.value.field == field


def test_quotas_of_a_year_add_up_signed() -> None:
    """An adjustment run that lowers the TFR base posts a negative quota."""
    quotas = TfrQuotaYtd(2026).plus(Decimal("163.03")).plus(Decimal("-3.03"))
    assert quotas == TfrQuotaYtd(2026, Decimal("160.00"))


@pytest.mark.parametrize(
    ("year", "amount", "field"),
    [
        (1969, Decimal(0), "TfrQuotaYtd.year"),
        (2026, Decimal("1.001"), "TfrQuotaYtd.amount"),
        (2026, 1, "TfrQuotaYtd.amount"),
    ],
)
def test_invalid_quotas_are_rejected(year: object, amount: object, field: str) -> None:
    """An early year, a sub-cent or non-Decimal amount."""
    with pytest.raises(InvalidInputError) as raised:
        TfrQuotaYtd(year, amount)  # type: ignore[arg-type]
    assert raised.value.field == field
