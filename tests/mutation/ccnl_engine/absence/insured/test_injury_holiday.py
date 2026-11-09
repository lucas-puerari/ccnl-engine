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
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.sickness.holiday.rules import covered_target_holidays
from ccnl_engine.sickness.term.rules import DailyQuota

_PAY = MonthPay(
    chain=MonthlyPayChain(base=Decimal(3000), seniority=Decimal(0), allowances=()),
    quota=DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
    extra_months=1,
    employee_rate=Decimal("0.0919"),
)


def _paid(
    name: str,
    first: date,
    last: date,
    injury_on: date,
    employer: EmployerProfile | None = None,
) -> InsuredPay:
    contract = load_ccnl(name)
    assert contract.work_rules is not None
    assert contract.work_rules.insured_absence is not None
    rules = contract.work_rules.insured_absence.injury
    assert rules is not None
    holidays = covered_target_holidays(
        rules.holiday, load_national_holidays(), first.year, employer
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


def test_patron_day_in_work_injury_needs_a_stated_employer_day() -> None:
    """March 19: INAIL pays 60 of daily 100; the stated patron adds 40.

    Without the employer fact there is no additional holiday payment.
    """
    first = last = date(2026, 3, 19)
    injury_on = date(2026, 3, 15)
    name = "metalmeccanico-federmeccanica"
    absent = _paid(name, first, last, injury_on)
    stated = _paid(
        name,
        first,
        last,
        injury_on,
        EmployerProfile(headcount=Headcount(50), patron_saint_day="03-19"),
    )
    assert (absent.indemnity, absent.integration) == (Decimal(60), Decimal(0))
    assert (stated.indemnity, stated.integration) == (Decimal(60), Decimal(40))


@pytest.mark.parametrize(
    "name",
    ["esercizi-cinematografici-anec"],
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


def test_confapi_january_injury_month_tops_up_epiphany() -> None:
    """Jan 1-7: Jan 1 waiting pays 60 and Jan 2-7 INAIL pays 6*60=360.

    Daily global pay is 3000/30=100. Before art. 32, employer holiday
    integration was 0; now Jan 1 and Jan 6 each add 100-60=40, so the
    month slice pays 60+360+80=500 rather than 420.
    """
    paid = _paid(
        "metalmeccanico-confapi",
        date(2026, 1, 1),
        date(2026, 1, 7),
        date(2025, 12, 29),
    )
    assert (paid.carenza, paid.indemnity, paid.integration) == (
        Decimal(60),
        Decimal(360),
        Decimal(80),
    )


def test_confapi_april_injury_month_excludes_liberation_day() -> None:
    """Apr 24-26, 2028: INAIL pays 3*60=180 of 3*100 daily pay.

    Before and after art. 32, April 25 (letter a) adds zero: the slice
    pays 180, not the 220 due if the holiday were incorrectly included.
    """
    paid = _paid(
        "metalmeccanico-confapi",
        date(2028, 4, 24),
        date(2028, 4, 26),
        date(2028, 4, 20),
    )
    assert (paid.carenza, paid.indemnity, paid.integration) == (
        Decimal(0),
        Decimal(180),
        Decimal(0),
    )
    work = load_ccnl("metalmeccanico-confapi").work_rules
    assert work is not None
    assert work.insured_absence is not None
    injury = work.insured_absence.injury
    assert injury is not None
    days = covered_target_holidays(injury.holiday, load_national_holidays(), 2028)
    assert date(2028, 4, 25) not in days
    assert date(2028, 1, 6) in days
    assert date(2028, 10, 4) not in days


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
    neither increases the ordinary integration due on those days.
    """
    for first, last, injury_on in [
        (date(2026, 11, 1), date(2026, 11, 2), date(2026, 10, 28)),
        (date(2027, 10, 4), date(2027, 10, 5), date(2027, 9, 30)),
    ]:
        paid = _paid("ced-assoced", first, last, injury_on)
        rules = load_ccnl("ced-assoced").work_rules
        assert rules is not None
        assert rules.insured_absence is not None
        injury = rules.insured_absence.injury
        assert injury is not None
        without_holiday = injury.model_copy(update={"holiday": None})
        baseline = injury_pay(
            first,
            last,
            injury_on,
            _PAY,
            Decimal(200),
            Decimal(40),
            load_insured_absence_rates().injury,
            without_holiday,
        )
        assert paid.integration == baseline.integration


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


@pytest.mark.parametrize(
    ("name", "target", "integration"),
    [
        ("ced-assoced", Decimal("0.75"), Decimal("197.13")),
        ("terziario-confesercenti", Decimal("0.90"), Decimal("672.13")),
        ("impianti-sportivi-sport", Decimal("0.90"), Decimal("672.13")),
    ],
)
def test_ordinary_injury_month_crosses_waiting_and_integration_bands(
    name: str, target: Decimal, integration: Decimal
) -> None:
    """January injury: 2-4 waiting = 3*60 = 180; INAIL 5-31 = 27*60 = 1620.

    With the BY_30 pay quota (January 31 is excluded), the employer target
    is 26*75=1950 for CED, or 16*90+10*100=2440 for the other
    contracts. The net-basis INAIL
    offset is 1620 / .9081 = 1783.94; the January 6 holiday adds
    100-(60+75-60/.9081)=31.07 for CED, or
    100-(60+90-60/.9081)=16.07 otherwise. January 1 is paid in full.
    Before ordinary integration, the paid replacement was 180+1620+40
    (the holiday only); after it is 180+1620+integration.
    """
    clause = load_ccnl(name).work_rules
    assert clause is not None
    assert clause.insured_absence is not None
    injury = clause.insured_absence.injury
    assert injury is not None
    assert injury.integration_bands[0].day_from == 4
    assert injury.integration_bands[0].rate == target
    if name != "ced-assoced":
        assert [(b.day_from, b.rate) for b in injury.integration_bands] == [
            (4, Decimal("0.90")),
            (20, Decimal(1)),
        ]
    paid = _paid(name, date(2026, 1, 1), date(2026, 1, 31), date(2026, 1, 1))
    assert (paid.deduction, paid.carenza, paid.indemnity, paid.integration) == (
        Decimal("2900.00"),
        Decimal("180.00"),
        Decimal("1620.00"),
        integration,
    )
    assert paid.carenza_units == 3
