"""The days an insured absence deducts, and the daily base on the run's pay."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.base.rules import run_daily_base
from ccnl_engine.absence.insured.days.rules import deducted_days
from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.rules import MonthPay, injury_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.catalog.loaders import load_ccnl
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


def test_no_day_deducts_a_decimal_zero() -> None:
    """No day: zero units, a Decimal and not the int of an empty sum."""
    units, pay = deducted_days(_PAY, ())

    assert (units, pay) == (Decimal(0), Decimal(0))
    assert isinstance(units, Decimal)


def test_the_daily_base_carries_the_extra_months() -> None:
    """2,678 / 26 plus the rateo of two extra months, 2,678 x 2 / (12 x 26)."""
    monthly = Decimal(2678)

    assert run_daily_base(_PAY, 26) == (monthly / 26 + monthly * 2 / (Decimal(12) * 26))


def test_a_partial_month_takes_the_quota_of_every_component() -> None:
    """2 and 3 March at a 26th: (100 + 2 + 1) x 2 = 206."""
    assert _PAY.deducted(date(2026, 3, 2), date(2026, 3, 3)) == (
        Decimal(2),
        Decimal(206),
    )


def test_an_hourly_quota_counts_the_hours_of_each_day() -> None:
    """Two days of 8 hours of 168: 2,600, 52 and 26 x 16 / 168, each rounded."""
    hourly = MonthPay(
        chain=_PAY.chain,
        quota=DailyQuota(DailyDivisorMethod.BY_HOURLY, Decimal(168), Decimal(8)),
        extra_months=2,
        employee_rate=Decimal("0.0919"),
    )

    assert hourly.deducted(date(2026, 3, 2), date(2026, 3, 3)) == (
        Decimal(16),
        Decimal("247.62") + Decimal("4.95") + Decimal("2.48"),
    )


_THREE_THOUSAND = MonthPay(
    chain=MonthlyPayChain(base=Decimal(3000), seniority=Decimal(0), allowances=()),
    quota=DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
    extra_months=1,
    employee_rate=Decimal("0.0919"),
)


def test_an_injury_with_a_ccnl_carenza_and_top_up() -> None:
    """Injured Monday 2 March, unable to 13 March, 3,000 a month in 30ths.

    The 11 days after the injury day are deducted, 1,100.00; the carenza of
    3 days, 300.00, at the CCNL 100% (the statutory 60% gives 180.00); INAIL
    pays 60% of 3,000 / 173 x 40 / 6 on 8 days, 554.91; the CCNL tops the
    INAIL share up to the whole pay of those days: 1,100 - 300 - 554.91.
    """
    work = load_ccnl("chimica-farmaceutica-federchimica").work_rules
    assert work is not None
    assert work.insured_absence is not None
    clause = work.insured_absence.injury
    assert clause is not None
    rules = clause.model_copy(
        update={
            "carenza_rate": Decimal(1),
            "integration_rate": Decimal(1),
            "net_basis": False,
        }
    )
    paid = injury_pay(
        date(2026, 3, 2),
        date(2026, 3, 13),
        date(2026, 3, 2),
        _THREE_THOUSAND,
        Decimal(173),
        Decimal(40),
        load_insured_absence_rates().injury,
        rules,
    )

    assert (paid.deduction, paid.carenza, paid.indemnity, paid.integration) == (
        Decimal("1100.00"),
        Decimal("300.00"),
        Decimal("554.91"),
        Decimal("245.09"),
    )
