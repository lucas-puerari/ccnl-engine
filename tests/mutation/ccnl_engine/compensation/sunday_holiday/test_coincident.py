"""National holidays on Saturday and Sunday under a coincident-holiday clause."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.rest_day.inputs import Weekday
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


@pytest.mark.parametrize(
    ("agreement", "level", "monthly", "rest", "days", "quota"),
    [
        (
            "logistica-trasporto-confetra",
            "6",
            Decimal("1703.67"),
            Weekday.SUNDAY,
            "2027-12-25,2027-12-26",
            Decimal("154.88"),
        ),
        (
            "logistica-trasporto-confetra-viaggiante",
            "C3",
            Decimal("2131.65"),
            Weekday.SUNDAY,
            "2027-12-25,2027-12-26",
            Decimal("193.79"),
        ),
        (
            "logistica-trasporto-confetra",
            "6",
            Decimal("1703.67"),
            Weekday.SATURDAY,
            "2027-12-26",
            Decimal("77.44"),
        ),
    ],
)
def test_coincident_days_not_weekday(
    agreement: str,
    level: str,
    monthly: Decimal,
    rest: Weekday,
    days: str,
    quota: Decimal,
) -> None:
    """December 2027: 25 Sat and 26 Sun add 2 * monthly/22; 8 Wed adds zero.

    Level 6: 2 * 1703.67 / 22 = 154.88, rather than zero; C3:
    2 * 2131.65 / 22 = 193.79. Saturday compensatory rest instead pays
    1703.67 / 22 = 77.44. The 2021 EDR has no incidence on the quota.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20)),
            period_id=PeriodId(2027, 12),
            payment_date=date(2027, 12, 27),
            ccnl_id=agreement,
            level_code=level,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            weekly_rest_day=rest,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    decisions = [d for d in result.decisions if d.capability == "sunday_holiday"]
    assert len(decisions) == 1
    assert decisions[0].amount == quota
    assert decisions[0].inputs["days"] == days
    assert decisions[0].inputs["monthly"] == monthly
    assert (
        sum(
            (
                i.amount
                for i in result.pay_items
                if i.item_id.startswith("sunday_holiday")
            ),
            Decimal(0),
        )
        == quota
    )
