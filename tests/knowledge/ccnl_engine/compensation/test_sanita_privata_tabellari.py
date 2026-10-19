"""The tabellari of CCNL Sanità privata AIOP-ARIS from the 2020 text.

CCNL of 8 October 2020, Tabella 1 "Prospetto valori tabellari", decorrenza
1° luglio 2020, p. 104 (sha256
183c5c0a01c9a113fd08efffed8132b4e598e4db574f6aed402afb7be880a442), read on
14 October 2026.  Column D, "Nuovi tabellari mensili", is column C, the
annual tabellare "x 13 mensilità", over 13; no later renewal is in force,
so the same amounts are paid in 2026.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("sanita-privata-aiop-aris")
#: Position, annual tabellare (column C), monthly tabellare (column D).
_TABLE = (
    ("A", "19076.87", "1467.45"),
    ("C", "23446.87", "1803.61"),
    ("D", "25400.25", "1953.87"),
    ("DS", "27314.09", "2101.08"),
    ("E2", "46207.05", "3554.39"),
)


@pytest.mark.parametrize(("position", "annual", "monthly"), _TABLE)
def test_monthly_tabellare_from_july_2020_still_in_2026(
    position: str, annual: str, monthly: str
) -> None:
    """Column D, the annual amount over 13, from 1 July 2020 into 2026."""
    salary = _CCNL.level_by_code(position).base_salary

    assert (Decimal(annual) / 13).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) == Decimal(monthly)
    assert salary.value_at(date(2020, 7, 1)) == Decimal(monthly)
    assert salary.value_at(date(2026, 10, 1)) == Decimal(monthly)


def test_thirteen_monthly_payments() -> None:
    """'Nuovi tabellari annui (x 13 mensilità)'."""
    assert _CCNL.parameters.additional_months.value_at(date(2026, 1, 1)) == 13
