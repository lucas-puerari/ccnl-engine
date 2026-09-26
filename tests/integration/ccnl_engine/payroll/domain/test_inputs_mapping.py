"""``PeriodInput.calculation_request`` maps each public fact to the pipeline.

The public inputs are validated in the acceptance suite; this checks the
internal request they produce, field by field.
"""

from __future__ import annotations

from dataclasses import fields
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    ContributableHours,
    ContributionCeilingStatus,
    Dependent,
    DependentRelationship,
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    FixedTerm,
    Headcount,
    OvertimeEvent,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodState,
    PriorYearTaxFacts,
    SeniorityMonths,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId

_YEAR = 2026
_METAL = "metalmeccanico-federmeccanica.json"
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_OVERTIME = OvertimeEvent(
    event_date=date(_YEAR, 6, 10), hours=Decimal(2), hourly_rate=Decimal(15)
)


def test_mapping_copies_every_fact_to_its_request_field() -> None:
    """Each field of the request comes from its owner in the input."""
    family = FamilyComposition(
        dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
    )
    employment = Employment(
        ccnl_slug=_METAL,
        level_code="C3",
        contract_type=FixedTerm(),
        category=WorkerCategory.OPERAIO,
        employment_period=EmploymentPeriod(date(2020, 1, 1)),
        weekly_hours=WeeklyHours(30),
        full_time_weekly_hours=WeeklyHours(40),
        seniority_months=SeniorityMonths(24),
        roles=frozenset({"caposquadra"}),
        ceiling_status=ContributionCeilingStatus.POST_1995,
        sector=EmploymentSector.PRIVATE,
    )
    facts = PeriodFacts(
        contributable_hours=ContributableHours(Decimal(120)),
        events=(_OVERTIME,),
        regione="IT-45",
        comune_belfiore="F257",
        family_composition=family,
        has_dependent_children=True,
    )
    prior = PriorYearTaxFacts(employment_income=Decimal(20000))
    opening = PeriodState.zero()
    run = PayrollRun.regular(_YEAR, 6)
    request = PeriodInput(
        run=run,
        payment_date=date(_YEAR, 6, 28),
        employment=employment,
        employer=_EMPLOYER,
        facts=facts,
        prior_year=prior,
        opening_state=opening,
    ).calculation_request()

    assert request.period_id == PeriodId(year=_YEAR, month=6)
    assert request.run is run
    assert request.payment_date == date(_YEAR, 6, 28)
    assert request.employer is _EMPLOYER
    assert request.opening_state is opening
    assert request.prior_year is prior
    for name in (
        "ccnl_slug",
        "level_code",
        "contract_type",
        "category",
        "employment_period",
        "weekly_hours",
        "full_time_weekly_hours",
        "seniority_months",
        "roles",
        "ceiling_status",
        "sector",
    ):
        assert getattr(request, name) == getattr(employment, name), name
    for field in fields(PeriodFacts):
        name = field.name
        assert getattr(request, name) == getattr(facts, name), name
    assert request.extra_month_accrual is None
    assert request.extra_month_settlements == ()
    assert request.withholding_schedule is None
