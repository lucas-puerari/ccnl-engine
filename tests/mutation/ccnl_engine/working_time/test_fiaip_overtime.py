"""FIAIP art. 109: overtime at 15% on the hourly quota (1/168, art. 161).

Level IV, January 2026, 1,782.68 a month: 10 hours of weekday overtime pay
10 x 1,782.68 / 168 x 1.15 = 122.03.  Art. 106: a flexible week earns 45
minutes up to 44 hours and 70 up to 48.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import Employment
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import NoPensionFund, Permanent
from tests.knowledge.ccnl_engine.irpef.other_income.builders import employment_only
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

_CCNL_ID = "agenti-immobiliari-fiaip"


def test_weekday_overtime_takes_fifteen_percent() -> None:
    """122.03 for ten hours."""
    result = regular_period(
        employment=Employment(
            ccnl_id=_CCNL_ID,
            level_code="IV",
            seniority=new_hire(),
            pension_fund=NoPensionFund(),
            contract_type=Permanent(),
        ),
        current_year=employment_only(),
        events=(OvertimeEvent(date(2026, 1, 15), Decimal(10)),),
    )
    (item,) = [i for i in result.pay_items if i.item_id.endswith("_evt0")]
    assert item.amount == Decimal("122.03")


def test_the_flexible_week_earns_45_or_70_minutes() -> None:
    """44 hours: three quarters of an hour; 48 hours: 70 minutes."""
    work = load_ccnl(_CCNL_ID).work_rules
    assert work is not None
    assert work.leave_rules is not None
    flex = work.leave_rules.flexibility
    assert flex is not None
    assert flex.hours_for(Decimal(44)) == Decimal("0.75")
    assert flex.hours_for(Decimal(48)) == Decimal(70) / 60
