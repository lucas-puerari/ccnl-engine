"""Turismo Confesercenti: the pubblici esercizi and their aziende minori tables.

The ipotesi of 22 July 2024 (printed pp. 39-41) prints the tables of the
sezione pubblici esercizi, stabilimenti balneari, alberghi diurni and of
the aziende minori (arts. 291 and 345): level 7 is 1,390.20 and 1,387.62
EUR from June 2026, against the 1,412.60 of the alberghi from May 2026.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import EmployerProfile, Headcount
from tests.knowledge.ccnl_engine.support import regular_period


@pytest.mark.parametrize(
    ("subsector", "base"),
    [
        (None, "1412.60"),
        ("pubblici_esercizi", "1390.20"),
        ("aziende_minori", "1387.62"),
    ],
)
def test_each_section_pays_its_table(subsector: str | None, base: str) -> None:
    """The employer's sub-sector picks the table of level 7 in June 2026."""
    result = regular_period(
        ccnl_id="turismo-confesercenti",
        level_code="7",
        month=6,
        employer=EmployerProfile(headcount=Headcount(5), subsector=subsector),
    )
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    assert item.amount == Decimal(base)
