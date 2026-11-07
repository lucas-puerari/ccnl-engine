"""The Orafi minimums of the renewal signed 10 February 2026 (art. 47, p. 4).

"Tabella minimi contrattuali lordi mensili (in €)": the 2021 tables until
30 September 2026, then 1 October 2026, 1 June 2027 and 1 June 2028.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_ORAFI = load_ccnl("orafi-argentieri-industria-federorafi")


def _minimum(code: str, day: date) -> Decimal | None:
    (level,) = [lv for lv in _ORAFI.levels if lv.code == code]
    return level.base_salary.value_at(day)


@pytest.mark.parametrize(
    ("code", "september", "october", "june_2027", "june_2028"),
    [
        ("2", "1574.39", "1617.24", "1665.23", "1717.48"),
        ("5", "1928.22", "1980.70", "2039.47", "2103.47"),
        ("5S", "2058.07", "2114.08", "2176.81", "2245.12"),
        ("7Q", "2405.58", "2471.05", "2544.37", "2624.22"),
    ],
)
def test_the_minimums_follow_the_2026_table(
    code: str, september: str, october: str, june_2027: str, june_2028: str
) -> None:
    """The 2021 minimum in September 2026, then the three columns."""
    assert [
        _minimum(code, day)
        for day in (
            date(2026, 9, 30),
            date(2026, 10, 1),
            date(2027, 6, 1),
            date(2028, 6, 1),
        )
    ] == [Decimal(september), Decimal(october), Decimal(june_2027), Decimal(june_2028)]
