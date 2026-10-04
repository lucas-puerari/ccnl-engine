"""Years of a Metalmeccanico C3 worker around a deferred IRPEF shortfall.

Year N is 2026 with a 20,000 EUR fringe benefit in December: its IRPEF
exceeds the December and thirteenth pay, so the conguaglio leaves a
shortfall.  Year N+1 is modelled as 2026 opening with a deferral of the
conguaglio 2025, the only year whose rules the bundle holds.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.domain.events import FringeEvent
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.prior_year import (
    PriorYearTaxFacts,
    ShortfallDeferralRequest,
)
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from tests.helpers import year_plan

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.year_result import CompetenceYearResult
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.events import AbsenceEvent
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__ = [
    "CCNL",
    "DEFERRAL_REQUEST",
    "YEAR",
    "decision_amount",
    "deferred_lines",
    "opening_with_deferral",
    "year_n",
    "year_n1",
    "year_n_with_request",
    "year_n_without_request",
]

CCNL = "metalmeccanico-federmeccanica.json"
YEAR = 2026
_FRINGE = FringeEvent(event_date=date(YEAR, 12, 5), amount=Decimal(20000))
DEFERRAL_REQUEST = ShortfallDeferralRequest(signed_on=date(YEAR, 12, 10))


def year_n(
    request: ShortfallDeferralRequest | None,
    employment_period: EmploymentPeriod | None = None,
) -> CompetenceYearResult:
    """Return year N, with or without the worker's deferral request.

    Returns:
        The competence year result.
    """
    return calculate_competence_year(
        year_plan(
            YEAR,
            CCNL,
            "C3",
            events={12: (_FRINGE,)},
            prior_year=PriorYearTaxFacts(shortfall_deferral=request),
            employment_period=employment_period,
        )
    )


@cache
def year_n_without_request() -> CompetenceYearResult:
    """Return year N without a deferral request, computed once.

    Returns:
        The competence year result.
    """
    return year_n(None)


@cache
def year_n_with_request() -> CompetenceYearResult:
    """Return year N with the deferral request, computed once.

    Returns:
        The competence year result.
    """
    return year_n(DEFERRAL_REQUEST)


def decision_amount(result: PeriodResult, capability: str, reason: str) -> Decimal:
    """Return the amount of the only decision of ``capability`` for ``reason``.

    Returns:
        The decision amount.
    """
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == capability and d.reason_code == reason
    )
    assert decision.amount is not None
    return decision.amount


def opening_with_deferral(irpef: str) -> PeriodState:
    """Return the opening state of N+1 carrying ``irpef`` deferred from N.

    Returns:
        The opening state.
    """
    deferred = DeferredShortfall(
        tax_year=YEAR - 1,
        signed_on=date(YEAR - 1, 12, 10),
        deferred_from=date(YEAR - 1, 12, 1),
        irpef=Decimal(irpef),
    )
    return PeriodState(
        cash=TaxCashState(
            tax_year=YEAR,
            obligations=EmploymentObligations(deferred_shortfall=(deferred,)),
        )
    )


def year_n1(
    opening: PeriodState | None,
    events: dict[int, tuple[AbsenceEvent, ...]] | None = None,
    employment_period: EmploymentPeriod | None = None,
) -> CompetenceYearResult:
    """Return year N+1 from ``opening``.

    Returns:
        The competence year result.
    """
    return calculate_competence_year(
        year_plan(
            YEAR,
            CCNL,
            "C3",
            events=events,
            opening_state=opening,
            employment_period=employment_period,
        )
    )


def deferred_lines(result: PeriodResult) -> list[tuple[str, Decimal]]:
    """Return the deferred IRPEF lines (code 1066) of ``result``.

    Returns:
        The entry id and amount of each line.
    """
    return [
        (e.entry_id, e.amount)
        for e in result.ledger_entries
        if e.account == AccountKind.ORDINARY_TAX and e.remittance_code == "1066"
    ]
