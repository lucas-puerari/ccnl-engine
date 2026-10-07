"""Shared helpers for legal scenarios: one bundled engine and request builders."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache
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
from ccnl_engine.inputs import ContributableHours, PeriodState, PriorYearTaxFacts
from tests.fixtures.opening_state import fresh_tax_year
from tests.fixtures.seniority import new_hire
from tests.fixtures.tfr import no_tfr_fund

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.events import WorkEvent

ENGINE = PayrollEngine.bundled()

COMMERCIO = "commercio-confcommercio.json"
COOP_SOCIALI = "cooperative-sociali.json"
DOMESTIC = "lavoro-domestico-non-convivente.json"
POSTAL_FISE = "servizi-postali-appalto-fise.json"
PA_FUNZIONI_CENTRALI = "funzioni-centrali-aran.json"

#: Ledger account of the flat taxes of the substitute regimes.
_SUBSTITUTE_TAX = "substitute_tax"

#: Employer of 50 employees, the headcount the scenarios assume.
EMPLOYER = EmployerProfile(headcount=Headcount(50))


def regular_period(
    *,
    ccnl_slug: str = COMMERCIO,
    level_code: str = "4",
    year: int = 2026,
    month: int = 1,
    payment_date: date | None = None,
    employment: Employment | None = None,
    employer: EmployerProfile = EMPLOYER,
    events: tuple[WorkEvent, ...] = (),
    opening_state: PeriodState | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    prior_year: PriorYearTaxFacts | None = None,
    contributable_hours: ContributableHours | None = None,
) -> PeriodResult:
    """Compute one regular payroll run through the public facade.

    ``employment``, when given, replaces ``ccnl_slug`` and ``level_code``;
    otherwise the worker is a :func:`~tests.fixtures.seniority.new_hire`
    with no TFR fund (:func:`~tests.fixtures.tfr.no_tfr_fund`) whose TFR
    accrues in the company.

    Returns:
        The engine result for the requested run.
    """
    return ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=payment_date or date(year, month, 27),
            employment=employment
            or Employment(
                ccnl_slug=ccnl_slug,
                level_code=level_code,
                seniority=new_hire(year),
                tfr_fund=no_tfr_fund(year),
                tfr_treasury_fund=False,
            ),
            employer=employer,
            facts=PeriodFacts(
                contributable_hours=contributable_hours,
                events=events,
                regione=regione,
                comune_belfiore=comune_belfiore,
            ),
            prior_year=prior_year or PriorYearTaxFacts(),
            opening_state=opening_state or PeriodState.zero(),
        )
    )


@cache
def history(
    employment: Employment,
    month: int,
    *,
    employer: EmployerProfile = EMPLOYER,
    facts: PeriodFacts = PeriodFacts(),  # noqa: B008
    prior_year: PriorYearTaxFacts = PriorYearTaxFacts(),  # noqa: B008
    year: int = 2026,
) -> PeriodState:
    """Return the state the regular runs of ``year`` before ``month`` close.

    A scenario of a month after January opens with the history of the same
    worker: the regular runs of the months before it, without events, paid
    on the 27th, from a tax year that carries nothing from the year before
    and no other employment
    (:func:`~tests.fixtures.opening_state.fresh_tax_year`).

    Returns:
        The closing state of the run of the month before ``month``, or the
        state that opens ``year`` for January.
    """
    if month == 1:
        return fresh_tax_year(year)
    opening = history(
        employment,
        month - 1,
        employer=employer,
        facts=facts,
        prior_year=prior_year,
        year=year,
    )
    previous = ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month - 1),
            payment_date=date(year, month - 1, 27),
            employment=employment,
            employer=employer,
            facts=facts,
            prior_year=prior_year,
            opening_state=opening,
        )
    )
    return previous.closing_state


def substitute_tax(result: PeriodResult) -> Decimal:
    """Return the total substitute tax posted to the ledger for one run.

    Returns:
        Sum of all ledger entries on the substitute-tax account.
    """
    return sum(
        (
            entry.amount
            for entry in result.ledger_entries
            if entry.account == _SUBSTITUTE_TAX
        ),
        Decimal(0),
    )


def remitted(result: PeriodResult, code: str) -> Decimal:
    """Return the amount of one run under an F24 codice tributo.

    Returns:
        Sum of the remittance summary lines of ``result`` with ``code``.
    """
    return sum(
        (
            line.amount
            for line in result.remittance_summary()
            if line.remittance_code == code
        ),
        Decimal(0),
    )
