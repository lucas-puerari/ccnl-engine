"""Tessile PMI art. 46: the calzature employers pay their own table.

"SETTORE CALZATURE [...] Minimi dal 01/01/2026 [...] 8 [...] 2507,94"
against the tessile 2.497,90 (renewal 2024-2027, p. 21).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import EmployerProfile, Headcount
from tests.knowledge.ccnl_engine.support import regular_period


@pytest.mark.parametrize(
    ("subsector", "base"), [(None, "2497.90"), ("calzature", "2507.94")]
)
def test_the_calzature_table_of_level_8(subsector: str | None, base: str) -> None:
    """June 2026, level 8: the tessile table, or the calzature one."""
    result = regular_period(
        ccnl_id="tessile-pmi-uniontessile",
        level_code="8",
        month=6,
        employer=EmployerProfile(headcount=Headcount(20), subsector=subsector),
    )
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    assert item.amount == Decimal(base)
