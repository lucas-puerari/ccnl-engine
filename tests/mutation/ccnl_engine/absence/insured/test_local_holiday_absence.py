"""Hand-computed March 2026 local-holiday targets during insured absences."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.paternity.rules import paternity_pay
from ccnl_engine.absence.insured.rules import MonthPay, injury_pay, maternity_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.sickness.holiday.rules import covered_target_holidays
from ccnl_engine.sickness.term.rules import DailyQuota

_FIRST = date(2026, 3, 1)
_LAST = date(2026, 3, 31)
_LOCAL = date(2026, 3, 19)
_PAY = MonthPay(
    MonthlyPayChain(Decimal(3000), Decimal(0), ()),
    DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
    0,
    Decimal(0),
)


@pytest.mark.parametrize(
    "name",
    [
        "ced-assoced",
        "istituzioni-servizi-socio-assistenziali-anaste",
        "studi-professionali-confprofessioni",
    ],
)
def test_maternity_march_patron_top_up(name: str) -> None:
    """March: 31 INPS days x 80 = 2480; 19 March adds 100 - 80 = 20.

    No local date gives zero holiday top-up; an unstated date is never guessed.
    """
    rules = load_ccnl(name).work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.holiday is not None
    for local, expected in ((None, Decimal(0)), ("03-19", Decimal(20))):
        holidays = maternity.holiday.holidays(_FIRST, _LAST, local)
        result = maternity_pay(
            _FIRST,
            _LAST,
            _FIRST,
            _PAY,
            load_insured_absence_rates().maternity,
            maternity,
            Decimal(100),
            holidays,
        )
        assert (result.indemnity, result.integration) == (Decimal(2480), expected)


def test_paternity_march_patron_top_up() -> None:
    """19 March leave: 3000/26 = 115.38, minus INPS 100 = 15.38.

    The same March leave without a stated local date adds zero.
    """
    rules = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.paternity_holiday is not None
    pay = MonthPay(
        _PAY.chain,
        DailyQuota(DailyDivisorMethod.BY_26, Decimal(26)),
        0,
        Decimal(0),
    )
    for local, expected in ((None, Decimal(0)), ("03-19", Decimal("15.38"))):
        holidays = maternity.paternity_holiday.holidays(_FIRST, _LAST, local)
        result = paternity_pay(
            (_LOCAL,),
            pay,
            load_insured_absence_rates().paternity,
            Decimal(100),
            maternity.paternity_holiday,
            holidays,
        )
        assert (result.indemnity, result.integration) == (Decimal(100), expected)


@pytest.mark.parametrize(
    ("name", "ordinary"),
    [
        ("ced-assoced", Decimal("8.93")),
        ("impianti-sportivi-sport", Decimal("23.93")),
        ("studi-professionali-confprofessioni", Decimal("15.00")),
        ("terziario-confesercenti", Decimal("23.93")),
    ],
)
def test_injury_march_patron_reaches_full_daily_pay(
    name: str, ordinary: Decimal
) -> None:
    """19 March: INAIL 60% x (3000/200 x 40/6) = 60.

    Before the local day, the ordinary top-up is 8.93, 23.93 or 15.00;
    on the patron day total employer top-up reaches 100 - 60 = 40.
    """
    rules = load_ccnl(name).work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    injury = rules.insured_absence.injury
    assert injury is not None
    assert injury.holiday is not None
    pay = MonthPay(_PAY.chain, _PAY.quota, 1, Decimal("0.0919"))
    for employer, expected in (
        (None, ordinary),
        (
            EmployerProfile(headcount=Headcount(50), patron_saint_day="03-19"),
            Decimal(40),
        ),
    ):
        holidays = covered_target_holidays(
            injury.holiday, load_national_holidays(), 2026, employer
        )
        result = injury_pay(
            _LOCAL,
            _LOCAL,
            date(2026, 3, 15),
            pay,
            Decimal(200),
            Decimal(40),
            load_insured_absence_rates().injury,
            injury,
            holidays,
        )
        assert (result.indemnity, result.integration) == (Decimal(60), expected)


def test_leap_day_only_occurs_inside_the_leave_interval() -> None:
    """29 February exists in 2024, but neither 2025 nor outside March leave."""
    rules = load_ccnl("ced-assoced").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.holiday is not None
    holiday = maternity.holiday
    leap = date(2024, 2, 29)
    assert holiday.holidays(leap, leap, "02-29") == frozenset({leap})
    assert (
        holiday.holidays(date(2024, 2, 28), date(2024, 2, 28), "02-29") == frozenset()
    )
    assert holiday.holidays(date(2025, 2, 28), date(2025, 3, 1), "02-29") == frozenset()


def test_local_holiday_is_not_added_twice_or_on_sunday() -> None:
    """1 May 2026 is already national: one 20 top-up; 22 March is Sunday: zero."""
    rules = load_ccnl("ced-assoced").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.holiday is not None
    holiday = maternity.holiday
    assert holiday.holidays(date(2026, 5, 1), date(2026, 5, 31), "05-01") == frozenset({
        date(2026, 5, 1)
    })
    sunday = holiday.holidays(_FIRST, _LAST, "03-22")
    assert sunday == frozenset({date(2026, 3, 22)})
    result = maternity_pay(
        _FIRST,
        _LAST,
        _FIRST,
        _PAY,
        load_insured_absence_rates().maternity,
        maternity,
        Decimal(100),
        sunday,
    )
    assert result.integration == Decimal(0)
