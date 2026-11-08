"""The holiday target on a work injury nets amounts already paid that day."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.models import InjuryIntegrationBand
from ccnl_engine.absence.insured.rules import InsuredPay, MonthPay, injury_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.sickness.holiday.rules import covered_target_holidays
from ccnl_engine.sickness.term.rules import DailyQuota

_PAY = MonthPay(
    chain=MonthlyPayChain(base=Decimal(3000), seniority=Decimal(0), allowances=()),
    quota=DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
    extra_months=1,
    employee_rate=Decimal("0.0919"),
)


def _paid(name: str, first: date, last: date, injury_on: date) -> InsuredPay:
    contract = load_ccnl(name)
    assert contract.work_rules is not None
    assert contract.work_rules.insured_absence is not None
    rules = contract.work_rules.insured_absence.injury
    assert rules is not None
    holidays = covered_target_holidays(
        rules.holiday, load_national_holidays(), first.year
    )
    return injury_pay(
        first,
        last,
        injury_on,
        _PAY,
        Decimal(200),
        Decimal(40),
        load_insured_absence_rates().injury,
        rules,
        holidays,
    )


@pytest.mark.parametrize(
    "name",
    [
        "terziario-confesercenti",
        "ced-assoced",
        "impianti-sportivi-sport",
        "esercizi-cinematografici-anec",
    ],
)
def test_holiday_only_clause_nets_waiting_pay_and_inail(name: str) -> None:
    """Jan 1 waiting pays 60; Jan 6 INAIL pays 60.

    Injured Dec 29: Jan 1 adds 40; Jan 6 INAIL pays
    60% of (3000/200*40/6) = 60, extra 40. Total extra 80.00, on top
    of the INAIL share of Jan 2-7 (6*60=360) and waiting pay of 60.
    """
    paid = _paid(name, date(2026, 1, 1), date(2026, 1, 7), date(2025, 12, 29))
    assert (paid.carenza, paid.indemnity, paid.integration) == (
        Decimal("60.00"),
        Decimal("360.00"),
        Decimal("80.00"),
    )


def test_studi_ordinary_integration_is_netted_on_each_holiday() -> None:
    """The employer integration is 155.00 after holiday extras.

    Jan 6: INAIL 60 plus CCNL 75% target minus 60 = 15, so
    the holiday adds 25; Jan 1 waiting pay 60 adds 40: extra 65.
    The six indemnified days cost 600, ordinary target 450 minus 360
    INAIL = 90; total employer integration 155.00.
    """
    paid = _paid(
        "studi-professionali-confprofessioni",
        date(2026, 1, 1),
        date(2026, 1, 7),
        date(2025, 12, 29),
    )
    assert (paid.indemnity, paid.integration) == (Decimal(360), Decimal(155))


def test_metal_only_letter_b_and_reduced_days() -> None:
    """Only letter b qualifies and reduced-pay days get an extra.

    Jan 1 waiting pay already reaches 100 so adds zero; Jan 6
    (letter b) pays INAIL 60 of 100 and adds 40. April 25 (letter a)
    never qualifies; the ordinary injury integration is not encoded.
    """
    paid = _paid(
        "metalmeccanico-federmeccanica",
        date(2026, 1, 1),
        date(2026, 1, 7),
        date(2025, 12, 29),
    )
    assert paid.integration == Decimal(40)
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.insured_absence is not None
    target = rules.insured_absence.injury
    assert target is not None
    days = covered_target_holidays(target.holiday, load_national_holidays(), 2026)
    assert date(2026, 1, 6) in days
    assert date(2026, 4, 25) not in days


def test_confcommercio_injury_holiday_reaches_gross_quota() -> None:
    """Jan 6: 100 gross = 60 INAIL + 40 employer, despite net ordinary bands."""
    paid = _paid(
        "commercio-confcommercio",
        date(2026, 1, 6),
        date(2026, 1, 6),
        date(2026, 1, 2),
    )
    assert (paid.indemnity, paid.integration) == (Decimal(60), Decimal(40))
    work = load_ccnl("commercio-confcommercio").work_rules
    assert work is not None
    assert work.insured_absence is not None
    injury = work.insured_absence.injury
    assert injury is not None
    assert date(2027, 10, 4) not in covered_target_holidays(
        injury.holiday, load_national_holidays(), 2027
    )


def test_banded_integration_is_netted_on_the_holiday() -> None:
    """Jan 6 INAIL pays 60; the band pays 30 to reach 90% of 100.

    The holiday adds only 10, so total employer integration is 40.
    """
    contract = load_ccnl("studi-professionali-confprofessioni")
    assert contract.work_rules is not None
    assert contract.work_rules.insured_absence is not None
    clause = contract.work_rules.insured_absence.injury
    assert clause is not None
    rules = clause.model_copy(
        update={
            "integration_rate": None,
            "integration_bands": (
                InjuryIntegrationBand(day_from=4, rate=Decimal("0.9")),
            ),
        }
    )
    paid = injury_pay(
        date(2026, 1, 6),
        date(2026, 1, 6),
        date(2026, 1, 2),
        _PAY,
        Decimal(200),
        Decimal(40),
        load_insured_absence_rates().injury,
        rules,
        frozenset({date(2026, 1, 6)}),
    )
    assert paid.integration == Decimal(40)


def test_sunday_and_excluded_code_are_not_topped_up() -> None:
    """No extra is due on Sundays or excluded holiday codes.

    Nov 1, 2026 is Sunday; Oct 4, 2027 is excluded by the clause:
    neither increases the baseline zero integration of a holiday-only rule.
    """
    for first, last, injury_on in [
        (date(2026, 11, 1), date(2026, 11, 2), date(2026, 10, 28)),
        (date(2027, 10, 4), date(2027, 10, 5), date(2027, 9, 30)),
    ]:
        assert _paid("ced-assoced", first, last, injury_on).integration == 0


def test_no_clause_keeps_statutory_injury_unchanged() -> None:
    """Without a holiday clause there is no extra.

    On Jan 6 INAIL pays 60 of the daily 100; without a clause,
    the employer pays zero additional integration.
    """
    paid = injury_pay(
        date(2026, 1, 6),
        date(2026, 1, 6),
        date(2026, 1, 2),
        _PAY,
        Decimal(200),
        Decimal(40),
        load_insured_absence_rates().injury,
        None,
        frozenset({date(2026, 1, 6)}),
    )
    assert (paid.indemnity, paid.integration) == (Decimal(60), Decimal(0))
