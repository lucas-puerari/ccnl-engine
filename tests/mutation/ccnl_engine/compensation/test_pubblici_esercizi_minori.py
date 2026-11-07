"""Pubblici esercizi art. 162: the aziende minori pay a reduced paga base.

"La paga base nazionale delle aziende minori di cui all'art. 162 è
stabilita come segue" (accordo integrativo 26 June 2024, pp. 4-6): level 7
in June 2026, 1,390.20 EUR conglobated, is 2.58 EUR less.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import EmployerProfile, Headcount
from tests.knowledge.ccnl_engine.support import regular_period


def _base(subsector: str | None) -> Decimal:
    result = regular_period(
        ccnl_id="pubblici-esercizi-fipe-angem",
        level_code="7",
        month=6,
        employer=EmployerProfile(headcount=Headcount(5), subsector=subsector),
    )
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


@pytest.mark.parametrize(
    ("subsector", "base"), [(None, "1390.20"), ("aziende_minori", "1387.62")]
)
def test_the_aziende_minori_pay_the_reduced_table(
    subsector: str | None, base: str
) -> None:
    """Without the sub-sector the ordinary table, with it 2.58 EUR less."""
    assert _base(subsector) == Decimal(base)
