"""Payment dates of a competence-year plan."""

from __future__ import annotations

import copy
import pickle
from datetime import date, datetime

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment, Permanent
from ccnl_engine.payroll.domain.inputs import PeriodFacts
from ccnl_engine.payroll.domain.run import PayrollRun

_EMPLOYMENT = Employment(
    ccnl_slug="commercio-confcommercio.json", level_code="4", contract_type=Permanent()
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _plan(dates: object, payment_day: int = 28) -> CompetenceYearPlan:
    return CompetenceYearPlan(
        year=2026,
        employment=_EMPLOYMENT,
        employer=_EMPLOYER,
        payment_day=payment_day,
        payment_dates=dates,  # type: ignore[arg-type]
    )


def test_a_run_is_paid_on_its_date_or_on_the_payment_day() -> None:
    """December on 13 January 2027; the tredicesima on the 10th of December."""
    plan = _plan({12: date(2027, 1, 13)}, payment_day=10)

    assert str(plan.payment_for(PayrollRun.regular(2026, 12))) == (
        "2026-12-regular@2027-01-13"
    )
    assert str(plan.payment_for(PayrollRun.thirteenth(2026, 12))) == (
        "2026-12-thirteenth@2026-12-10"
    )
    assert plan.dated_runs == {"2026-12-regular"}


@pytest.mark.parametrize(
    ("dates", "field"),
    [
        ({12: "2027-01-13"}, "CompetenceYearPlan.payment_dates[12]"),
        ({12: datetime(2027, 1, 13)}, "CompetenceYearPlan.payment_dates[12]"),  # noqa: DTZ001
        ({13: date(2027, 1, 13)}, "CompetenceYearPlan.payment_dates[13]"),
        ({12: date(2026, 11, 30)}, "PaymentId.payment_date"),
        (
            {12: date(2027, 1, 13), "2026-12-regular": date(2027, 1, 14)},
            "CompetenceYearPlan.payment_dates['2026-12-regular']",
        ),
        ([date(2027, 1, 13)], "CompetenceYearPlan.payment_dates"),
    ],
    ids=["text", "datetime", "month 13", "before the month", "twice", "not a map"],
)
def test_rejects_payment_dates_that_cannot_pay_a_run(dates: object, field: str) -> None:
    """A date per run of the year, not before the run month."""
    with pytest.raises(InvalidInputError) as info:
        _plan(dates)

    assert info.value.field == field


def test_the_plan_keeps_its_own_copy_of_the_dates() -> None:
    """A caller editing its dict after the plan is built changes nothing."""
    dates = {12: date(2026, 12, 18)}
    plan = _plan(dates)
    dates[12] = date(2026, 12, 20)

    assert plan.payment_dates == {12: date(2026, 12, 18)}


def test_the_dates_of_a_plan_cannot_be_changed() -> None:
    """The exposed dates are the ones the plan pays on, and stay so."""
    plan = _plan({12: date(2026, 12, 18)})

    with pytest.raises(TypeError):
        plan.payment_dates[12] = date(2027, 1, 13)  # type: ignore[index]

    assert plan.payment_dates == {12: date(2026, 12, 18)}
    assert str(plan.payment_for(PayrollRun.regular(2026, 12))) == (
        "2026-12-regular@2026-12-18"
    )


def test_the_facts_of_a_plan_cannot_be_changed() -> None:
    """A month's facts read by the runs are the ones the plan exposes."""
    facts = PeriodFacts(regione="IT-25")
    plan = CompetenceYearPlan(
        year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER, periods={3: facts}
    )

    with pytest.raises(TypeError):
        plan.periods[4] = facts  # type: ignore[index]

    assert plan.periods == {3: facts}
    assert plan.facts_for(PayrollRun.regular(2026, 3)) is facts
    assert plan.facts_for(PayrollRun.regular(2026, 4)) is plan.default_facts
    assert dict(plan.facts_by_run) == {"2026-03-regular": facts}


def test_a_copied_plan_keeps_its_runs() -> None:
    """A deep copy and a pickle round trip pay and read the same runs."""
    plan = _plan({12: date(2027, 1, 13)})

    for twin in (copy.deepcopy(plan), pickle.loads(pickle.dumps(plan))):
        assert twin == plan
        assert twin.payment_for(PayrollRun.regular(2026, 12)) == plan.payment_for(
            PayrollRun.regular(2026, 12)
        )


def test_a_plan_of_year_9999_is_rejected() -> None:
    """Its December could be paid in 10000, which is not a date."""
    with pytest.raises(InvalidInputError):
        CompetenceYearPlan(year=9999, employment=_EMPLOYMENT, employer=_EMPLOYER)
