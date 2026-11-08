"""National holidays inside a compulsory maternity leave."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.models import MaternityHoliday
from ccnl_engine.absence.insured.paternity.rules import paternity_pay
from ccnl_engine.absence.insured.rules import InsuredPay, MonthPay, maternity_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.sickness.term.rules import DailyQuota


def _pay(ccnl_id: str, year: int = 2026) -> InsuredPay:
    rules = load_ccnl(ccnl_id).work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    first, last = date(year, 5, 1), date(year, 5, 31)
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
        0,
        Decimal(0),
    )
    return maternity_pay(
        first,
        last,
        first,
        pay,
        load_insured_absence_rates().maternity,
        maternity,
        Decimal(100),
        load_national_holidays().between(first, last),
    )


@pytest.mark.parametrize(
    "ccnl_id",
    [
        "studi-professionali-confprofessioni",
        "ced-assoced",
        "istituzioni-servizi-socio-assistenziali-anaste",
    ],
)
def test_may_day_reaches_daily_pay(ccnl_id: str) -> None:
    """May: daily 3000/30 = 100, minus INPS 80 = 20 extra."""
    result = _pay(ccnl_id)
    assert result.indemnity == Decimal(2480)
    assert result.integration == Decimal("20.00")


def test_sunday_is_not_paid_twice() -> None:
    """1 May 2022 was Sunday: 31 x 80 = 2480, no extra 20."""
    assert _pay("ced-assoced", 2022).integration == Decimal(0)


def test_existing_integration_is_credited_before_holiday_top_up() -> None:
    """520 monthly top-up: 100 - 80 - 520/31 = 3.23 extra."""
    rules = load_ccnl("chimica-farmaceutica-federchimica").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    source = load_ccnl("ced-assoced").work_rules
    assert source is not None
    assert source.insured_absence is not None
    assert source.insured_absence.maternity is not None
    holiday = source.insured_absence.maternity.holiday
    assert isinstance(holiday, MaternityHoliday)
    first, last = date(2026, 5, 1), date(2026, 5, 31)
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
        0,
        Decimal(0),
    )
    result = maternity_pay(
        first,
        last,
        first,
        pay,
        load_insured_absence_rates().maternity,
        maternity.model_copy(update={"holiday": holiday}),
        Decimal(100),
        load_national_holidays().between(first, last),
    )
    assert result.integration == Decimal("523.23")


def test_studi_paternity_holiday_offsets_the_full_inps_share() -> None:
    """1 May: 3000/26 = 115.38, minus INPS 3000/30 = 100: 15.38."""
    rules = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
        0,
        Decimal(0),
    )
    may_day = date(2026, 5, 1)
    monday = date(2026, 5, 4)
    result = paternity_pay(
        (may_day, monday),
        pay,
        load_insured_absence_rates().paternity,
        Decimal(100),
        maternity.paternity_holiday,
        load_national_holidays().between(may_day, monday),
    )
    assert result.indemnity == Decimal(200)
    assert result.integration == Decimal("15.38")


def test_no_paternity_top_up_outside_the_leave_days() -> None:
    """1 May not taken as leave: 100 INPS on 4 May, no holiday increment."""
    rules = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    pay = MonthPay(
        MonthlyPayChain(Decimal(3000), Decimal(0), ()),
        DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
        0,
        Decimal(0),
    )
    result = paternity_pay(
        (date(2026, 5, 4),),
        pay,
        load_insured_absence_rates().paternity,
        Decimal(100),
        maternity.paternity_holiday,
        load_national_holidays().between(date(2026, 5, 1), date(2026, 5, 4)),
    )
    assert result.integration == Decimal(0)


def _ced_holiday() -> MaternityHoliday:
    rules = load_ccnl("ced-assoced").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    assert rules.insured_absence.maternity is not None
    holiday = rules.insured_absence.maternity.holiday
    assert holiday is not None
    return holiday


def test_the_holidays_of_the_clause_leave_out_the_excluded_codes() -> None:
    """4 October 2027 is a Monday: in the calendar, not in CED (10-04 excluded)."""
    ced = _ced_holiday()
    every = ced.model_copy(update={"excluded_days": ()})
    october = (date(2027, 10, 1), date(2027, 10, 31))
    assert every.holidays(*october) == frozenset({date(2027, 10, 4)})
    assert ced.holidays(*october) == frozenset()
