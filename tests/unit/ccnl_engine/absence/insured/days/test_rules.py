"""The days an insured absence deducts, and the daily base on the run's pay."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.base.rules import run_daily_base
from ccnl_engine.absence.insured.days.rules import deducted_days
from ccnl_engine.absence.insured.rules import MonthPay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.sickness.term.rules import DailyQuota
from tests.unit.ccnl_engine.builders import _series

_EDR = Allowance(
    code="EDR",
    description="EDR",
    monthly=TimeSeries.model_validate(_series("26.00")),
    provenance=None,
)
_PAY = MonthPay(
    chain=MonthlyPayChain(
        base=Decimal(2600), seniority=Decimal(52), allowances=((_EDR, Decimal(26)),)
    ),
    quota=DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
    extra_months=2,
    employee_rate=Decimal("0.0919"),
)


def test_each_day_takes_a_26th_of_base_seniority_and_allowances() -> None:
    """Monday and Tuesday 2 and 3 March: 2 x (100 + 2 + 1) = 206."""
    assert deducted_days(_PAY, (date(2026, 3, 2), date(2026, 3, 3))) == (
        Decimal(2),
        Decimal(206),
    )


def test_the_daily_base_carries_the_extra_months() -> None:
    """2,678 / 26 plus the rateo of two extra months, 2,678 x 2 / (12 x 26)."""
    monthly = Decimal(2678)

    assert run_daily_base(_PAY, 26) == (monthly / 26 + monthly * 2 / (Decimal(12) * 26))
