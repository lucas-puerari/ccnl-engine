"""Full-year payroll orchestration: chains calculate_period across all 12 periods."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.events import WorkEvent

__all__ = ["YearCalculationResult", "calculate_year"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class YearCalculationResult:
    """Aggregated result for a full payroll year.

    Attributes:
        year: The tax year.
        period_results: One :class:`PeriodCalculationResult` per computed
            period, in chronological order (January to December).
        annual_gross: Sum of ``period_gross`` across all periods.
        annual_net: Sum of ``period_net`` across all periods.
        annual_employer_cost: Sum of ``period_employer_cost`` across all
            periods.
    """

    year: int
    period_results: tuple[PeriodCalculationResult, ...]
    annual_gross: Decimal
    annual_net: Decimal
    annual_employer_cost: Decimal


def calculate_year(
    year: int,
    ccnl_slug: str,
    level_code: str,
    *,
    calendar: WorkCalendar,
    contract_type: Permanent | Apprentice | FixedTerm | None = None,
    num_employees: int = 50,
    period_events: dict[int, tuple[WorkEvent, ...]] | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    family_composition: FamilyComposition | None = None,
    has_dependent_children: bool = False,
    repo: KnowledgeRepository | None = None,
) -> YearCalculationResult:
    """Compute payroll for all 12 periods of a year.

    Calls :func:`calculate_period` for months 1-12, threading the closing
    :class:`~ccnl_engine.payroll.domain.period.PeriodState` of each period
    as the opening state of the next.  The ``calendar`` parameter governs
    the extra-month schedule but does not alter the 12 regular period calls.

    Args:
        year: The tax year.
        ccnl_slug: Knowledge-bundle CCNL filename (e.g.
            ``"metalmeccanico-federmeccanica.json"``).
        level_code: Worker's contractual level code (e.g. ``"C3"``).
        calendar: Year-level payroll calendar.  Currently used to carry
            the extra-month schedule; period payment dates default to the
            28th of each month.
        contract_type: Employment contract type.  Defaults to
            :class:`~ccnl_engine.engine.payroll.domain.employment.Permanent`.
        num_employees: Employer headcount for INPS rate resolution.
            Defaults to 50.
        period_events: Optional mapping from month number (1-12) to the
            variable work events for that period.  Months not present
            receive no events.
        regione: ISO region code for regional surtax.  ``None`` skips.
        comune_belfiore: Belfiore code for municipal surtax.  ``None`` skips.
        family_composition: Dependent family composition for tax credits.
        has_dependent_children: Whether the worker has fiscally dependent
            children; selects the higher fringe-benefit threshold.
        repo: Optional knowledge repository.  Uses the bundled repository
            when ``None``.

    Returns:
        :class:`YearCalculationResult` with one
        :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`
        per month and aggregated annual totals.

    Raises:
        ValueError: If ``calendar.year`` does not match ``year``.
    """
    if calendar.year != year:
        msg = f"calendar.year={calendar.year} does not match year={year}"
        raise ValueError(msg)

    effective_contract = contract_type if contract_type is not None else Permanent()
    effective_events: dict[int, tuple[WorkEvent, ...]] = period_events or {}

    state = PeriodState.zero()
    results: list[PeriodCalculationResult] = []

    for month in range(1, 13):
        pid = PeriodId(year=year, month=month)
        payment_date = date(year, month, 28)
        req = PeriodCalculationRequest(
            period_id=pid,
            payment_date=payment_date,
            ccnl_slug=ccnl_slug,
            level_code=level_code,
            opening_state=state,
            contract_type=effective_contract,
            num_employees=num_employees,
            events=effective_events.get(month, ()),
            regione=regione,
            comune_belfiore=comune_belfiore,
            family_composition=family_composition,
            has_dependent_children=has_dependent_children,
        )
        result = calculate_period(req, repo=repo)
        results.append(result)
        state = result.closing_state

    period_results = tuple(results)
    return YearCalculationResult(
        year=year,
        period_results=period_results,
        annual_gross=sum((r.period_gross for r in period_results), _ZERO),
        annual_net=sum((r.period_net for r in period_results), _ZERO),
        annual_employer_cost=sum(
            (r.period_employer_cost for r in period_results), _ZERO
        ),
    )
