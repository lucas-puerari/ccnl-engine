"""The minimi of CCNL Metalmeccanico Federmeccanica from the signed renewal.

Ipotesi di accordo of 22 November 2025 (ratified by the referendum of 18-20
February 2026), "Tabelle dei minimi contrattuali", p. 2 of the signed scan
(sha256 37152685c30627ee755fa5593faee689db76fa42a70b87f30661e9561f40f4ec),
read again on 14 October 2026: the minimi of every level from 1 June 2026,
2027 and 2028.  Each tranche starts on 1 June and the day before still pays
the tranche of the year before.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("metalmeccanico-federmeccanica")
#: Level, minimi from 1 June 2026, 2027 and 2028, as printed.
_TABLE = (
    ("D1", "1784.94", "1833.02", "1885.37"),
    ("D2", "1979.37", "2032.70", "2090.76"),
    ("C1", "2022.12", "2076.59", "2135.89"),
    ("C2", "2064.88", "2120.52", "2181.09"),
    ("C3", "2211.43", "2271.01", "2335.88"),
    ("B1", "2370.33", "2434.19", "2503.72"),
    ("B2", "2542.98", "2611.49", "2686.08"),
    ("B3", "2838.99", "2915.48", "2998.76"),
    ("A1", "2907.01", "2985.33", "3070.61"),
)
_TRANCHES = (date(2026, 6, 1), date(2027, 6, 1), date(2028, 6, 1))


@pytest.mark.parametrize(("level", "y2026", "y2027", "y2028"), _TABLE)
def test_each_tranche_starts_on_1_june(
    level: str, y2026: str, y2027: str, y2028: str
) -> None:
    """The signed amount from 1 June, the previous one on 31 May."""
    salary = _CCNL.level_by_code(level).base_salary
    amounts = [Decimal(y2026), Decimal(y2027), Decimal(y2028)]

    for start, amount in zip(_TRANCHES, amounts, strict=True):
        assert salary.value_at(start) == amount
    for before, previous in zip(_TRANCHES[1:], amounts, strict=False):
        assert salary.value_at(before - timedelta(days=1)) == previous


def test_the_table_covers_every_level() -> None:
    """The nine levels of the table are the nine levels of the bundle."""
    assert [level.code for level in _CCNL.levels] == [row[0] for row in _TABLE]
