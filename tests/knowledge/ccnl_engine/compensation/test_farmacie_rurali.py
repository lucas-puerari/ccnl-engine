"""The Farmacie rurali sussidiate: Tabella B of the CCNL of 7 September 2021.

PDF p. 67 (sha256
b6798989a01293d9629dc61f8cb56faeb07f4f5eb4d447526b911c761ac40214): the paga
base from 1 November 2021 is lower than in Tabella A; contingenza, EDR and
ISQ are the same.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_DAY = date(2026, 3, 1)
_RURAL = load_ccnl("farmacie-rurali-sussidiate-h121")
_URBAN = load_ccnl("farmacie-private-h121")


@pytest.mark.parametrize(
    ("level", "rural", "urban"),
    [
        ("Q1", "1602.21", "1668.97"),
        ("1", "1372.02", "1429.19"),
        ("6", "775.49", "807.81"),
    ],
)
def test_the_rural_paga_base_of_tabella_b(level: str, rural: str, urban: str) -> None:
    """Tabella B for the rural subsidised pharmacies, Tabella A for the others."""
    assert _RURAL.level_by_code(level).base_salary.value_at(_DAY) == Decimal(rural)
    assert _URBAN.level_by_code(level).base_salary.value_at(_DAY) == Decimal(urban)


def test_the_allowances_are_those_of_tabella_a() -> None:
    """Contingenza, EDR and ISQ do not change with the table."""
    for rural, urban in zip(_RURAL.levels, _URBAN.levels, strict=True):
        assert [(a.code, a.monthly.value_at(_DAY)) for a in rural.fixed_allowances] == [
            (a.code, a.monthly.value_at(_DAY)) for a in urban.fixed_allowances
        ]
