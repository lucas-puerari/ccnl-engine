"""Default cases of fixed-term, pension fund and multi-episode sickness facts."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.employment.period.inputs import TerminationCause
from ccnl_engine.events import (
    ExtraordinaryLeaveEvent,
    HourlyParentalLeaveEvent,
    InpsSicknessBase,
    LeaveHours,
    MaternityLeaveEvent,
    NoticeIndemnityEvent,
    OvertimeEvent,
    ParentalLeaveEvent,
    ParentalLeaveTaken,
    PaternityLeaveEvent,
    SicknessEpisode,
)
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    EmploymentSector,
    FixedTerm,
    InpsBaseYtd,
    NaspiExclusion,
    NoPensionFund,
    OpeningBalances,
    PensionFundEnrolment,
    PeriodState,
    Permanent,
    PublicEndOfService,
    TaxSector,
    WorkerCategory,
)
from tests.integration.ccnl_engine.withholding.builders import paid_before
from tests.knowledge.ccnl_engine.period.builders import CONCIA_D2
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


__all__ = ["fixed_term_cases"]

#: A first fixed-term contract with no exclusion of L. 92/2012 art. 2 c. 29.
_FIXED_TERM = FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE)


def fixed_term_cases[C](
    pair: Callable[[Employment, Employment, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the fixed-term facts, built with ``pair``.

    Returns:
        The cases keyed ``Type.field``.
    """
    stated = replace(CONCIA_D2, contract_type=_FIXED_TERM)
    return {
        "FixedTerm.renewals": (
            pair(
                stated,
                replace(
                    CONCIA_D2,
                    contract_type=FixedTerm(naspi_exclusion=NaspiExclusion.NONE),
                ),
                "renewals",
            ),
        ),
        "FixedTerm.naspi_exclusion": (
            pair(
                stated,
                replace(CONCIA_D2, contract_type=FixedTerm(renewals=0)),
                "naspi_exclusion",
            ),
        ),
    }


__all__ = ["pension_cases"]


def _cometa(young_member: bool | None) -> Employment:
    enrolment = PensionFundEnrolment(
        "COMETA", Decimal("0.012"), tfr_to_fund=True, young_member=young_member
    )
    return replace(
        CONCIA_D2,
        category=None,
        ccnl_id="metalmeccanico-federmeccanica",
        level_code="C3",
        pension_fund=enrolment,
    )


def _byblos(erc_amount: Decimal | None) -> Employment:
    return replace(
        CONCIA_D2,
        category=None,
        ccnl_id="grafica-editoria-aieg",
        level_code="C1",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2019, 1, 1)),
        pension_fund=PensionFundEnrolment("BYBLOS", Decimal("0.01"), tfr_to_fund=True),
        erc_amount=erc_amount,
    )


def _previambiente(
    january: Callable[[Employment], PeriodInput], base: Decimal | None
) -> PeriodInput:
    """Return the March run: the CCNL tables start on 1 February 2026.

    Returns:
        The request of the March regular run.
    """
    enrolment = PensionFundEnrolment(
        "PREVIAMBIENTE", Decimal("0.013"), tfr_to_fund=True, conventional_base=base
    )
    employment = replace(
        CONCIA_D2,
        category=None,
        ccnl_id="igiene-ambientale-utilitalia",
        level_code="Q",
        pension_fund=enrolment,
    )
    request = january(employment)
    return replace(
        request, run=PayrollRun.regular(2026, 3), payment_date=date(2026, 3, 27)
    )


def _public(regime: PublicEndOfService | None) -> Employment:
    return replace(
        CONCIA_D2,
        category=None,
        ccnl_id="funzioni-centrali-aran",
        level_code="FUNZIONARI",
        sector=EmploymentSector.PUBLIC,
        public_end_of_service=regime,
    )


def _public_employer(
    january: Callable[[Employment], PeriodInput], insured: bool | None
) -> PeriodInput:
    request = january(_public(PublicEndOfService.TFS))
    employer = replace(request.employer, public_life_insurance=insured)
    return replace(request, employer=employer)


def _small_terziario(
    january: Callable[[Employment], PeriodInput], reduced: bool | None
) -> PeriodInput:
    terziario = replace(
        CONCIA_D2,
        category=None,
        ccnl_id="commercio-confcommercio",
        level_code="5",
    )
    request = january(terziario)
    employer = replace(request.employer, headcount=Headcount(5), fis_reduction=reduced)
    return replace(request, employer=employer)


def _craft_firm(
    january: Callable[[Employment], PeriodInput], indotto: bool | None
) -> PeriodInput:
    """Return a run of a metalworking craft firm of 20 employees.

    Returns:
        The January run, the indotto given.
    """
    craft = replace(CONCIA_D2, ccnl_id="metalmeccanico-artigianato", level_code="3")
    request = january(craft)
    employer = replace(request.employer, headcount=Headcount(20), cigs_indotto=indotto)
    return replace(request, employer=employer)


def _commercio_employer(
    january: Callable[[Employment], PeriodInput], in_force: bool | None
) -> PeriodInput:
    """Return a Commercio run whose level pays the terzo elemento nazionale.

    Returns:
        The January request with ``provincial_pay_element`` set to ``in_force``.
    """
    commercio = replace(
        CONCIA_D2,
        category=None,
        ccnl_id="commercio-confcommercio",
        level_code="4",
    )
    request = january(commercio)
    employer = replace(request.employer, provincial_pay_element=in_force)
    return replace(request, employer=employer)


def _unionalimentari_employer(
    january: Callable[[Employment], PeriodInput], premium: bool | None
) -> PeriodInput:
    """Return an Unionalimentari run whose level pays the EGR.

    Returns:
        The January request with ``second_level_premium`` set to ``premium``.
    """
    alimentari = replace(
        CONCIA_D2,
        category=None,
        ccnl_id="alimentari-pmi-unionalimentari",
        level_code="4",
    )
    request = january(alimentari)
    employer = replace(request.employer, second_level_premium=premium)
    return replace(request, employer=employer)


def _alimentari_employer(
    january: Callable[[Employment], PeriodInput], subsector: str | None
) -> PeriodInput:
    """Return an Alimentari run with overtime priced by the sub-sector bands.

    Returns:
        The January request with ``subsector`` stated or not.
    """
    alimentari = replace(
        CONCIA_D2,
        category=WorkerCategory.OPERAIO,
        ccnl_id="alimentari-federalimentare",
        level_code="4",
    )
    request = january(alimentari)
    employer = replace(request.employer, subsector=subsector)
    overtime = OvertimeEvent(
        event_date=date(2026, 1, 14), hours=Decimal(2), hourly_rate=Decimal(12)
    )
    facts = replace(request.facts, events=(overtime,))
    return replace(request, employer=employer, facts=facts)


def _logistica_employer(
    january: Callable[[Employment], PeriodInput], sector: TaxSector | None
) -> PeriodInput:
    """Return a Logistica run, a CCNL of the industria and of the terziario.

    Returns:
        The January request with ``inps_sector`` set to ``sector``.
    """
    logistica = replace(
        CONCIA_D2,
        ccnl_id="logistica-trasporto-confetra",
        level_code="3S",
    )
    request = january(logistica)
    employer = replace(request.employer, inps_sector=sector)
    return replace(request, employer=employer)


def _operaio(
    january: Callable[[Employment], PeriodInput], hours: Decimal | None
) -> PeriodInput:
    employment = replace(
        CONCIA_D2,
        ccnl_id="edilizia-ance",
        level_code="2",
        category=WorkerCategory.OPERAIO,
        pension_fund=NoPensionFund(),
    )
    request = january(employment)
    worked = None if hours is None else ContributableHours(hours)
    return replace(request, facts=replace(request.facts, ordinary_hours_worked=worked))


def pension_cases[C](
    pair: Callable[[Employment, Employment, str], C],
    january: Callable[[Employment], PeriodInput],
    case: Callable[[PeriodInput, PeriodInput, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the enrolment and hours facts.

    Returns:
        The cases keyed ``Type.field``.
    """
    return {
        "PeriodFacts.ordinary_hours_worked": (
            case(
                _operaio(january, Decimal(160)),
                _operaio(january, None),
                "ordinary_hours_worked",
            ),
        ),
        "Employment.erc_amount": (
            pair(_byblos(Decimal("412.50")), _byblos(None), "erc_amount"),
            pair(_byblos(Decimal(0)), _byblos(None), "erc_amount"),
        ),
        "PensionFundEnrolment.conventional_base": (
            case(
                _previambiente(january, Decimal("2077.84")),
                _previambiente(january, None),
                "conventional_base",
            ),
        ),
        "Employment.public_end_of_service": (
            pair(
                _public(PublicEndOfService.TFS), _public(None), "public_end_of_service"
            ),
        ),
        "EmployerProfile.cigs_indotto": (
            case(
                _craft_firm(january, True), _craft_firm(january, None), "cigs_indotto"
            ),
            case(
                _craft_firm(january, False), _craft_firm(january, None), "cigs_indotto"
            ),
        ),
        "EmployerProfile.fis_reduction": (
            case(
                _small_terziario(january, True),
                _small_terziario(january, None),
                "fis_reduction",
            ),
            case(
                _small_terziario(january, False),
                _small_terziario(january, None),
                "fis_reduction",
            ),
        ),
        "EmployerProfile.public_life_insurance": (
            case(
                _public_employer(january, True),
                _public_employer(january, None),
                "public_life_insurance",
            ),
            case(
                _public_employer(january, False),
                _public_employer(january, None),
                "public_life_insurance",
            ),
        ),
        "PensionFundEnrolment.young_member": (
            pair(_cometa(True), _cometa(None), "young_member"),
            pair(_cometa(False), _cometa(None), "young_member"),
        ),
    }


def employer_cases[C](
    january: Callable[[Employment], PeriodInput],
    case: Callable[[PeriodInput, PeriodInput, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the employer facts a CCNL level reads.

    Returns:
        The cases keyed ``Type.field``.
    """
    return {
        "EmployerProfile.provincial_pay_element": tuple(
            case(
                _commercio_employer(january, stated),
                _commercio_employer(january, None),
                "provincial_pay_element",
            )
            for stated in (False, True)
        ),
        "EmployerProfile.second_level_premium": tuple(
            case(
                _unionalimentari_employer(january, stated),
                _unionalimentari_employer(january, None),
                "second_level_premium",
            )
            for stated in (False, True)
        ),
        "EmployerProfile.subsector": tuple(
            case(
                _alimentari_employer(january, stated),
                _alimentari_employer(january, None),
                "subsector",
            )
            for stated in ("carni", "vini_liquori")
        ),
        "EmployerProfile.inps_sector": tuple(
            case(
                _logistica_employer(january, sector),
                _logistica_employer(january, None),
                "inps_sector",
            )
            for sector in (TaxSector.INDUSTRIA, TaxSector.TERZIARIO)
        ),
    }


__all__ = ["sickness_cases"]

_EMPLOYMENT = Employment(
    contract_type=Permanent(),
    ccnl_id="metalmeccanico-federmeccanica",
    level_code="C3",
    category=WorkerCategory.OPERAIO,
    seniority=new_hire(2025),
)


def _march(opening: PeriodState, *episodes: SicknessEpisode) -> PeriodInput:
    return PeriodInput(
        run=PayrollRun.regular(2026, 3),
        payment_date=date(2026, 3, 27),
        employment=_EMPLOYMENT,
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(events=episodes),
        opening_state=opening,
    )


def _short_absences(fourth_exempt: bool | None) -> PeriodInput:
    """Return four two-day absences of March 2026, the fourth's exemption given.

    Returns:
        The March run; the fourth absence of at most five days is reduced
        unless exempt.
    """
    episodes = tuple(
        SicknessEpisode(
            f"S{day}",
            date(2026, 3, day),
            date(2026, 3, day + 1),
            short_absence_exempt=False if day < 23 else fourth_exempt,
        )
        for day in (2, 9, 16, 23)
    )
    return _march(PeriodState.zero(), *episodes)


def _sickness_import(known_from: date | None) -> PeriodInput:
    """Return March 2026 after an import of January and February.

    The worker was hired before 2026: without ``known_from`` the sickness
    of the three previous years is unknown.

    Returns:
        The March run with a twelve-day episode.
    """
    opening = PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(PayrollRun.regular(2026, 3)),
            sickness_known_from=known_from,
            inps_bases=(InpsBaseYtd(2026, other_employers=Decimal(0)),),
            recoveries=(),
            surtax_obligations=(),
        )
    )
    episode = SicknessEpisode("M", date(2026, 3, 2), date(2026, 3, 13))
    return _march(opening, episode)


def _long_sickness(stays: tuple[tuple[date, date], ...] | None) -> PeriodInput:
    """Return March 2026 of an episode past the 122 full-pay days of C3.

    The episode starts on 1 November 2025: from 3 March the days are paid
    at 80%, which a hospital stay could change.

    Returns:
        The March run, the stays given.
    """
    episode = SicknessEpisode(
        "LONG", date(2025, 11, 1), date(2026, 3, 20), hospital_stays=stays
    )
    return _march(PeriodState.zero(), episode)


def _logistica_long(*, serious: bool | None) -> PeriodInput:
    """Return March 2026 of a Logistica episode past its 90 full-pay days.

    Returns:
        The March run of a level 3 worker sick since 1 November 2025.
    """
    episode = SicknessEpisode(
        "LOG", date(2025, 11, 1), date(2026, 3, 20), serious_illness=serious
    )
    run = _march(PeriodState.zero(), episode)
    employment = replace(
        _EMPLOYMENT, ccnl_id="logistica-trasporto-confetra", level_code="3"
    )
    return replace(run, employment=employment)


def _cinema_sickness(contributions: int | None) -> PeriodInput:
    """Return a ten-day episode of a film production impiegato.

    Returns:
        The March run, the daily contributions given.
    """
    episode = SicknessEpisode(
        "CIN", date(2026, 3, 2), date(2026, 3, 11), daily_contributions=contributions
    )
    run = _march(PeriodState.zero(), episode)
    employment = replace(
        _EMPLOYMENT,
        ccnl_id="cinema-audiovisivi-industria",
        level_code="4",
        category=WorkerCategory.IMPIEGATO,
    )
    return replace(run, employment=employment)


def _fixed_term_sickness(worked: int | None) -> PeriodInput:
    """Return a five-day episode of a fixed-term worker, its days of work given.

    Returns:
        The March run; with 200 days of work before it the limit of D.L.
        463/1983 art. 5 leaves every day paid.
    """
    episode = SicknessEpisode(
        "FT", date(2026, 3, 9), date(2026, 3, 13), prior_worked_days=worked
    )
    run = _march(PeriodState.zero(), episode)
    employment = replace(
        _EMPLOYMENT,
        contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
    )
    return replace(run, employment=employment)


def _inps_base_sickness(base: InpsSicknessBase | None) -> PeriodInput:
    """Return a five-day episode of an operaio, the pay of February given.

    Returns:
        The March run; the INPS share needs the pay of the month before.
    """
    episode = SicknessEpisode("IB", date(2026, 3, 9), date(2026, 3, 13), inps_base=base)
    return _march(PeriodState.zero(), episode)


def _maternity(base: InpsSicknessBase | None) -> PeriodInput:
    """Return a March maternity leave of an impiegata, the February pay given.

    Returns:
        The March run; the indemnity needs the pay of the month before.
    """
    leave = MaternityLeaveEvent(
        date(2026, 3, 2), date(2026, 3, 31), maternity_base_pay=base
    )
    run = _march(PeriodState.zero())
    employment = replace(_EMPLOYMENT, category=WorkerCategory.IMPIEGATO)
    return replace(run, employment=employment, facts=PeriodFacts(events=(leave,)))


def _paternity(base: InpsSicknessBase | None) -> PeriodInput:
    """Return ten days of paternity leave in March of an impiegato.

    Returns:
        The March run; the indemnity needs the pay of the month before.
    """
    days = tuple(date(2026, 3, d) for d in (2, 3, 4, 5, 6, 9, 10, 11, 12, 13))
    leave = PaternityLeaveEvent(days, paternity_base_pay=base)
    run = _march(PeriodState.zero())
    employment = replace(_EMPLOYMENT, category=WorkerCategory.IMPIEGATO)
    return replace(run, employment=employment, facts=PeriodFacts(events=(leave,)))


_FEBRUARY_PAY = InpsSicknessBase(Decimal("2158.26"), Decimal(0))
_MATERNITY_END = date(2023, 1, 1)


def _parental(base: InpsSicknessBase | None, ended: date | None) -> PeriodInput:
    """Return two weeks of parental leave in March of an impiegato.

    The child was born on 1 October 2022: only a maternity leave ended in
    2023 gives a month at 80%.

    Returns:
        The March run; the indemnity needs the pay of the month before and
        the end of the maternity leave.
    """
    leave = ParentalLeaveEvent(
        date(2026, 3, 2),
        date(2026, 3, 15),
        date(2022, 10, 1),
        ParentalLeaveTaken(0, 0, 0),
        ended,
        parental_base_pay=base,
    )
    run = _march(PeriodState.zero())
    employment = replace(_EMPLOYMENT, category=WorkerCategory.IMPIEGATO)
    return replace(run, employment=employment, facts=PeriodFacts(events=(leave,)))


def _hourly_parental(base: InpsSicknessBase | None, ended: date | None) -> PeriodInput:
    """Return two days of parental leave by the hour in March of an impiegato.

    The same child as :func:`_parental`, an average day of 8 hours.

    Returns:
        The March run; the indemnity needs the pay of the month before and
        the end of the maternity leave.
    """
    leave = HourlyParentalLeaveEvent(
        tuple(LeaveHours(date(2026, 3, d), Decimal(4)) for d in (2, 3, 4, 5)),
        date(2022, 10, 1),
        ParentalLeaveTaken(0, 0, 0),
        Decimal(8),
        protection_ended_on=ended,
        parental_base_pay=base,
    )
    run = _march(PeriodState.zero())
    employment = replace(_EMPLOYMENT, category=WorkerCategory.IMPIEGATO)
    return replace(run, employment=employment, facts=PeriodFacts(events=(leave,)))


def _notice(cause: TerminationCause | None, just: bool | None) -> PeriodInput:
    """Return the March run of a C3 whose employment ends on 31 March.

    The act is received on 20 March; who owes the notice depends on how the
    employment ends and on its just cause.

    Returns:
        The March run with the notice not given.
    """
    period = EmploymentPeriod(date(2025, 1, 1), date(2026, 3, 31), cause, just)
    run = _march(PeriodState.zero())
    employment = replace(_EMPLOYMENT, employment_period=period)
    events = (NoticeIndemnityEvent(date(2026, 3, 20)),)
    return replace(run, employment=employment, facts=PeriodFacts(events=events))


def _extraordinary(last_pay: Decimal | None) -> PeriodInput:
    """Return two weeks of extraordinary leave in March of an impiegato.

    Returns:
        The March run; the indemnity needs the last pay before the leave.
    """
    leave = ExtraordinaryLeaveEvent(date(2026, 3, 2), date(2026, 3, 15), last_pay)
    run = _march(PeriodState.zero())
    employment = replace(_EMPLOYMENT, category=WorkerCategory.IMPIEGATO)
    return replace(run, employment=employment, facts=PeriodFacts(events=(leave,)))


def sickness_cases[C](
    case: Callable[[PeriodInput, PeriodInput, str], C],
) -> Mapping[str, tuple[C, ...]]:
    """Return the cases of the sickness facts, built with ``case``.

    Returns:
        The cases keyed ``Type.field``.
    """
    return {
        "SicknessEpisode.short_absence_exempt": (
            case(
                _short_absences(False),
                _short_absences(None),
                "short_absence_exempt",
            ),
        ),
        "SicknessEpisode.hospital_stays": (
            case(
                _long_sickness(()),
                _long_sickness(None),
                "hospital_stays",
            ),
        ),
        "SicknessEpisode.daily_contributions": (
            case(_cinema_sickness(120), _cinema_sickness(None), "daily_contributions"),
        ),
        "SicknessEpisode.serious_illness": (
            case(
                _logistica_long(serious=False),
                _logistica_long(serious=None),
                "serious_illness",
            ),
        ),
        "SicknessEpisode.inps_base": (
            case(
                _inps_base_sickness(
                    InpsSicknessBase(Decimal("2158.26"), Decimal(0), paid_days=24)
                ),
                _inps_base_sickness(None),
                "inps_base",
            ),
        ),
        "InpsSicknessBase.paid_days": (
            case(
                _inps_base_sickness(
                    InpsSicknessBase(Decimal("2158.26"), Decimal(0), paid_days=24)
                ),
                _inps_base_sickness(InpsSicknessBase(Decimal("2158.26"), Decimal(0))),
                "inps_base",
            ),
        ),
        "MaternityLeaveEvent.maternity_base_pay": (
            case(
                _maternity(InpsSicknessBase(Decimal("2158.26"), Decimal(0))),
                _maternity(None),
                "maternity_base_pay",
            ),
        ),
        "PaternityLeaveEvent.paternity_base_pay": (
            case(
                _paternity(InpsSicknessBase(Decimal("2158.26"), Decimal(0))),
                _paternity(None),
                "paternity_base_pay",
            ),
        ),
        "ParentalLeaveEvent.parental_base_pay": (
            case(
                _parental(_FEBRUARY_PAY, _MATERNITY_END),
                _parental(None, _MATERNITY_END),
                "parental_base_pay",
            ),
        ),
        "ParentalLeaveEvent.protection_ended_on": (
            case(
                _parental(_FEBRUARY_PAY, _MATERNITY_END),
                _parental(_FEBRUARY_PAY, None),
                "protection_ended_on",
            ),
        ),
        "HourlyParentalLeaveEvent.parental_base_pay": (
            case(
                _hourly_parental(_FEBRUARY_PAY, _MATERNITY_END),
                _hourly_parental(None, _MATERNITY_END),
                "parental_base_pay",
            ),
        ),
        "HourlyParentalLeaveEvent.protection_ended_on": (
            case(
                _hourly_parental(_FEBRUARY_PAY, _MATERNITY_END),
                _hourly_parental(_FEBRUARY_PAY, None),
                "protection_ended_on",
            ),
        ),
        "EmploymentPeriod.ended_by": (
            case(
                _notice(TerminationCause.DISMISSAL, False),
                _notice(None, None),
                "ended_by",
            ),
        ),
        "EmploymentPeriod.just_cause": (
            case(
                _notice(TerminationCause.DISMISSAL, False),
                _notice(TerminationCause.DISMISSAL, None),
                "just_cause",
            ),
        ),
        "ExtraordinaryLeaveEvent.last_fixed_pay": (
            case(
                _extraordinary(Decimal("2158.26")),
                _extraordinary(None),
                "last_fixed_pay",
            ),
        ),
        "SicknessEpisode.prior_worked_days": (
            case(
                _fixed_term_sickness(200),
                _fixed_term_sickness(None),
                "prior_worked_days",
            ),
        ),
        "OpeningBalances.sickness_known_from": (
            case(
                _sickness_import(date(2023, 1, 1)),
                _sickness_import(None),
                "sickness_known_from",
            ),
        ),
    }
