"""The stipendio of CCNL ABI from the tables of the renewal of 2023.

Ipotesi di accordo of 23 November 2023, "Tabelle economiche, importi
mensili per 13 mensilità" (FISAC CGIL text, sha256
c6506346fe9e68332ddd33d960f28ec965c42eaeb15170f6da2bd7bcd70f1ddd, pp.
35-38), read on 14 October 2026.  Three levels at each of the four tranches,
the first from 1 July 2023, the day before each later one still paying the
tranche before.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("bancari-abi.json")
_TRANCHES = (date(2023, 7, 1), date(2024, 9, 1), date(2025, 6, 1), date(2026, 3, 1))
_TABLE = (
    ("QD4", ("4911.48", "5045.85", "5113.03", "5160.06")),
    ("3A4", ("3156.90", "3256.90", "3306.90", "3341.90")),
    ("1e2A", ("2350.10", "2420.02", "2454.98", "2479.45")),
)


@pytest.mark.parametrize(("level", "amounts"), _TABLE)
def test_each_tranche_of_the_tables(level: str, amounts: tuple[str, ...]) -> None:
    """The printed stipendio from each tranche."""
    salary = _CCNL.level_by_code(level).base_salary
    values = [Decimal(a) for a in amounts]

    for start, value in zip(_TRANCHES, values, strict=True):
        assert salary.value_at(start) == value
    for start, previous in zip(_TRANCHES[1:], values, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous


def test_thirteen_monthly_payments() -> None:
    """'Importi mensili per 13 mensilità'."""
    months = _CCNL.parameters.additional_months.value_at(date(2026, 3, 1))

    assert months == 13
