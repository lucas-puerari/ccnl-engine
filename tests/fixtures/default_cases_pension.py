"""Default cases of the facts of a pension fund enrolment.

Part of :data:`tests.fixtures.default_cases.DEFAULT_CASES`: the explicit
Concia D2 moved to Metalmeccanico Federmeccanica C3 and enrolled in Cometa,
whose employer rate is higher for a young member, moved to Edilizia
industria as an operaio, whose Prevedi contractual contribution is an
amount per ordinary hour worked, and moved to Grafica editoria C1, hired
in 2019 and enrolled in Byblos, whose employer rate is lower for a holder
of the ERC, moved to Servizi ambientali Q and enrolled in Previambiente,
whose rates go on a conventional base of the worker, moved to Funzioni
Centrali, whose end-of-service regime sets the contributions to INPS, and
moved to Terziario 5 at an employer of five, whose FIS rate is cut when it
has not applied for the assegno di integrazione salariale.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import Headcount, PayrollRun
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    EmploymentSector,
    NoPensionFund,
    PensionFundEnrolment,
    PublicEndOfService,
    WorkerCategory,
)
from tests.fixtures.explicit_facts import CONCIA_D2
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from ccnl_engine import Employment, PeriodInput

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
