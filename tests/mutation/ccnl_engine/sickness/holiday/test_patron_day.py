"""Employer-specific holiday targets use only stated local dates."""

from datetime import date

import pytest

from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.default.employer.policies import EMPLOYER_DEFAULTS
from ccnl_engine.default.models import DefaultPolicy, FactEnforcement
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.holiday.rules import covered_target_holidays


@pytest.mark.parametrize(
    "ccnl_id",
    [
        "studi-professionali-confprofessioni",
        "terziario-confesercenti",
        "ced-assoced",
        "impianti-sportivi-sport",
        "esercizi-cinematografici-anec",
        "metalmeccanico-federmeccanica",
    ],
)
def test_each_clause_covers_the_stated_patron_for_both_absences(ccnl_id: str) -> None:
    """March 19, 2026 is a Thursday: one eligible date per 2026 target."""
    work = load_ccnl(ccnl_id).work_rules
    assert work is not None
    assert work.sickness_rules is not None
    assert work.insured_absence is not None
    assert work.insured_absence.injury is not None
    employer = EmployerProfile(headcount=Headcount(1), patron_saint_day="03-19")
    for target in (work.sickness_rules.holiday, work.insured_absence.injury.holiday):
        assert target is not None
        assert date(2026, 3, 19) in covered_target_holidays(
            target, load_national_holidays(), 2026, employer
        )
        assert date(2026, 3, 19) not in covered_target_holidays(
            target, load_national_holidays(), 2026
        )


@pytest.mark.parametrize(
    "value", ["03-0", "2-19", "02-30", "13-01", "03/19", 319, True]
)
def test_invalid_patron_dates_are_rejected(value: object) -> None:
    """Only valid zero-padded calendar MM-DD dates are employer facts."""
    with pytest.raises(InvalidInputError, match="patron_saint_day"):
        EmployerProfile(headcount=Headcount(1), patron_saint_day=value)  # type: ignore[arg-type]


def test_unstated_patron_is_an_unknown_optional_fact() -> None:
    """Unknown leaves the local holiday unpaid without blocking other pay."""
    policy = EMPLOYER_DEFAULTS["EmployerProfile.patron_saint_day"]
    assert policy.policy is DefaultPolicy.REQUIRES_FACT
    assert policy.enforcement is FactEnforcement.PENDING
    assert EmployerProfile(headcount=Headcount(1)).patron_saint_day is None


def test_a_target_that_does_not_opt_in_and_a_sunday_pay_no_extra() -> None:
    """March 19 is absent without opt-in; March 22 is a Sunday quota."""
    work = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert work is not None
    assert work.sickness_rules is not None
    target = work.sickness_rules.holiday
    assert target is not None
    calendar = load_national_holidays()
    no_opt_in = target.model_copy(update={"includes_patron_saint": False})
    march_19 = EmployerProfile(headcount=Headcount(1), patron_saint_day="03-19")
    march_22 = EmployerProfile(headcount=Headcount(1), patron_saint_day="03-22")
    assert date(2026, 3, 19) not in covered_target_holidays(
        no_opt_in, calendar, 2026, march_19
    )
    assert date(2026, 3, 22) not in covered_target_holidays(
        target, calendar, 2026, march_22
    )


def test_leap_patron_only_applies_in_leap_years() -> None:
    """February 29 exists in 2024, not in 2025 or 2026."""
    work = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert work is not None
    assert work.sickness_rules is not None
    employer = EmployerProfile(headcount=Headcount(1), patron_saint_day="02-29")
    days = covered_target_holidays(
        work.sickness_rules.holiday, load_national_holidays(), 2026, employer
    )
    assert date(2024, 2, 29) in days
    assert date(2025, 2, 28) not in days
