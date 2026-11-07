"""The minimi of the operai of CCNL Edilizia ANCE from the national table.

ANCE, "CCNL 21 febbraio 2025 - Nuovi minimi di paga base e di stipendio"
(sha256 d01c1635bf8f5185043f6c5509f0c829fb58bdb1d9ef2943f554d825f60d1710),
read again on 14 October 2026.  The bundle states the monthly minimo of an
operaio as the minimo of the impiegato of the same level, and the operai are
paid by the hour on 1/173 of it (Allegato A of the CCNL of 19 April 2010):
each monthly amount over 173 is the hourly minimo the table prints for the
operai, at each of the three tranches.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("edilizia-ance")
_TRANCHES = (date(2025, 2, 1), date(2026, 3, 1), date(2027, 3, 1))
_DIVISOR = Decimal(173)
#: Level, monthly minimo (impiegati column), hourly minimo (operai column).
_TABLE = (
    ("1", ("1067.36", "1117.36", "1167.36"), ("6.17", "6.46", "6.75")),
    ("2", ("1248.81", "1307.31", "1365.81"), ("7.22", "7.56", "7.89")),
    ("3", ("1387.56", "1452.56", "1517.56"), ("8.02", "8.40", "8.77")),
    ("4", ("1494.31", "1564.31", "1634.31"), ("8.64", "9.04", "9.45")),
)


@pytest.mark.parametrize(("level", "monthly", "hourly"), _TABLE)
def test_each_tranche_of_the_national_table(
    level: str, monthly: tuple[str, ...], hourly: tuple[str, ...]
) -> None:
    """The monthly minimo of each tranche, and its 1/173 the printed hourly."""
    salary = _CCNL.level_by_code(level).base_salary
    amounts = [Decimal(m) for m in monthly]

    for start, amount, hour in zip(_TRANCHES, amounts, hourly, strict=True):
        assert salary.value_at(start) == amount
        assert (amount / _DIVISOR).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ) == Decimal(hour)
    for start, previous in zip(_TRANCHES[1:], amounts, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous
