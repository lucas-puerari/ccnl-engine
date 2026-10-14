"""The pay of CCNL Logistica, Trasporto e Spedizione from the testo unico.

Testo unico of the renewal of 6 December 2024 (Confetra, sha256
99d743d0924958c9cea8e80ec97377763090ad2b3b84d1a4bb8aa5900f0d6e24),
"Minimi contrattuali mensili ed EPA", personale non viaggiante, pp. 80-81,
read on 14 October 2026: the base salary of the bundle is the minimo plus
the EPA of each tranche.  Three levels at each tranche change.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("logistica-trasporto-confetra.json")
_TRANCHES = (date(2025, 1, 1), date(2026, 1, 1), date(2027, 1, 1), date(2027, 6, 1))
#: Level, (minimo, EPA) of each tranche, as printed.
_TABLE = (
    (
        "1",
        (
            ("2326.61", "36.67"),
            ("2374.79", "36.67"),
            ("2374.79", "73.34"),
            ("2386.84", "110.00"),
        ),
    ),
    (
        "4",
        (
            ("1786.59", "26.67"),
            ("1823.56", "26.67"),
            ("1823.56", "53.34"),
            ("1832.80", "80.00"),
        ),
    ),
    (
        "6",
        (
            ("1592.38", "23.33"),
            ("1625.41", "23.33"),
            ("1625.41", "46.66"),
            ("1633.67", "70.00"),
        ),
    ),
)


@pytest.mark.parametrize(("level", "rows"), _TABLE)
def test_base_salary_is_minimo_plus_epa(
    level: str, rows: tuple[tuple[str, str], ...]
) -> None:
    """Minimo plus EPA from each tranche, the tranche before the day before."""
    salary = _CCNL.level_by_code(level).base_salary
    totals = [Decimal(m) + Decimal(e) for m, e in rows]

    for start, total in zip(_TRANCHES, totals, strict=True):
        assert salary.value_at(start) == total
    for start, previous in zip(_TRANCHES[1:], totals, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous
