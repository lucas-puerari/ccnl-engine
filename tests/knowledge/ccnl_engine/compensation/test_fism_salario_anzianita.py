"""FISM art. 46: the salario di anzianità from 1 September 2025.

15 EUR a month (levels I-IV) or 20 EUR (levels V-VIII) on 13 payments to
the staff with two years of uninterrupted service with the Ente on 1
September 2025, that is in service since 1 September 2023 at the latest.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period


def _salario(
    level: str, hired: date, year: int = 2026, month: int = 1
) -> list[Decimal]:
    employment = Employment(
        ccnl_id="scuole-materne-fism",
        level_code=level,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(hired),
    )
    result = regular_period(ccnl_id="scuole-materne-fism", employment=employment)
    return [i.amount for i in result.pay_items if "SALARIO_ANZIANITA" in i.item_id]


@pytest.mark.parametrize(
    ("level", "hired", "expected"),
    [
        ("III", date(2020, 1, 1), [Decimal("15.00")]),
        ("VI", date(2023, 9, 1), [Decimal("20.00")]),
        ("VI", date(2023, 9, 2), []),
    ],
    ids=["level-iii", "two-years-exactly", "short-of-two-years"],
)
def test_the_salario_di_anzianita_by_level_and_service(
    level: str, hired: date, expected: list[Decimal]
) -> None:
    """Two years of service on 1 September 2025, by the level."""
    assert _salario(level, hired) == expected
