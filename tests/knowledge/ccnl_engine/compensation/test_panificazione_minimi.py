"""The base salary of the CCNL Alimentazione-Panificazione artigianato.

Signed CCNL of 6 June 2024 (UILA UIL, sha256
8a29e01b3f000b1d1896f8303c015cdd3301538a99ea30e2397ce56da8b2724e), read on
15 October 2026: the base salary is the retribuzione tabellare of Art. 32
(pp. 45-47) plus the indennità speciale of Art. 33 (p. 48) plus an ERR of
0.44 the text does not state.  Every level at each of the four tranches,
the day before each later one still paying the tranche before.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("panificazione-artigianato-confartigianato.json")
_TRANCHES = (date(2024, 4, 1), date(2025, 1, 1), date(2025, 11, 1), date(2026, 4, 1))
_ERR = Decimal("0.44")
#: Level, indennità speciale (Art. 33) and the tabellare of each tranche.
_TABLE = (
    ("A1S", "94.77", ("1958.87", "2004.81", "2067.98", "2117.37")),
    ("A1", "88.06", ("1821.08", "1863.79", "1922.52", "1968.43")),
    ("A2", "82.63", ("1705.54", "1745.54", "1800.54", "1843.54")),
    ("A3", "75.92", ("1561.73", "1598.36", "1648.72", "1688.09")),
    ("A4", "72.05", ("1479.65", "1514.35", "1562.07", "1599.37")),
    ("B1", "92.19", ("1917.86", "1962.84", "2024.69", "2073.04")),
    ("B2", "76.44", ("1575.60", "1612.55", "1663.36", "1703.08")),
    ("B3S", "74.87", ("1533.41", "1569.37", "1618.82", "1657.48")),
    ("B3", "72.56", ("1483.40", "1518.19", "1566.03", "1603.43")),
    ("B4", "68.69", ("1406.84", "1439.83", "1485.20", "1520.67")),
)


@pytest.mark.parametrize(("level", "special", "tabellari"), _TABLE)
def test_each_tranche_of_art_32(
    level: str, special: str, tabellari: tuple[str, ...]
) -> None:
    """Tabellare, indennità speciale and ERR from each tranche."""
    salary = _CCNL.level_by_code(level).base_salary
    values = [Decimal(t) + Decimal(special) + _ERR for t in tabellari]

    for start, value in zip(_TRANCHES, values, strict=True):
        assert salary.value_at(start) == value
    for start, previous in zip(_TRANCHES[1:], values, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous


def test_thirteen_monthly_payments() -> None:
    """Art. 36: the tredicesima; the ex 14a ceased in August 1995 (Art. 33)."""
    months = _CCNL.parameters.additional_months.value_at(date(2026, 4, 1))

    assert months == 13
