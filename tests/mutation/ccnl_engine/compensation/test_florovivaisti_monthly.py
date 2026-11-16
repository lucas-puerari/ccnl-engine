"""The monthly pay of a floriculture OTI: the hourly minimum times 169.

Art. 50 of the CCNL operai agricoli e florovivaisti: "Quella oraria si
ottiene dividendo la paga mensile per 169"; note 12: the floriculture
salary is the hourly one.  Area2: 8.09 x 169 = 1367.21 in March 2026,
8.50259 x 169 = 1436.94 from June 2026; an agricultural Area2 keeps 1330.25.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _base(month: int, subsector: str | None) -> Decimal | None:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10), subsector=subsector),
            period_id=PeriodId(year=2026, month=month),
            payment_date=date(2026, month, 27),
            ccnl_id="operai-agricoli-florovivaisti",
            level_code="Area2",
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (decision,) = (d for d in result.decisions if d.capability == "base_salary")
    return decision.amount


@pytest.mark.parametrize(
    ("month", "subsector", "base"),
    [
        (3, "florovivaisti", "1367.21"),
        (6, "florovivaisti", "1436.94"),
        (3, None, "1330.25"),
    ],
    ids=["florovivaisti-2025-table", "florovivaisti-2026-table", "agricoli"],
)
def test_the_monthly_pay_by_subsector(
    month: int, subsector: str | None, base: str
) -> None:
    """The floriculture month follows the hourly table, not Tabella n. 1."""
    assert _base(month, subsector) == Decimal(base)
