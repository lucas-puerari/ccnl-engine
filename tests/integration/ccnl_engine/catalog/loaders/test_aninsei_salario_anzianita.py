"""ANINSEI art. 24: the salario di anzianità by hire-date band.

CCNL ANINSEI 2024-2027 (15 June 2024, foe.it copy, sha256
7ded0d5d6b5a3dc5763084517f7fb520e293b4f0a7d9b85be96648d537c35b65), pp. 53-54:
the printed total of each band at 1/09/2022 and at 1/01/2025; the 20 EUR of
2025 only for two years of service at 1/01/2025.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain

_CCNL = load_ccnl("scuole-private-laiche-aninsei")


def _salario(hired_on: date | None, as_of: date) -> Decimal:
    level = _CCNL.level_by_code("IV")
    allowances = tuple(
        (a, a.monthly.value_at(as_of))
        for a in level.fixed_allowances
        if a.code.startswith("SAL_ANZ_")
    )
    chain = MonthlyPayChain(
        base=Decimal(0), seniority=Decimal(0), allowances=allowances
    )
    return chain.for_hire_date(hired_on).allowances_total


@pytest.mark.parametrize(
    ("hired_on", "in_2024", "in_2025"),
    [
        (date(1997, 3, 1), "70.00", "90.00"),
        (date(2001, 12, 31), "70.00", "90.00"),
        (date(2002, 1, 1), "55.00", "75.00"),
        (date(2007, 9, 1), "45.00", "65.00"),
        (date(2010, 9, 1), "35.00", "55.00"),
        (date(2013, 9, 1), "25.00", "45.00"),
        (date(2020, 8, 31), "15.00", "35.00"),
        (date(2020, 9, 1), "0.00", "20.00"),
        (date(2023, 1, 1), "0.00", "20.00"),
        (date(2023, 1, 2), "0.00", "0.00"),
        (None, "0.00", "0.00"),
    ],
)
def test_band_total(hired_on: date | None, in_2024: str, in_2025: str) -> None:
    """Each band receives the printed total; no hire date, no salario."""
    assert _salario(hired_on, date(2024, 9, 1)) == Decimal(in_2024)
    assert _salario(hired_on, date(2025, 1, 1)) == Decimal(in_2025)
