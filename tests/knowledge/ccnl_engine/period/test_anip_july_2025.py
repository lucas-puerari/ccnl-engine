"""Signed ANIP fifth tranche, CNEL 139292 p. 34, ordinary August 2025."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl


@pytest.mark.parametrize(
    ("level", "minimum", "contingenza", "gross"),
    [
        ("2", "779.21", "513.96", "1303.50"),
        ("7", "1436.88", "532.06", "1979.27"),
    ],
)
def test_anip_signed_august_month(
    level: str, minimum: str, contingenza: str, gross: str
) -> None:
    """Level 2: 779.21 + 513.96 + 10.33 = 1303.50.

    Level 7: 1436.88 + 532.06 + 10.33 = 1979.27. No 2025 tax
    tables are bundled, so this checks the contractual ordinary monthly pay.
    """
    day = date(2025, 8, 1)
    contract = load_ccnl("multiservizi-anip")
    record = next(item for item in contract.levels if item.code == level)
    allowances = {
        item.code: item.monthly.value_at(day) for item in record.fixed_allowances
    }
    assert record.base_salary.value_at(day) == Decimal(minimum)
    assert allowances["CONTINGENZA"] == Decimal(contingenza)
    assert allowances["EDR"] == Decimal("10.33")
    assert record.base_salary.value_at(day) + sum(allowances.values()) == Decimal(gross)
