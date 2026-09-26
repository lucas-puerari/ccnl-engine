"""Shared helpers for legal scenarios: one bundled engine and request builders."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    PayrollState,
)
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine import PayrollResult
    from ccnl_engine.events import WorkEvent

ENGINE = PayrollEngine.bundled()

COMMERCIO = "commercio-confcommercio.json"
COOP_SOCIALI = "cooperative-sociali.json"
DOMESTIC = "lavoro-domestico-non-convivente.json"
POSTAL_FISE = "servizi-postali-appalto-fise.json"
PA_FUNZIONI_CENTRALI = "funzioni-centrali-aran.json"


def regular_period(
    *,
    ccnl_slug: str = COMMERCIO,
    level_code: str = "4",
    year: int = 2026,
    month: int = 1,
    payment_date: date | None = None,
    facts: EmploymentFacts | None = None,
    employer: Employer | None = None,
    events: tuple[WorkEvent, ...] = (),
    opening_state: PayrollState | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
) -> PayrollResult:
    """Compute one regular payroll run through the public facade.

    Returns:
        The engine result for the requested run.
    """
    return ENGINE.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=payment_date or date(year, month, 27),
            ccnl_slug=ccnl_slug,
            level_code=level_code,
            employment_facts=facts or EmploymentFacts(),
            employer=employer or Employer(),
            opening_state=opening_state or PayrollState.zero(),
            events=events,
            regione=regione,
            comune_belfiore=comune_belfiore,
        )
    )


def substitute_tax(result: PayrollResult) -> Decimal:
    """Return the total substitute tax posted to the ledger for one run.

    Returns:
        Sum of all ledger entries on the substitute-tax account.
    """
    return sum(
        (
            entry.amount
            for entry in result.ledger_entries
            if entry.account is AccountKind.SUBSTITUTE_TAX
        ),
        Decimal(0),
    )
