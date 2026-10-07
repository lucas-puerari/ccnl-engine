"""``PeriodInput.calculation_request`` maps each public fact to the pipeline.

The public inputs are validated in the acceptance suite; this checks the
internal request they produce, field by field.
"""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    ContributableHours,
    ContributionHistory,
    DependentRelationship,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    FixedTerm,
    InpsBaseYtd,
    PeriodState,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from tests.fixtures.current_year import employment_only
from tests.fixtures.dependents import declared_dependent

_YEAR = 2026
_METAL = "metalmeccanico-federmeccanica.json"
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_OVERTIME = OvertimeEvent(
    event_date=date(_YEAR, 6, 10), hours=Decimal(2), hourly_rate=Decimal(15)
)


#: Request fields copied unchanged from :class:`Employment`.
_EMPLOYMENT_FIELDS = (
    "ccnl_slug",
    "level_code",
    "contract_type",
    "category",
    "employment_period",
    "weekly_hours",
    "full_time_weekly_hours",
    "seniority",
    "roles",
    "contribution_history",
    "sector",
)


def _employment() -> Employment:
    return Employment(
        ccnl_slug=_METAL,
        level_code="C3",
        contract_type=FixedTerm(),
        category=WorkerCategory.OPERAIO,
        employment_period=EmploymentPeriod(date(2020, 1, 1)),
        weekly_hours=WeeklyHours(30),
        full_time_weekly_hours=WeeklyHours(40),
        seniority=SeniorityFact(24, date(2026, 1, 1), SenioritySource.PAYSLIP),
        roles=frozenset({"caposquadra"}),
        contribution_history=ContributionHistory(date(2001, 9, 1)),
        sector=EmploymentSector.PRIVATE,
    )


def _facts() -> PeriodFacts:
    family = FamilyComposition(
        dependents=(declared_dependent(relationship=DependentRelationship.SPOUSE),)
    )
    return PeriodFacts(
        contributable_hours=ContributableHours(Decimal(120)),
        events=(_OVERTIME,),
        regione="IT-45",
        comune_belfiore="F257",
        family_composition=family,
    )


def test_mapping_copies_every_fact_to_its_request_field() -> None:
    """Each field of the request comes from its owner in the input."""
    employment = _employment()
    facts = _facts()
    prior = PriorYearTaxFacts(employment_income=Decimal(20000))
    current = employment_only(_YEAR)
    opening = PeriodState.zero()
    run = PayrollRun.regular(_YEAR, 6)
    request = PeriodInput(
        run=run,
        payment_date=date(_YEAR, 6, 28),
        employment=employment,
        employer=_EMPLOYER,
        facts=facts,
        prior_year=prior,
        current_year=current,
        opening_state=opening,
    ).calculation_request()

    assert request.period_id == PeriodId(year=_YEAR, month=6)
    assert request.run is run
    assert request.payment_date == date(_YEAR, 6, 28)
    assert request.employer is _EMPLOYER
    stated = InpsBaseYtd(_YEAR, Decimal(0), current.other_employment_inps_base)
    assert request.opening_state == replace(
        opening, accrual=EmploymentAccrualState(inps_bases=(stated,))
    )
    assert request.prior_year is prior
    assert request.current_year is current
    for name in _EMPLOYMENT_FIELDS:
        assert getattr(request, name) == getattr(employment, name), name
    for field in fields(PeriodFacts):
        name = field.name
        assert getattr(request, name) == getattr(facts, name), name
    assert request.extra_month_accrual is None
    assert request.extra_month_settlements is None
    assert request.withholding_schedule is None
