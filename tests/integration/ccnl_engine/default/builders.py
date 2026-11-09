"""Pairs of requests: a defaulted public field stated, and left to its default.

Every ``requires_fact`` field of
:mod:`ccnl_engine.default.policies` has a
:class:`DefaultCase` in :data:`DEFAULT_CASES` or a reason not to, as
``test_policies_default_registry_coverage.py`` checks.
Each case is the explicit Concia D2 of 2026
(:mod:`tests.knowledge.ccnl_engine.period.builders`)
with one field changed: ``true`` states the fact, ``default`` leaves the field
to its default; ``tests/integration/ccnl_engine/api/test_default_facts.py`` runs both.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    TaxYearPlan,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.events import (
    AbsenceEvent,
    AgriculturalDays,
    ArrearsEvent,
    BonusEvent,
    ExtraordinaryLeaveEvent,
    NightShiftEvent,
    PeriodId,
    SicknessEpisode,
    TerminationTFREvent,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    Dependent,
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    FixedTerm,
    InpsBaseYtd,
    NaspiCase,
    NaspiExclusion,
    NoPensionFund,
    OpeningBalances,
    PensionFundEnrolment,
    PeriodState,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    TerminationCause,
    TfrFundBalance,
    TfrQuotaYtd,
    WeeklyHours,
    WorkerCategory,
    WorkPattern,
)
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from tests.integration.ccnl_engine.default.event.builders import (
    absence_cases,
)
from tests.integration.ccnl_engine.default.fact.builders import (
    employer_cases,
    fixed_term_cases,
    pension_cases,
    sickness_cases,
)
from tests.integration.ccnl_engine.family.builders import (
    declared_dependent,
)
from tests.knowledge.ccnl_engine.balance.builders import (
    fresh_tax_year,
)
from tests.knowledge.ccnl_engine.period.builders import (
    CONCIA_D2,
    EMPLOYER,
    FACTS,
    competence_year,
    regular_run,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.events import WorkEvent

__all__ = [
    "DEFAULT_CASES",
    "DefaultCase",
    "Request",
]

type Request = PeriodInput | CompetenceYearPlan | TaxYearPlan


@dataclass(frozen=True)
class DefaultCase:
    """One field stated and left to its default, all else equal.

    Attributes:
        true: The request stating the fact.
        default: The same request with the field left to its default.
        names: Detail of the blocker the default adds and the fact lacks,
            ``None`` when the scenario does not reach a branch the fact
            decides (the property alone is checked).
        engine: Optional engine with an in-memory agreement rule for this pair.
    """

    true: Request
    default: Request
    names: str | None = None
    engine: PayrollEngine | None = None


def _january(
    employment: Employment = CONCIA_D2,
    *,
    events: tuple[WorkEvent, ...] = (),
    family: FamilyComposition | None = None,
) -> PeriodInput:
    """Return the January run of a hire on 1 January: the zero state is a fact.

    Returns:
        The request with every other fact explicit.
    """
    facts = FACTS if family is None else replace(FACTS, family_composition=family)
    return regular_run(
        1,
        employment=employment,
        facts=facts,
        events=events,
        opening_state=PeriodState.zero(),
    )


def _studi_fourteenth(amount: Decimal | None) -> PeriodInput:
    """Build the June fourteenth of a worker employed at contract entry.

    Returns:
        A run that must read the historical extra-month amount.
    """
    employment = replace(
        CONCIA_D2,
        ccnl_id="studi-professionali-confprofessioni",
        level_code="4",
        category=None,
        seniority=None,
        employment_period=EmploymentPeriod(date(2020, 1, 1)),
        prior_extra_month_amount=amount,
    )
    return replace(
        _january(employment),
        run=PayrollRun.fourteenth(2026, 6),
        payment_date=date(2026, 6, 28),
    )


def _employment_pair(
    true: Employment, default: Employment, names: str | None = None
) -> DefaultCase:
    return DefaultCase(_january(true), _january(default), names)


def _event_pair(
    true: WorkEvent, default: WorkEvent, names: str | None = None
) -> DefaultCase:
    request = replace(_january(), prior_year=_ELIGIBLE_PRIOR)
    return DefaultCase(
        replace(request, facts=replace(request.facts, events=(true,))),
        replace(request, facts=replace(request.facts, events=(default,))),
        names,
    )


def _dependent_pair(fact: str, dependent: Dependent) -> DefaultCase:
    fields: dict[str, Any] = {fact: None}
    unknown = replace(dependent, **fields)
    return DefaultCase(
        _january(family=FamilyComposition(dependents=(dependent,))),
        _january(family=FamilyComposition(dependents=(unknown,))),
        fact,
    )


#: Part time on a 40-hour week: the income of the year is within the
#: 20,000 EUR limit of the somma esente (L. 207/2024 art. 1 c. 4), whose
#: reddito complessivo reads the income beyond this employment.
_PART_TIME = replace(CONCIA_D2, weekly_hours=WeeklyHours(Decimal(20)))
#: Hired on 1 January 2025: a run of 2026 needs the history of 2025.
_SINCE_2025 = replace(CONCIA_D2, employment_period=EmploymentPeriod(date(2025, 1, 1)))
_PART_TIME_SINCE_2025 = replace(_SINCE_2025, weekly_hours=WeeklyHours(Decimal(20)))
#: A bonus above the IVS massimale of 2026 (L. 335/1995 art. 2 c. 18), whose
#: application depends on the first enrolment of the worker.
_LARGE_BONUS = BonusEvent(event_date=date(2026, 1, 15), amount=Decimal(150_000))
#: Prior-year income within the income caps of the renewal and night-work
#: substitute tax regimes of the bundle.
_ELIGIBLE_PRIOR = PriorYearTaxFacts(employment_income=Decimal(20_000))
_EVENT_DAY = date(2026, 1, 15)
_SIGNED_ON = date(2025, 3, 1)
#: The explicit worker with no category, for a level that fixes another one.
_UNCATEGORISED = replace(CONCIA_D2, category=None)
_TABACCO_3A = replace(
    _UNCATEGORISED, ccnl_id="tabacco-apti", level_code="3A", pension_fund=None
)
_ALIFOND = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=False)
#: Confapi January 2026: New Year and Epiphany both fall on weekdays.
_CONFAPI_HOLIDAYS = replace(
    _UNCATEGORISED,
    ccnl_id="metalmeccanico-confapi",
    level_code="5",
    roles=frozenset({"former_legal_operaio"}),
    holiday_company_offset=Decimal(0),
)
#: Alimentari 1S, a quadro level paying the IND_FUNZIONE_QUADRO allowance
#: to the holders of the role ``quadro``.
_ALIMENTARI_1S = replace(
    _UNCATEGORISED, ccnl_id="alimentari-federalimentare", level_code="1S"
)
_ASCENDANT = declared_dependent(DependentRelationship.ASCENDANT)
_SPOUSE = declared_dependent(DependentRelationship.SPOUSE)
_CHILD = declared_dependent(DependentRelationship.CHILD, birth_date=date(2004, 3, 1))
_CURRENT = CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 1))


def _renewal(signed_on: date | None = _SIGNED_ON) -> BonusEvent:
    return BonusEvent(
        event_date=_EVENT_DAY,
        amount=Decimal(2_000),
        kind="contract_renewal",
        agreement_signed_on=signed_on,
    )


def _night_shift(employer: EmployerProfile) -> PeriodInput:
    request = replace(_january(), employer=employer, prior_year=_ELIGIBLE_PRIOR)
    night = NightShiftEvent(_EVENT_DAY, Decimal(500))
    return replace(request, facts=replace(request.facts, events=(night,)))


def _arrears(reference_period: PeriodId | None) -> ArrearsEvent:
    return ArrearsEvent(_EVENT_DAY, Decimal(500), Decimal("0.23"), reference_period)


def _unrated() -> ArrearsEvent:
    return ArrearsEvent(_EVENT_DAY, Decimal(500), reference_period=PeriodId(2025, 6))


def _leave(suspends_accrual: bool | None) -> AbsenceEvent:
    # Unpaid leave of March 2026 but the 1st: suspending, March keeps one day.
    return AbsenceEvent(
        date(2026, 3, 2),
        Decimal(173),
        Decimal("11.86"),
        end_date=date(2026, 3, 31),
        suspends_accrual=suspends_accrual,
    )


def _year_with_leave(suspends_accrual: bool | None) -> CompetenceYearPlan:
    return competence_year(
        periods={3: replace(FACTS, events=(_leave(suspends_accrual),))}
    )


def _imported(inps_base: InpsBaseYtd) -> PeriodState:
    return PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            inps_bases=(inps_base,),
            recoveries=(),
            surtax_obligations=(),
        )
    )


#: Hired on 1 January 2025 and out on 31 January 2026, with the TFR fund
#: at 31 December 2025 stated in full: the January run settles the TFR.
_LEAVING = replace(
    _SINCE_2025,
    employment_period=EmploymentPeriod(date(2025, 1, 1), date(2026, 1, 31)),
    tfr_fund=TfrFundBalance(2025, Decimal(2_000), Decimal(0), Decimal(0)),
)


def _vertical_leave(paid_days: int | None) -> PeriodInput:
    """Return an extraordinary leave of a vertical part time, three days a week.

    Returns:
        The January run; the indemnity divides by the paid days when stated.
    """
    days = (Decimal(8),) * 3 + (Decimal(0),) * 4
    employment = replace(
        CONCIA_D2,
        weekly_hours=WeeklyHours(Decimal(24)),
        work_pattern=WorkPattern(weekday_hours=days),
    )
    leave = ExtraordinaryLeaveEvent(
        date(2026, 1, 12),
        date(2026, 1, 23),
        Decimal(1300),
        last_month_paid_days=paid_days,
    )
    return _january(employment, events=(leave,))


def _farm_sickness(days: AgriculturalDays | None) -> PeriodInput:
    """Return a sickness of an operaio agricolo a tempo determinato.

    Returns:
        The January run; INPS pays it within the elenchi days when stated.
    """
    employment = replace(
        CONCIA_D2,
        ccnl_id="operai-agricoli-florovivaisti",
        level_code="Area1",
        category=WorkerCategory.OPERAIO,
        contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
    )
    episode = SicknessEpisode(
        "AG", date(2026, 1, 12), date(2026, 1, 16), agricultural_days=days
    )
    return _january(employment, events=(episode,))


def _ending(case: NaspiCase | None) -> Employment:
    """Return a dismissal on 31 January 2026, with or without its NASpI case.

    Returns:
        The employment of :data:`_SINCE_2025` ending by dismissal.
    """
    period = EmploymentPeriod(
        date(2025, 1, 1), date(2026, 1, 31), TerminationCause.DISMISSAL, False, case
    )
    return replace(_SINCE_2025, employment_period=period)


def _leaving(
    employment: Employment = _LEAVING, opening: PeriodState | None = None
) -> PeriodInput:
    """Return the January run that settles the TFR of :data:`_LEAVING`.

    Returns:
        The request, opened with ``opening`` or the zero state.
    """
    return regular_run(
        1,
        employment=employment,
        events=(TerminationTFREvent(date(2026, 1, 31)),),
        opening_state=PeriodState.zero() if opening is None else opening,
    )


def _imported_quotas(quotas: tuple[TfrQuotaYtd, ...] | None) -> PeriodState:
    return PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            inps_bases=(InpsBaseYtd(2026, Decimal(0), Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
            tfr_quotas=quotas,
        )
    )


def _fund_case(fund: TfrFundBalance, names: str) -> DefaultCase:
    return DefaultCase(_leaving(), _leaving(replace(_LEAVING, tfr_fund=fund)), names)


def _since_2025_january(opening: PeriodState) -> PeriodInput:
    request = regular_run(1, employment=_SINCE_2025, opening_state=opening)
    return replace(request, current_year=None)


def _tax_year(
    opening_state: PeriodState | None = None,
    current_year: CurrentYearTaxFacts | None = None,
    employment: Employment = _SINCE_2025,
) -> TaxYearPlan:
    plan = replace(competence_year(employment=employment), current_year=None)
    return TaxYearPlan(
        tax_year=2026,
        competence_years=(plan,),
        opening_state=opening_state,
        current_year=current_year,
    )


def _turismo_young(birth: date | None) -> PeriodInput:
    """Return a Turismo run of a worker whose increments count from age 18.

    Returns:
        The January request with the birth date stated or not.
    """
    request = _january(
        replace(CONCIA_D2, ccnl_id="turismo-federalberghi", level_code="4")
    )
    seniority = request.employment.seniority
    assert seniority is not None
    employment = replace(
        request.employment, seniority=replace(seniority, birth_date=birth)
    )
    return replace(request, employment=employment)


def _pharmacist(career: int | None) -> PeriodInput:
    """Return a Farmacie Q3 run whose ISQ follows the career in Area Q.

    Returns:
        The January request with the career months stated or not.
    """
    request = _january(
        replace(CONCIA_D2, ccnl_id="farmacie-private-h121", level_code="Q3")
    )
    seniority = request.employment.seniority
    assert seniority is not None
    employment = replace(
        request.employment, seniority=replace(seniority, career_months=career)
    )
    return replace(request, employment=employment)


def _on_probation(until: date | None) -> PeriodInput:
    """Return a March Igiene ambientale run whose FASDA skips the probation.

    Returns:
        The request with the end of the probation stated or not.
    """
    employment = replace(
        CONCIA_D2, ccnl_id="igiene-ambientale-utilitalia", level_code="C1"
    )
    period = employment.employment_period
    assert period is not None
    employment = replace(
        employment, employment_period=replace(period, probation_until=until)
    )
    return regular_run(
        3, employment=employment, facts=FACTS, opening_state=PeriodState.zero()
    )


#: The cases of each ``requires_fact`` field, keyed ``Type.field``.
class _FractionalCreditRepository(BundledKnowledgeRepository):
    """Serve the verified share in memory without editing production knowledge."""

    def load_ccnl(self, ccnl_id: str) -> CCNL:
        """Return the unchanged agreement except for the tested credit rule.

        Returns:
            The agreement with an in-memory fractional-credit rule.
        """
        ccnl = load_ccnl(ccnl_id)
        if ccnl_id != "metalmeccanico-confapi":
            return ccnl
        rules = ccnl.parameters.seniority_increments.model_copy(
            update={"apprenticeship_credit_share": Decimal("0.65")}
        )
        return ccnl.model_copy(
            update={
                "parameters": ccnl.parameters.model_copy(
                    update={"seniority_increments": rules}
                )
            }
        )


def _apprenticeship_credit(duration: int | None) -> PeriodInput:
    """Return a retained worker with stated or unknown past apprenticeship.

    Returns:
        The January run of the retained worker.
    """
    seniority = SeniorityFact(
        months=0,
        as_of=date(2026, 1, 1),
        source=SenioritySource.EMPLOYER_RECORDS,
        apprenticeship_months=duration,
    )
    employment = replace(
        CONCIA_D2,
        ccnl_id="metalmeccanico-confapi",
        level_code="2",
        category=None,
        seniority=seniority,
        employment_period=EmploymentPeriod(date(2026, 1, 1)),
    )
    return _january(employment)


DEFAULT_CASES: Mapping[str, tuple[DefaultCase, ...]] = {
    "Employment.prior_extra_month_amount": (
        DefaultCase(
            _studi_fourteenth(Decimal(400)),
            _studi_fourteenth(None),
            "prior_extra_month_amount",
        ),
    ),
    "PeriodInput.current_year": (
        DefaultCase(
            _january(_PART_TIME),
            replace(_january(_PART_TIME), current_year=None),
            "current_year",
        ),
    ),
    "PeriodInput.opening_state": (
        DefaultCase(
            regular_run(1, employment=_SINCE_2025, opening_state=fresh_tax_year()),
            regular_run(1, employment=_SINCE_2025),
            "opening_state",
        ),
    ),
    "CompetenceYearPlan.current_year": (
        DefaultCase(
            competence_year(employment=_PART_TIME),
            replace(competence_year(employment=_PART_TIME), current_year=None),
            "current_year",
        ),
    ),
    "CompetenceYearPlan.opening_state": (
        DefaultCase(
            replace(
                competence_year(employment=_SINCE_2025),
                opening_state=fresh_tax_year(),
            ),
            competence_year(employment=_SINCE_2025),
            "opening_state",
        ),
    ),
    "TaxYearPlan.opening_state": (
        DefaultCase(
            _tax_year(opening_state=fresh_tax_year(), current_year=_CURRENT),
            _tax_year(current_year=_CURRENT),
            "opening_state",
        ),
    ),
    "TaxYearPlan.current_year": (
        DefaultCase(
            _tax_year(fresh_tax_year(), _CURRENT, _PART_TIME_SINCE_2025),
            _tax_year(fresh_tax_year(), None, _PART_TIME_SINCE_2025),
            "current_year",
        ),
    ),
    "EmployerProfile.activity": (
        DefaultCase(
            _night_shift(EMPLOYER),
            _night_shift(replace(EMPLOYER, activity=None)),
            "activity",
        ),
    ),
    "Employment.category": (_employment_pair(CONCIA_D2, _UNCATEGORISED, "category"),),
    "Employment.employment_period": (
        # Hired on the first of a month: Concia's quota of 1/25 leaves the
        # payable days of a partly employed month undefined, so a hire in
        # mid-month is not computed at all.
        DefaultCase(
            competence_year(
                employment=replace(
                    CONCIA_D2, employment_period=EmploymentPeriod(date(2026, 6, 1))
                )
            ),
            replace(
                competence_year(employment=replace(CONCIA_D2, employment_period=None)),
                opening_state=fresh_tax_year(),
            ),
        ),
    ),
    "Employment.weekly_hours": (
        _employment_pair(
            _PART_TIME,
            replace(CONCIA_D2, weekly_hours=None, full_time_weekly_hours=None),
        ),
    ),
    "Employment.full_time_weekly_hours": (
        _employment_pair(
            _PART_TIME,
            replace(_PART_TIME, full_time_weekly_hours=None),
            "full_time_weekly_hours",
        ),
    ),
    "Employment.seniority": (
        _employment_pair(CONCIA_D2, replace(CONCIA_D2, seniority=None), "seniority"),
    ),
    "Employment.holiday_company_offset": (
        _employment_pair(
            _CONFAPI_HOLIDAYS,
            replace(_CONFAPI_HOLIDAYS, holiday_company_offset=None),
            "holiday_company_offset",
        ),
    ),
    "Employment.qualifying_shifts": (
        _employment_pair(
            replace(_CONFAPI_HOLIDAYS, qualifying_shifts=False),
            _CONFAPI_HOLIDAYS,
        ),
    ),
    "Employment.roles": (
        _employment_pair(
            replace(_ALIMENTARI_1S, roles=frozenset({"quadro"})),
            _ALIMENTARI_1S,
            "roles",
        ),
        _employment_pair(
            replace(_ALIMENTARI_1S, roles=frozenset()), _ALIMENTARI_1S, "roles"
        ),
    ),
    "Employment.contribution_history": (
        DefaultCase(
            _january(events=(_LARGE_BONUS,)),
            _january(
                replace(CONCIA_D2, contribution_history=None), events=(_LARGE_BONUS,)
            ),
            "contribution_history",
        ),
    ),
    "Employment.sector": (
        DefaultCase(
            replace(
                _january(events=(_renewal(),)),
                prior_year=_ELIGIBLE_PRIOR,
            ),
            replace(
                _january(replace(CONCIA_D2, sector=None), events=(_renewal(),)),
                prior_year=_ELIGIBLE_PRIOR,
            ),
            "sector",
        ),
    ),
    "Employment.tfr_fund": (
        DefaultCase(
            replace(
                competence_year(
                    employment=replace(
                        _SINCE_2025, tfr_fund=TfrFundBalance(2025, Decimal(2_000))
                    )
                ),
                opening_state=fresh_tax_year(),
            ),
            replace(
                competence_year(employment=_SINCE_2025),
                opening_state=fresh_tax_year(),
            ),
            "tfr_fund",
        ),
    ),
    "TfrFundBalance.revaluations": (
        _fund_case(
            TfrFundBalance(2025, Decimal(2_000), advances=Decimal(0)), "revaluations"
        ),
    ),
    "TfrFundBalance.advances": (
        _fund_case(
            TfrFundBalance(2025, Decimal(2_000), revaluations=Decimal(0)), "advances"
        ),
    ),
    "TfrFundBalance.advances_taxable": (
        _fund_case(
            TfrFundBalance(
                2025,
                Decimal(2_000),
                Decimal(0),
                Decimal(500),
                advances_tax=Decimal(115),
            ),
            "advances_taxable",
        ),
    ),
    "TfrFundBalance.advances_tax": (
        _fund_case(
            TfrFundBalance(
                2025,
                Decimal(2_000),
                Decimal(0),
                Decimal(500),
                advances_taxable=Decimal(500),
            ),
            "advances_taxable",
        ),
    ),
    "OpeningBalances.tfr_quotas": (
        DefaultCase(
            _leaving(opening=_imported_quotas(())),
            _leaving(opening=_imported_quotas(None)),
            "tfr_quotas",
        ),
    ),
    "Employment.tfr_treasury_fund": (
        _employment_pair(
            CONCIA_D2,
            replace(CONCIA_D2, tfr_treasury_fund=None),
            "tfr_treasury_fund",
        ),
    ),
    "Employment.pension_fund": (
        _employment_pair(
            replace(_TABACCO_3A, pension_fund=_ALIFOND), _TABACCO_3A, "pension_fund"
        ),
        _employment_pair(
            replace(_TABACCO_3A, pension_fund=NoPensionFund()),
            _TABACCO_3A,
            "pension_fund",
        ),
        _employment_pair(
            CONCIA_D2, replace(CONCIA_D2, pension_fund=None), "pension_fund"
        ),
    ),
    "PeriodFacts.meal_benefit_days": (
        DefaultCase(
            replace(
                _january(
                    replace(
                        CONCIA_D2,
                        ccnl_id="ced-assoced",
                        level_code="4",
                        category=WorkerCategory.IMPIEGATO,
                    )
                ),
                facts=replace(FACTS, meal_benefit_days=0),
            ),
            _january(
                replace(
                    CONCIA_D2,
                    ccnl_id="ced-assoced",
                    level_code="4",
                    category=WorkerCategory.IMPIEGATO,
                )
            ),
            "meal_benefit_days",
        ),
    ),
    "PeriodFacts.regione": (
        DefaultCase(
            _january(),
            replace(_january(), facts=replace(FACTS, regione=None)),
            "facts.regione",
        ),
    ),
    "PeriodFacts.comune_belfiore": (
        DefaultCase(
            _january(),
            replace(_january(), facts=replace(FACTS, comune_belfiore=None)),
            "facts.comune_belfiore",
        ),
    ),
    "PeriodFacts.family_composition": (
        DefaultCase(
            _january(),
            replace(_january(), facts=replace(FACTS, family_composition=None)),
            "facts.family_composition",
        ),
    ),
    "Dependent.own_income": (_dependent_pair("own_income", _SPOUSE),),
    "Dependent.allocation_pct": (_dependent_pair("allocation_pct", _CHILD),),
    "Dependent.cohabiting": (_dependent_pair("cohabiting", _ASCENDANT),),
    "Dependent.residency_eligibility": (
        _dependent_pair("residency_eligibility", _SPOUSE),
    ),
    "InpsBaseYtd.other_employers": (
        DefaultCase(
            _since_2025_january(_imported(InpsBaseYtd(2026, Decimal(0), Decimal(0)))),
            _since_2025_january(_imported(InpsBaseYtd(2026, Decimal(0)))),
            "other_employers",
        ),
    ),
    "InpsBaseYtd.other_employers_additional_ivs": (
        DefaultCase(
            _since_2025_january(
                _imported(
                    InpsBaseYtd(
                        2026,
                        Decimal(0),
                        Decimal(0),
                        other_employers_additional_ivs=Decimal(0),
                    )
                )
            ),
            _since_2025_january(_imported(InpsBaseYtd(2026, Decimal(0), Decimal(0)))),
        ),
    ),
    "PriorYearTaxFacts.employment_income": (
        DefaultCase(
            replace(_january(events=(_renewal(),)), prior_year=_ELIGIBLE_PRIOR),
            replace(_january(events=(_renewal(),)), prior_year=PriorYearTaxFacts()),
            "employment_income",
        ),
    ),
    "AbsenceEvent.suspends_accrual": (
        DefaultCase(_year_with_leave(True), _year_with_leave(None), "suspends_accrual"),
        DefaultCase(
            _year_with_leave(False), _year_with_leave(None), "suspends_accrual"
        ),
    ),
    "ExtraordinaryLeaveEvent.last_month_paid_days": (
        DefaultCase(_vertical_leave(13), _vertical_leave(None), "last_month_paid_days"),
    ),
    "EmploymentPeriod.naspi_case": (
        _employment_pair(_ending(NaspiCase.ORDINARY), _ending(None), "naspi_case"),
    ),
    "SicknessEpisode.agricultural_days": (
        DefaultCase(
            _farm_sickness(AgriculturalDays(100, 0)),
            _farm_sickness(None),
            "agricultural_days",
        ),
    ),
    "ArrearsEvent.unused_deductions": (
        _event_pair(replace(_unrated(), unused_deductions=Decimal(40)), _unrated()),
    ),
    "ArrearsEvent.reference_period": (
        _event_pair(_arrears(PeriodId(2025, 6)), _arrears(None), "reference_period"),
    ),
    "PriorYearTaxFacts.net_income_biennio": (
        DefaultCase(
            replace(
                _january(events=(_unrated(),)),
                prior_year=replace(
                    _january().prior_year,
                    net_income_biennio=(Decimal(30_000), Decimal(32_000)),
                ),
            ),
            _january(events=(_unrated(),)),
            "net_income_biennio",
        ),
    ),
    "BonusEvent.agreement_signed_on": (
        _event_pair(_renewal(), _renewal(None), "agreement_signed_on"),
    ),
    "SeniorityFact.apprenticeship_months": (
        DefaultCase(
            _apprenticeship_credit(36),
            _apprenticeship_credit(None),
            "apprenticeship_months",
            PayrollEngine(repository=_FractionalCreditRepository()),
        ),
    ),
    "SeniorityFact.birth_date": tuple(
        DefaultCase(_turismo_young(birth), _turismo_young(None))
        for birth in (date(1990, 4, 2), date(2009, 4, 2))
    ),
    "EmploymentPeriod.probation_until": tuple(
        DefaultCase(_on_probation(until), _on_probation(None))
        for until in (date(2026, 2, 28), date(2026, 3, 31))
    ),
    "SeniorityFact.career_months": tuple(
        DefaultCase(_pharmacist(career), _pharmacist(None)) for career in (0, 200)
    ),
    **absence_cases(_event_pair),
    **fixed_term_cases(_employment_pair),
    **pension_cases(_employment_pair, _january, DefaultCase),
    **employer_cases(_january, DefaultCase),
    **sickness_cases(DefaultCase),
}
