"""Pairs of requests: a defaulted public field stated, and left to its default.

Every ``requires_fact`` field of :mod:`ccnl_engine.payroll.domain.input_defaults`
has a :class:`DefaultCase` in :data:`DEFAULT_CASES` or a reason in
:data:`NOT_EXERCISED`, as ``tests/architecture/test_input_defaults.py`` checks.
Each case is the explicit Concia D2 of 2026 (:mod:`tests.fixtures.explicit_facts`)
with one field changed: ``true`` states the fact, ``default`` leaves the field
to its default; ``tests/acceptance/public_api/test_default_facts.py`` runs both.
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
    PeriodInput,
    TaxYearPlan,
)
from ccnl_engine.events import (
    AbsenceEvent,
    ArrearsEvent,
    BonusEvent,
    NightShiftEvent,
    PeriodId,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    Dependent,
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    InpsBaseYtd,
    NoPensionFund,
    OpeningBalances,
    PensionFundEnrolment,
    PeriodState,
    PriorYearTaxFacts,
    TfrFundBalance,
    WeeklyHours,
)
from tests.fixtures.default_cases_absence import absence_cases
from tests.fixtures.default_cases_fixed_term import fixed_term_cases
from tests.fixtures.default_cases_pension import pension_cases
from tests.fixtures.default_cases_sickness import sickness_cases
from tests.fixtures.dependents import declared_dependent
from tests.fixtures.explicit_facts import (
    CONCIA_D2,
    EMPLOYER,
    FACTS,
    competence_year,
    regular_run,
)
from tests.fixtures.opening_state import fresh_tax_year

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.events import WorkEvent

__all__ = [
    "DEFAULT_CASES",
    "NAMES_NOT_SHOWN",
    "NOT_EXERCISED",
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
    """

    true: Request
    default: Request
    names: str | None = None


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
_PART_TIME = replace(CONCIA_D2, weekly_hours=WeeklyHours(20))
#: Hired on 1 January 2025: a run of 2026 needs the history of 2025.
_SINCE_2025 = replace(CONCIA_D2, employment_period=EmploymentPeriod(date(2025, 1, 1)))
_PART_TIME_SINCE_2025 = replace(_SINCE_2025, weekly_hours=WeeklyHours(20))
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
    _UNCATEGORISED, ccnl_slug="tabacco-apti.json", level_code="3A", pension_fund=None
)
_ALIFOND = PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=False)
#: Alimentari 1S, a quadro level paying the IND_FUNZIONE_QUADRO allowance
#: to the holders of the role ``quadro``.
_ALIMENTARI_1S = replace(
    _UNCATEGORISED, ccnl_slug="alimentari-federalimentare.json", level_code="1S"
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


#: The cases of each ``requires_fact`` field, keyed ``Type.field``.
DEFAULT_CASES: Mapping[str, tuple[DefaultCase, ...]] = {
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
    "Employment.category": (
        _employment_pair(CONCIA_D2, _UNCATEGORISED, "employer_rate_category_assumed"),
    ),
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
    "ArrearsEvent.reference_period": (
        _event_pair(_arrears(PeriodId(2025, 6)), _arrears(None), "reference_period"),
    ),
    "BonusEvent.agreement_signed_on": (
        _event_pair(_renewal(), _renewal(None), "agreement_signed_on"),
    ),
    **absence_cases(_event_pair),
    **fixed_term_cases(_employment_pair),
    **pension_cases(_employment_pair, _january, DefaultCase),
    **sickness_cases(DefaultCase),
}

#: ``requires_fact`` fields without a case, and why.
NOT_EXERCISED: Mapping[str, str] = {
    "PeriodFacts.contributable_hours": (
        "a domestic CCNL raises MissingRequiredFactError without it: the "
        "default yields no result to compare; other CCNLs do not read it"
    ),
    "Apprentice.track": (
        "a level with several tracks raises InvalidInputError without it, and "
        "the unique track of a level is the fact: no result to compare"
    ),
    "Dependent.birth_date": (
        "a child without it raises InvalidInputError, and no other dependant "
        "reads it: no result to compare"
    ),
}


#: ``reported`` or ``requirement`` fields whose cases show no blocker naming
#: the fact, and why.
NAMES_NOT_SHOWN: Mapping[str, str] = {
    "InpsBaseYtd.other_employers_additional_ivs": (
        "read by the December run settling the additional 1% IVS with a base "
        "of other employers; test_opening_balances_import shows its blocker"
    ),
}
