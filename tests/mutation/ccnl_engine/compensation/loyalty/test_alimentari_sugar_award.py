"""Bundled sugar award: 1,204.74 + 515.31 + 10.33 + 65.70 = EUR 1,796.08.

The 25-year clerical award is EUR 1,796.08; the manual award is
200 x 1,796.08 / 173 = EUR 2,076.39, rounded to cents. The preceding
month and the other food-industry branches pay EUR 0. This monthly chain
is an approximation of normal pay, not an additional source wage table.
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _run(category: WorkerCategory, subsector: str, month: int) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20), subsector=subsector),
            period_id=PeriodId(2026, month),
            payment_date=date(2026, month, 27),
            ccnl_id="alimentari-federalimentare",
            level_code="6",
            category=category,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            employment_period=EmploymentPeriod(started_on=date(2001, 4, 15)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        (WorkerCategory.IMPIEGATO, Decimal("1796.08")),
        (WorkerCategory.OPERAIO, Decimal("2076.39")),
    ],
)
def test_sugar_award_on_twenty_fifth_anniversary(
    category: WorkerCategory, expected: Decimal
) -> None:
    """At EUR 1,796.08 normal pay, award EUR 1,796.08 or 200/173 times it."""
    april = _run(category, "saccarifero", 4)
    march = _run(category, "saccarifero", 3)
    other = _run(category, "carni", 4)
    assert [
        item.amount for item in april.pay_items if item.kind == "bonus_earning"
    ] == [expected]
    assert not [item for item in march.pay_items if item.kind == "bonus_earning"]
    assert not [item for item in other.pay_items if item.kind == "bonus_earning"]
