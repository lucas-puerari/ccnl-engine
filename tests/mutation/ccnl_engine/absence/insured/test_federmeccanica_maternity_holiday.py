"""Federmeccanica art. 9: the holidays of letters b and c in the maternity leave."""

from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.maternity_holiday import MaternityHoliday
from ccnl_engine.catalog.loaders import load_ccnl


def _holiday() -> MaternityHoliday:
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    maternity = rules.insured_absence.maternity
    assert maternity is not None
    assert maternity.holiday is not None
    return maternity.holiday


def test_letters_b_and_c_reach_the_whole_pay() -> None:
    """The same target as in a sickness: 100%, with the stated patron day."""
    holiday = _holiday()

    assert (holiday.rate, holiday.includes_patron_saint) == (Decimal(1), True)


def test_letter_a_and_4_october_are_left_out() -> None:
    """April to October 2026: Easter Monday, 15 August and Rome's 29 June."""
    days = _holiday().holidays(date(2026, 4, 1), date(2026, 10, 31), "06-29")

    assert sorted(days) == [
        date(2026, 4, 6),
        date(2026, 6, 29),
        date(2026, 8, 15),
    ]


def test_without_a_stated_patron_day_only_the_national_ones() -> None:
    """The local day or its substitute is the employer's fact."""
    days = _holiday().holidays(date(2026, 6, 1), date(2026, 6, 30))

    assert days == frozenset()
