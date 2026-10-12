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
from ccnl_engine.events import SicknessEpisode
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
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        pension_fund=enrolment,
    )


def _byblos(erc_amount: Decimal | None) -> Employment:
    return replace(
        CONCIA_D2,
        category=None,
        ccnl_slug="grafica-editoria-aieg.json",
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
        ccnl_slug="igiene-ambientale-utilitalia.json",
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
        ccnl_slug="funzioni-centrali-aran.json",
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
        ccnl_slug="commercio-confcommercio.json",
        level_code="5",
    )
    request = january(terziario)
    employer = replace(request.employer, headcount=Headcount(5), fis_reduction=reduced)
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
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
    )
    request = january(commercio)
    employer = replace(request.employer, provincial_pay_element=in_force)
    return replace(request, employer=employer)


def _operaio(
    january: Callable[[Employment], PeriodInput], hours: Decimal | None
) -> PeriodInput:
    employment = replace(
        CONCIA_D2,
        ccnl_slug="edilizia-ance.json",
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
    }


__all__ = ["sickness_cases"]

_EMPLOYMENT = Employment(
    contract_type=Permanent(),
    ccnl_slug="metalmeccanico-federmeccanica.json",
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
        _EMPLOYMENT, ccnl_slug="logistica-trasporto-confetra.json", level_code="3"
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
        "SicknessEpisode.serious_illness": (
            case(
                _logistica_long(serious=False),
                _logistica_long(serious=None),
                "serious_illness",
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
