"""March 2026 maternity holiday treatment for metal agreements."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.rules import MonthPay, maternity_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.sickness.term.rules import DailyQuota


@pytest.mark.parametrize("name", ["metalmeccanico-confapi"])
def test_march_patron_holiday_requires_target_and_local_date(name: str) -> None:
    """31 INPS days x 80 = 2480; ordinary integration = 3000 - 2480 = 520.

    March 19's full daily pay is 3000/30 = 100 (30-day quota); INPS pays 80
    and the month's ordinary integration is (3000 - 31 x 80)/31 = 16.77 a
    day, so the added holiday portion is 100 - 80 - 16.77 = 3.23.
    Without the holiday target or local date integration stays 520.00.
    """
    rules = load_ccnl(name).work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.holiday is not None
    first, last = date(2026, 3, 1), date(2026, 3, 31)
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
        0,
        Decimal(0),
    )
    assert maternity.holiday.includes_patron_saint
    for local in (None, "03-19"):
        holidays = maternity.holiday.holidays(first, last, local)
        result = maternity_pay(
            first,
            last,
            first,
            pay,
            load_insured_absence_rates().maternity,
            maternity,
            Decimal(100),
            holidays,
        )
        without = maternity_pay(
            first,
            last,
            first,
            pay,
            load_insured_absence_rates().maternity,
            maternity.model_copy(update={"holiday": None}),
            Decimal(100),
            frozenset(),
        )
        assert result.indemnity == without.indemnity == Decimal(2480)
        assert result.integration - without.integration == (
            Decimal("3.23") if local else Decimal(0)
        )
