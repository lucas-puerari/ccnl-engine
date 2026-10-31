"""JSON form of a request: round trip, registry, envelope, rejected values."""

from __future__ import annotations

import dataclasses
import json
import typing
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.absence.inputs import AbsenceEvent, SickLeaveEvent
from ccnl_engine.absence.insured.extraordinary.inputs import ExtraordinaryLeaveEvent
from ccnl_engine.absence.insured.hours.inputs import LeaveHours
from ccnl_engine.absence.insured.inputs import (
    MaternityLeaveEvent,
    PaternityLeaveEvent,
    WorkInjuryEvent,
)
from ccnl_engine.absence.insured.parental.inputs import (
    ParentalLeaveEvent,
    ParentalLeaveTaken,
)
from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
from ccnl_engine.absence.insured.rest.inputs import NursingRestEvent
from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.serializers import STATE_TYPES
from ccnl_engine.calendar.inputs import CalendarOverride, CalendarOverrideReason
from ccnl_engine.calendar.models import WorkCalendar
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelAgreement,
    SecondLevelElement,
)
from ccnl_engine.contribution.ceiling.inputs import ContributionHistory
from ccnl_engine.contribution.zone.models import AgriculturalZone
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.change.inputs import EmploymentChange
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    EmploymentPeriod,
    PublicEndOfService,
    WeeklyHours,
    WorkPattern,
)
from ccnl_engine.employment.fixed_term.inputs import FixedTerm, NaspiExclusion
from ccnl_engine.employment.inputs import Apprentice, Contract, Employment, Permanent
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import WorkEvent
from ccnl_engine.extra_month.schedule.models import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.family.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.interchange.request.serializers import (
    REQUEST_SCHEMA_VERSION,
    REQUEST_TYPES,
    Request,
    request_from_json,
    request_to_json,
)
from ccnl_engine.irpef.declaration.inputs import (
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
)
from ccnl_engine.irpef.other_income.inputs import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.leave.inputs import LeaveTakenEvent
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.pension_fund.inputs import NoPensionFund, PensionFundEnrolment
from ccnl_engine.period.inputs import PeriodFacts, PeriodInput
from ccnl_engine.regime.models import (
    EmployerActivity,
    EmploymentSector,
    SubstituteTaxRegime,
)
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import (
    EarnedIncrements,
    SeniorityFact,
    SeniorityPromotion,
    SenioritySource,
)
from ccnl_engine.severance.provision.models import TfrFundBalance
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.tax_credit.foreign.inputs import ForeignTaxPaid
from ccnl_engine.termination.inputs import TerminationTFREvent
from ccnl_engine.termination.notice.inputs import NoticeIndemnityEvent
from ccnl_engine.termination.notice.models import TerminationCause
from ccnl_engine.variable_pay.inputs import (
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    TravelAllowanceEvent,
    WelfareEvent,
)
from ccnl_engine.working_time.inputs import (
    HolidayWorkEvent,
    HolidayWorkKind,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftKind,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.standby.inputs import StandbyEvent, StandbyKind
from ccnl_engine.year.competence.inputs import CompetenceYearPlan
from ccnl_engine.year.tax_year.inputs import TaxYearPlan
from tests.unit.ccnl_engine import support

_DAY = date(2026, 3, 10)
_AMOUNT = Decimal("120.50")

#: One event of each work event type.
_EVENTS: dict[type, WorkEvent] = {
    type(event): event
    for event in (
        AbsenceEvent(_DAY, Decimal(8), Decimal("12.40"), end_date=date(2026, 3, 11)),
        ArrearsEvent(
            _DAY, _AMOUNT, Decimal("0.23"), reference_period=PeriodId(2025, 6)
        ),
        BilateralFundEvent(_DAY, Decimal("10.00"), Decimal("20.00")),
        BonusEvent(
            _DAY, _AMOUNT, kind="contract_renewal", agreement_signed_on=date(2025, 1, 1)
        ),
        FringeEvent(_DAY, _AMOUNT),
        HolidayWorkEvent(_DAY, _AMOUNT, kind=HolidayWorkKind.HOLIDAY),
        LeaveTakenEvent(_DAY, next(iter(LeaveBucket)), Decimal(2)),
        HolidayWorkEvent(_DAY, _AMOUNT),
        MaternityLeaveEvent(_DAY, date(2026, 8, 7)),
        PaternityLeaveEvent((_DAY,)),
        DisabilityPermitEvent((_DAY,), (LeaveHours(date(2026, 3, 3), Decimal("1.5")),)),
        ExtraordinaryLeaveEvent(_DAY, _DAY, Decimal("2000.00")),
        NursingRestEvent((LeaveHours(_DAY, Decimal(2)),), date(2026, 1, 15)),
        NoticeIndemnityEvent(_DAY, TerminationCause.DISMISSAL, just_cause=False),
        ParentalLeaveEvent(
            _DAY,
            _DAY,
            date(2025, 6, 1),
            ParentalLeaveTaken(30, 10, 0),
            single_parent=True,
        ),
        NightShiftEvent(_DAY, _AMOUNT),
        OvertimeEvent(
            _DAY,
            Decimal("2.5"),
            Decimal("15.00"),
            Decimal("1.25"),
            list(OvertimeKind)[-1],
        ),
        ShiftWorkEvent(_DAY, _AMOUNT, kind=ShiftKind.NIGHT),
        SickLeaveEvent(_DAY, _AMOUNT, sick_days=3, waiting_period_days=3),
        SicknessEpisode(
            "E1",
            date(2026, 3, 2),
            date(2026, 3, 13),
            hospital_stays=((date(2026, 3, 3), date(2026, 3, 5)),),
        ),
        StandbyEvent(_DAY, next(iter(StandbyKind)), Decimal(2), calls=1),
        TerminationTFREvent(_DAY, _AMOUNT, Decimal("0.23")),
        TravelAllowanceEvent(
            _DAY, 2, True, "one", daily_amount=Decimal("46.48"), tfr_base="whole"
        ),
        WelfareEvent(_DAY, _AMOUNT),
        WorkInjuryEvent(_DAY, date(2026, 4, 20)),
    )
}

#: One contract of each contract type.
_CONTRACTS: dict[type, Contract] = {
    type(contract): contract
    for contract in (
        Permanent(),
        FixedTerm(renewals=1, naspi_exclusion=next(iter(NaspiExclusion))),
        Apprentice(months_elapsed=7, track="professionalizzante"),
    )
}


def _employment(contract: Contract) -> Employment:
    return Employment(
        ccnl_id="metalmeccanico-federmeccanica",
        level_code="C3",
        contract_type=contract,
        category=WorkerCategory.IMPIEGATO,
        employment_period=EmploymentPeriod(date(2020, 1, 1), date(2030, 12, 31)),
        weekly_hours=WeeklyHours(Decimal(30)),
        full_time_weekly_hours=WeeklyHours(Decimal(40)),
        work_pattern=WorkPattern(
            weekday_hours=(Decimal(6),) * 5 + (Decimal(0),) * 2,
            months=frozenset(range(1, 12)),
        ),
        seniority=SeniorityFact(
            60,
            date(2025, 12, 31),
            next(iter(SenioritySource)),
            EarnedIncrements(2, Decimal("40.00")),
            SeniorityPromotion(date(2025, 7, 1), "C2"),
        ),
        roles=frozenset({"capo_squadra", "addetto_primo_soccorso"}),
        contribution_history=ContributionHistory(date(2001, 9, 1)),
        sector=next(iter(EmploymentSector)),
        pension_fund=PensionFundEnrolment("cometa", Decimal("0.012"), True),
        tfr_fund=TfrFundBalance(2025, Decimal("8000.00")),
        tfr_treasury_fund=True,
        individual_elements=(
            IndividualElement(
                "superminimo", Decimal(200), absorbable=True, as_of=date(2026, 1, 1)
            ),
        ),
        erc_amount=Decimal(0),
        public_end_of_service=None,
    )


def _employer() -> EmployerProfile:
    return EmployerProfile(
        headcount=Headcount(50),
        activity=next(iter(EmployerActivity)),
        agricultural_zone=next(iter(AgriculturalZone)),
        inps_sector=next(iter(TaxSector)),
        second_level_elements=(
            SecondLevelElement(
                "premio_presenza",
                Decimal("50.00"),
                SecondLevelAgreement.TERRITORIAL,
                date(2026, 1, 1),
                date(2026, 12, 31),
                levels=("C3",),
                extra_months=False,
                tfr_relevant=False,
            ),
        ),
    )


def _family() -> FamilyComposition:
    child = Dependent(
        list(DependentRelationship)[1],
        birth_date=date(2015, 4, 2),
        allocation_pct=Decimal("0.5"),
        dependent_from=None,
        dependent_until=None,
    )
    return FamilyComposition(dependents=(child,))


def _facts(events: tuple[WorkEvent, ...]) -> PeriodFacts:
    return PeriodFacts(
        contributable_hours=ContributableHours(Decimal(120)),
        ordinary_hours_worked=None,
        events=events,
        regione="IT-45",
        comune_belfiore="F257",
        family_composition=_family(),
    )


def _prior_year() -> PriorYearTaxFacts:
    return PriorYearTaxFacts(
        employment_income=Decimal("31000.00"),
        waived_regimes=frozenset(SubstituteTaxRegime),
        shortfall_deferral=ShortfallDeferralRequest(date(2026, 1, 15)),
        foreign_taxes=(ForeignTaxPaid("FR", Decimal(1000), Decimal(200)),),
    )


def _current_year() -> CurrentYearTaxFacts:
    return CurrentYearTaxFacts(
        tax_year=2026,
        other_employment_income=Decimal(0),
        other_employment_inps_base=Decimal(0),
        other_income=Decimal("500.00"),
        main_dwelling_income=Decimal(0),
        exempt_regime_income=Decimal(0),
        estimated_on=date(2026, 1, 10),
        quality=next(iter(IncomeEstimateQuality)),
    )


def _period_input(contract: Contract, events: tuple[WorkEvent, ...]) -> PeriodInput:
    return PeriodInput(
        run=PayrollRun.regular(2026, 3),
        payment_date=date(2026, 3, 27),
        employment=_employment(contract),
        employer=_employer(),
        facts=_facts(events),
        prior_year=_prior_year(),
        current_year=_current_year(),
    )


def _calendar_override() -> CalendarOverride:
    calendar = WorkCalendar(
        2026,
        extra_months=(
            ExtraMonthSchedule(next(iter(ExtraMonthKind)), "Tredicesima", 12),
        ),
    )
    return CalendarOverride(
        calendar, next(iter(CalendarOverrideReason)), "Company calendar"
    )


def _competence_year(opening_state: PeriodState | None = None) -> CompetenceYearPlan:
    periods: dict[int | str, PeriodFacts] = {
        3: _facts(tuple(_EVENTS.values())),
        "2026-12-thirteenth": PeriodFacts(),
    }
    return CompetenceYearPlan(
        year=2026,
        employment=_employment(Permanent()),
        employer=_employer(),
        prior_year=_prior_year(),
        current_year=_current_year(),
        periods=periods,
        calendar_override=_calendar_override(),
        payment_day=27,
        payment_dates={12: date(2027, 1, 10)},
        employment_changes=(EmploymentChange(date(2026, 7, 1), level_code="C2"),),
        opening_state=opening_state,
    )


def _tax_year() -> TaxYearPlan:
    return TaxYearPlan(
        tax_year=2026,
        competence_years=(_competence_year(),),
        opening_state=PeriodState.zero(),
        current_year=_current_year(),
    )


def _public_employee() -> PeriodInput:
    request = _period_input(Permanent(), ())
    employment = dataclasses.replace(
        request.employment,
        pension_fund=NoPensionFund(),
        public_end_of_service=next(iter(PublicEndOfService)),
        tfr_treasury_fund=None,
    )
    return dataclasses.replace(request, employment=employment)


def _requests() -> list[Request]:
    return [
        _period_input(Permanent(), tuple(_EVENTS.values())),
        *(_period_input(contract, ()) for contract in _CONTRACTS.values()),
        _public_employee(),
        _competence_year(PeriodState.zero()),
        _tax_year(),
    ]


def test_every_work_event_and_contract_type_has_a_sample() -> None:
    """A new event or contract type fails here until it has a sample."""
    assert set(_EVENTS) == set(typing.get_args(WorkEvent))
    assert set(_CONTRACTS) == set(typing.get_args(Contract.__value__))


@pytest.mark.parametrize(
    "event", list(_EVENTS.values()), ids=lambda e: type(e).__name__
)
def test_a_period_with_each_event_reads_back_equal(event: WorkEvent) -> None:
    """Every work event survives the round trip inside a period."""
    request = _period_input(Permanent(), (event,))
    assert request_from_json(request_to_json(request), PeriodInput) == request


@pytest.mark.parametrize(
    "contract", list(_CONTRACTS.values()), ids=lambda c: type(c).__name__
)
def test_a_period_with_each_contract_reads_back_equal(contract: Contract) -> None:
    """Every contract type survives the round trip inside a period."""
    request = _period_input(contract, ())
    assert request_from_json(request_to_json(request), PeriodInput) == request


def test_a_competence_year_reads_back_equal_with_its_run_keys() -> None:
    """Month and run-id keys stay an int and a str, not JSON object keys."""
    plan = _competence_year(PeriodState.zero())
    read = request_from_json(request_to_json(plan), CompetenceYearPlan)
    assert read == plan
    assert set(read.periods) == {3, "2026-12-thirteenth"}
    assert read.facts_for(PayrollRun.regular(2026, 3)) == plan.facts_for(
        PayrollRun.regular(2026, 3)
    )


def test_a_public_employee_without_a_pension_fund_reads_back_equal() -> None:
    """The stated absence of a fund and the end-of-service regime survive."""
    request = _public_employee()
    assert request_from_json(request_to_json(request), PeriodInput) == request


def test_a_tax_year_reads_back_equal() -> None:
    """A tax-year plan with its competence years survives the round trip."""
    plan = _tax_year()
    assert request_from_json(request_to_json(plan), TaxYearPlan) == plan


def test_the_text_is_stable_and_carries_its_schema() -> None:
    """Sets are sorted and keys ordered: one request, one text."""
    request = _period_input(Permanent(), ())
    text = request_to_json(request)
    payload = json.loads(text)
    assert payload["schema_version"] == REQUEST_SCHEMA_VERSION
    assert set(payload) == {"schema_version", "request"}
    roles = payload["request"]["fields"]["employment"]["fields"]["roles"]
    assert roles == {"$set": ["addetto_primo_soccorso", "capo_squadra"]}
    assert request_to_json(request_from_json(text, PeriodInput)) == text


def _tags(value: object) -> set[str]:
    if isinstance(value, list):
        return {tag for item in value for tag in _tags(item)}
    if not isinstance(value, dict):
        return set()
    own = {value[key] for key in ("$type", "$enum") if key in value}
    return own | {tag for item in value.values() for tag in _tags(item)}


def test_the_samples_cover_every_request_type() -> None:
    """Each registered type outside the state is exercised by a round trip.

    The state types are exercised by the tests of the state codec.
    """
    written = {
        tag
        for request in _requests()
        for tag in _tags(json.loads(request_to_json(request)))
    }
    assert set(REQUEST_TYPES) - set(STATE_TYPES) <= written


def test_the_registry_holds_every_type_of_a_request() -> None:
    """Each dataclass and enum a request can hold has a tag, and only those."""
    registered = set(REQUEST_TYPES.values())
    reachable = support.reachable(
        (PeriodInput, CompetenceYearPlan, TaxYearPlan), support.domain_types()
    )
    difference = sorted(
        f"{c.__module__}.{c.__qualname__}" for c in registered ^ reachable
    )
    assert registered == reachable, difference
    assert len({cls.__name__ for cls in registered}) == len(registered)


def _envelope(**changes: object) -> str:
    payload = json.loads(request_to_json(_period_input(Permanent(), ())))
    payload.update(changes)
    return json.dumps(payload)


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("not json", id="not-json"),
        pytest.param("[]", id="not-an-object"),
        pytest.param(_envelope(schema_version=0), id="other-schema"),
        pytest.param(_envelope(request=[1]), id="request-not-an-object"),
        pytest.param(
            _envelope(request={"$type": "TaxYearPlan", "fields": {}}), id="other-kind"
        ),
    ],
)
def test_a_text_that_is_not_a_period_input_is_rejected_whole(text: str) -> None:
    """The envelope is checked before any value: no field is named."""
    with pytest.raises(InvalidInputError) as caught:
        request_from_json(text, PeriodInput)
    assert caught.value.field is None


def test_the_first_rejected_value_is_raised_at_its_path() -> None:
    """A constructor error names the field from the root of the request."""
    payload = json.loads(
        request_to_json(_period_input(Permanent(), (FringeEvent(_DAY, _AMOUNT),)))
    )
    event = payload["request"]["fields"]["facts"]["fields"]["events"]["$tuple"][0]
    event["fields"]["amount"] = {"$decimal": "-1"}
    with pytest.raises(InvalidInputError) as caught:
        request_from_json(json.dumps(payload), PeriodInput)
    assert caught.value.field == "PeriodInput.facts.events[0].amount"


def test_a_sickness_episode_in_the_opening_state_reads_back() -> None:
    """An opening state inside a request is read with the request types."""
    zero = PeriodState.zero()
    accrual = zero.accrual.__class__(
        sickness_episodes=(SicknessEpisode("A", date(2026, 1, 5), date(2026, 1, 9)),),
        sickness_known_from=date(2026, 1, 1),
    )
    state = PeriodState(accrual=accrual, cash=zero.cash, history_known=False)
    plan = TaxYearPlan(
        tax_year=2026, competence_years=(_competence_year(),), opening_state=state
    )
    assert request_from_json(request_to_json(plan), TaxYearPlan) == plan


def test_an_old_schema_names_both_versions_and_what_to_do() -> None:
    """No migration: the error says which schema it found and which it reads."""
    with pytest.raises(InvalidInputError) as caught:
        request_from_json(_envelope(schema_version=1), PeriodInput)
    message = str(caught.value)
    assert "schema_version 1" in message
    assert repr(REQUEST_SCHEMA_VERSION) in message
    assert caught.value.remediation is not None
    assert "release that wrote it" in caught.value.remediation
