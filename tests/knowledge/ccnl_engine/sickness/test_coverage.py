"""INPS sickness cover of the bundled rates by CCNL, sector and category.

INPS, Indennità di malattia per lavoratori dipendenti (updated 21.9.2026):
the indemnity "spetta [...] a: [...] lavoratori dell'agricoltura" and "Non
spetta a (elenco non esaustivo): [...] portieri".
"""

from __future__ import annotations

import pytest

from ccnl_engine.sickness.indemnity.loaders import load_sick_pay_rates


@pytest.mark.parametrize(
    ("sector", "category", "ccnl", "covered"),
    [
        ("terziario", "operaio", "portieri-fabbricati-confedilizia", False),
        ("terziario", "operaio", "commercio-confcommercio", True),
        ("agricoltura", "operaio", "operai-agricoli-florovivaisti", True),
    ],
)
def test_cover(sector: str, category: str, ccnl: str, covered: bool) -> None:
    """Portieri are out, agricultural operai in."""
    assert load_sick_pay_rates().covers(sector, category, "permanent", ccnl) is covered
