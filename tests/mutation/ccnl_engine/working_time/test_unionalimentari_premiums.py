"""Hand oracle: Unionalimentari art. 29 premiums by sub-sector, March 2026.

The premiums are paid on the minimo, contingenza and scatti over 173 (text
signed 18 March 2026, PDF p. 109-119):

- carni, operaio level 5, 10 overtime hours at 45%:
  (1566.14 + 521.59) / 173 x 10 x 1.45 -> 174.98;
- vini-liquori, impiegato level 3, 8 hours on a holiday at 65%:
  (1987.81 + 529.58) / 173 x 8 x 0.65 -> 75.67;
- panificazione, level 3B, 8 Sunday hours: 90% for the bread staff,
  (1476.40 + 522.81) / 173 x 8 x 0.90 -> 83.20, else 65% -> 60.09.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.event.facade import (
    HolidayWorkEvent,
    HolidayWorkKind,
    OvertimeEvent,
    WorkEvent,
)
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_OVERTIME = OvertimeEvent(date(2026, 3, 10), hours=Decimal(10))
_HOLIDAY = HolidayWorkEvent(
    date(2026, 3, 19), hours=Decimal(8), kind=HolidayWorkKind.HOLIDAY
)
_SUNDAY = HolidayWorkEvent(
    date(2026, 3, 15), hours=Decimal(8), kind=HolidayWorkKind.SUNDAY
)


def _event_pay(
    level: str,
    subsector: str,
    category: WorkerCategory,
    event: WorkEvent,
    roles: frozenset[str],
) -> Decimal:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(20),
                subsector=subsector,
                second_level_premium=False,
            ),
            period_id=PeriodId(2026, 3),
            payment_date=date(2026, 3, 27),
            ccnl_id="alimentari-pmi-unionalimentari",
            level_code=level,
            category=category,
            opening_state=PeriodState.zero(),
            roles=roles,
            events=(event,),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (amount,) = (i.amount for i in result.pay_items if i.item_id.endswith("_evt0"))
    return amount


@pytest.mark.parametrize(
    ("level", "subsector", "category", "event", "roles", "amount"),
    [
        ("5", "carni", WorkerCategory.OPERAIO, _OVERTIME, frozenset(), "174.98"),
        (
            "3",
            "vini_liquori",
            WorkerCategory.IMPIEGATO,
            _HOLIDAY,
            frozenset(),
            "75.67",
        ),
        (
            "P3B",
            "panificazione_industriale",
            WorkerCategory.OPERAIO,
            _SUNDAY,
            frozenset({"addetto_pane"}),
            "83.20",
        ),
        (
            "P3B",
            "panificazione_industriale",
            WorkerCategory.OPERAIO,
            _SUNDAY,
            frozenset(),
            "60.09",
        ),
    ],
    ids=["carni-overtime", "vini-holiday", "bread-sunday", "bakery-sunday"],
)
def test_the_sub_sector_table_pays_the_premium(
    level: str,
    subsector: str,
    category: WorkerCategory,
    event: WorkEvent,
    roles: frozenset[str],
    amount: str,
) -> None:
    """The row of the employer's table, on the art. 29 hourly base."""
    assert _event_pay(level, subsector, category, event, roles) == Decimal(amount)
