"""The paga base of the 1-2 star hotels and small campsites (Turismo art. 152 c. 2).

Renewal of 5 July 2024, p. 43: "Per il personale degli alberghi a una e due
stelle e dei campeggi con un numero di presenze - licenza non superiore a
milleduecento, i valori di paga base nazionale conglobata mensile sono i
seguenti"; the sibling ruleset holds them, the parent the general table.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_DAY = date(2026, 6, 1)


@pytest.mark.parametrize(
    ("level", "small", "general"),
    [
        ("A", "2405.46", "2416.82"),
        ("4", "1688.98", "1695.69"),
        ("7", "1407.44", "1412.60"),
    ],
)
def test_the_small_hotels_pay_the_lower_table(
    level: str, small: str, general: str
) -> None:
    """May 2026 column of the two tables of Art. 152."""
    sibling = load_ccnl("turismo-federalberghi-alberghi-minori").level_by_code(level)
    parent = load_ccnl("turismo-federalberghi").level_by_code(level)

    assert sibling.base_salary.value_at(_DAY) == Decimal(small)
    assert parent.base_salary.value_at(_DAY) == Decimal(general)
