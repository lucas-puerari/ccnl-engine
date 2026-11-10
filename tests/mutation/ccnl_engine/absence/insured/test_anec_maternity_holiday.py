"""Hand-computed national holiday supplement in compulsory maternity leave."""

from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.rules import MonthPay, maternity_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.sickness.term.rules import DailyQuota


def test_may_compulsory_maternity_holiday_target() -> None:
    """31 May days at 80 = 2480; 1 May adds 3000/26 - 80 = 35.38.

    Without the target, employer integration is zero; with it, it is 35.38.
    """
    rules = load_ccnl("esercizi-cinematografici-anec").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.holiday is not None
    first, last = date(2026, 5, 1), date(2026, 5, 31)
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
        0,
        Decimal(0),
    )
    holidays = maternity.holiday.holidays(first, last)
    assert date(2026, 5, 1) in holidays
    for target, expected in ((None, Decimal(0)), (maternity, Decimal("35.38"))):
        result = maternity_pay(
            first,
            last,
            first,
            pay,
            load_insured_absence_rates().maternity,
            target,
            Decimal(100),
            holidays,
        )
        assert (result.indemnity, result.integration) == (Decimal(2480), expected)
