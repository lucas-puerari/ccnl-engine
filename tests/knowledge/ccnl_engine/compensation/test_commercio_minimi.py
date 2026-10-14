"""The pay of CCNL Terziario Confcommercio from the signed renewal of 2024.

Ipotesi di accordo of 22 March 2024 with the accordo integrativo of 28
March 2024, signed scan (sha256
980356a766c5fad7450dd234052a9f311a2b66d732cb72b6632b354ffaf18001), tables of
pp. 64-65, read again on 14 October 2026: paga base, "Altri el."
and "Contingenza + EDR" of every tranche.  Three levels are pinned at each
tranche change, the day before still paying the tranche before; the
contingenza and the terzo elemento of Art. 215 (2.07) do not move.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("commercio-confcommercio.json")
_TRANCHES = (
    date(2024, 4, 1),
    date(2025, 3, 1),
    date(2025, 11, 1),
    date(2026, 11, 1),
    date(2027, 2, 1),
)
#: Level, paga base of each tranche, contingenza + EDR, as printed.
_TABLE = (
    ("Q", ("2070.25", "2122.33", "2183.09", "2243.85", "2313.29"), "540.37"),
    ("4", ("1192.46", "1222.46", "1257.46", "1292.46", "1332.46"), "524.22"),
    ("7", ("828.08", "848.91", "873.22", "897.53", "925.31"), "517.51"),
)


def _allowance(level: str, code: str, day: date) -> Decimal:
    (allowance,) = [
        a for a in _CCNL.level_by_code(level).fixed_allowances if a.code == code
    ]
    return allowance.monthly.value_at(day)


@pytest.mark.parametrize(("level", "bases", "contingenza"), _TABLE)
def test_each_tranche_of_the_signed_table(
    level: str, bases: tuple[str, ...], contingenza: str
) -> None:
    """Paga base from each tranche, the previous one the day before."""
    salary = _CCNL.level_by_code(level).base_salary
    amounts = [Decimal(b) for b in bases]

    for start, amount in zip(_TRANCHES, amounts, strict=True):
        assert salary.value_at(start) == amount
        assert _allowance(level, "CONTINGENZA_EDR", start) == Decimal(contingenza)
        assert _allowance(level, "TERZO_ELEMENTO_NAZIONALE", start) == Decimal("2.07")
    for start, previous in zip(_TRANCHES[1:], amounts, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous


def test_the_other_elements_of_quadro_and_level_seven() -> None:
    """The "Altri el." column: 260.76 for the quadro, 5.16 for level VII."""
    day = _TRANCHES[-1]

    assert _allowance("Q", "IND_FUNZIONE", day) == Decimal("260.76")
    assert _allowance("7", "ALTRI_ELEMENTI", day) == Decimal("5.16")
