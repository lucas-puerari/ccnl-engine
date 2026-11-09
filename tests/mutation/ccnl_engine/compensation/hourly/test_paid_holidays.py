"""Art. 17 holiday quotas of an hourly worker, with Art. 5 and 18 accruals."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    Employment,
    InvalidInputError,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employment.fact.inputs import ContributableHours
from ccnl_engine.inputs import NoPensionFund, Permanent, WorkerCategory
from ccnl_engine.period.facts.holiday import PaidHolidayDays
from ccnl_engine.period.facts.inputs import PeriodFacts
from tests.knowledge.ccnl_engine.irpef.other_income.builders import employment_only
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import EMPLOYER, ENGINE

pytestmark = pytest.mark.legal_scenario


def _run(holidays: int) -> PeriodResult:
    return ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id="edilizia-ance",
                level_code="1",
                category=WorkerCategory.OPERAIO,
                seniority=new_hire(),
                pension_fund=NoPensionFund(),
                contract_type=Permanent(),
            ),
            employer=EMPLOYER,
            facts=PeriodFacts(
                ordinary_hours_worked=ContributableHours(Decimal(160)),
                paid_holiday_days=PaidHolidayDays(holidays),
            ),
            opening_state=PeriodState.zero(),
            current_year=employment_only(),
        )
    )


def test_one_weekday_holiday_is_paid_in_addition_to_worked_hours() -> None:
    """160 worked + one January holiday x 8 = 168 paid: 1,904.44 gross.

    Base 1,036.51, contingenza 498.05, EDR 10.03; 4.95% of 1,534.56
    is 75.96 and 18.5% is 283.89, with 217.91 remitted net.
    The holiday adds 90.70 gross over 160 worked hours without a holiday.
    """
    result = _run(1)
    assert result.period_gross == Decimal("1904.44")
    assert {
        i.kind: i.amount for i in result.pay_items if i.kind == "base_salary_earning"
    }["base_salary_earning"] == Decimal("1036.51")
    assert sum(
        (i.amount for i in result.pay_items if i.kind == "hourly_percentage_earning"),
        Decimal(0),
    ) == Decimal("359.85")
    assert sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == "bilateral_fund_employee"
        ),
        Decimal(0),
    ) == Decimal("217.91")
    assert any(
        d.inputs.get("paid_holiday_hours") == Decimal(8) for d in result.decisions
    )
    assert sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == "pension_fund_employer"
        ),
        Decimal(0),
    ) == Decimal(11)


def test_month_without_eligible_holidays_pays_worked_hours_only() -> None:
    """160 worked + zero holidays: base 987.15 and gross 1,813.74.

    Base of both percentages: 987.15 + 474.33 = 1,461.48;
    riposi 72.34, Cassa Edile 270.37, net accrual 207.53.
    """
    result = _run(0)
    assert result.period_gross == Decimal("1813.74")
    assert sum(
        (i.amount for i in result.pay_items if i.kind == "hourly_percentage_earning"),
        Decimal(0),
    ) == Decimal("342.71")
    assert sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == "bilateral_fund_employee"
        ),
        Decimal(0),
    ) == Decimal("207.53")
    assert any(
        d.inputs.get("paid_holiday_hours") == Decimal(0) for d in result.decisions
    )
    assert sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == "pension_fund_employer"
        ),
        Decimal(0),
    ) == Decimal(11)


def test_invalid_holiday_count_is_rejected() -> None:
    """A negative count must not create a negative eight-hour quota."""
    with pytest.raises(InvalidInputError):
        PaidHolidayDays(-1)
