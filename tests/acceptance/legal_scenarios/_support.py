"""Shared helpers for legal scenarios: one bundled engine and request builders."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    ContributableHours,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodState,
    PriorYearTaxFacts,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult, WorkEvent

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

    ``employment``, when given, replaces ``ccnl_slug`` and ``level_code``.

    Returns:
        The engine result for the requested run.
    """
    return ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=payment_date or date(year, month, 27),
            employment=employment
            or Employment(ccnl_slug=ccnl_slug, level_code=level_code),
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
