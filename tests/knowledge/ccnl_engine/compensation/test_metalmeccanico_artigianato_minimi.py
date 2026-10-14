"""The tabellare of CCNL Area Meccanica artigianato from the signed renewal.

Accordo di rinnovo of 19 November 2024 and verbale integrativo of 25
November 2024, signed scan (sha256
6f8424cb05c74d81e1a9e58f2b6c972f6f3d61a9639ded36b4c316e13a4e00e1), p. 27,
Settore Metalmeccanica ed Installazione di Impianti, read on 14 October
2026.  Each tranche is the tabellare before it plus the printed increase,
and three levels are pinned at each tranche change; the 4th level takes the
120 euro of the renewal.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("metalmeccanico-artigianato.json")
_TRANCHES = (date(2024, 12, 1), date(2025, 7, 1), date(2026, 3, 1), date(2026, 11, 1))
#: Level, tabellare until 30 November 2024, increases of the four tranches.
_TABLE = (
    ("1", "1955.32", ("62.79", "31.40", "31.40", "25.12")),
    ("4", "1556.98", ("50.00", "25.00", "25.00", "20.00")),
    ("6", "1430.00", ("45.92", "22.96", "22.96", "18.37")),
)


@pytest.mark.parametrize(("level", "before", "increases"), _TABLE)
def test_each_tranche_adds_the_printed_increase(
    level: str, before: str, increases: tuple[str, ...]
) -> None:
    """Tabellare of 30 November 2024 plus each increase, from its tranche."""
    salary = _CCNL.level_by_code(level).base_salary
    amount = Decimal(before)

    assert salary.value_at(_TRANCHES[0] - timedelta(days=1)) == amount
    for start, increase in zip(_TRANCHES, increases, strict=True):
        amount += Decimal(increase)
        assert salary.value_at(start) == amount
