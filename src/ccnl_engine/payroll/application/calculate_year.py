"""Full-year payroll orchestration: chains calculate_period across all runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.eligibility import (
    ContributionCeilingStatus,
)
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.schedule import PayrollSchedule

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["YearCalculationResult", "calculate_year"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class YearCalculationResult:
    """Aggregated result for a full payroll year.

    Attributes:
        year: The tax year.
        period_results: One :class:`PeriodCalculationResult` per computed run,
            in payment order (regular runs and extra-month runs interleaved).
        annual_gross: Sum of ``period_gross`` across all runs.
        annual_net: Sum of ``period_net`` across all runs.
        annual_employer_cost: Sum of ``period_employer_cost`` across all runs.
    """

    year: int
    period_results: tuple[PeriodCalculationResult, ...]
    annual_gross: Decimal
    annual_net: Decimal
    annual_employer_cost: Decimal


def _allocate_events(
    run: PayrollRun,
    period_events: dict[int, tuple[WorkEvent, ...]],
    per_run_events: dict[str, tuple[WorkEvent, ...]],
) -> tuple[WorkEvent, ...]:
    """Return the events allocated to ``run`` under the two-layer policy.

    Priority: explicit ``run_id`` allocation in ``per_run_events`` takes
    precedence.  Regular runs fall back to ``period_events`` keyed by month.
    Extra-month runs (thirteenth, fourteenth, etc.) that have no explicit
    allocation receive no events.

    Args:
        run: The payroll run being processed.
        period_events: Month-keyed events (applies only to regular runs).
        per_run_events: ``run_id``-keyed events (any run kind).

    Returns:
        Tuple of :class:`~ccnl_engine.payroll.domain.events.WorkEvent` for
        this run, possibly empty.

    Raises:
        ValueError: When the same run is allocated events from both
            ``period_events`` and ``per_run_events`` (duplicate allocation).
    """
    in_per_run = run.run_id in per_run_events
    in_period = run.run_kind == "regular" and run.month in period_events
    if in_per_run and in_period:
        msg = (
            f"Duplicate event allocation for run '{run.run_id}': "
            f"events are present in both period_events[{run.month}] and "
            f"per_run_events['{run.run_id}']; supply events in one source only."
        )
        raise ValueError(msg)
    if in_per_run:
        return per_run_events[run.run_id]
    if in_period:
        return period_events[run.month]
    return ()


def calculate_year(
    year: int,
    ccnl_slug: str,
    level_code: str,
    *,
    calendar: WorkCalendar | None = None,
    contract_type: Permanent | Apprentice | FixedTerm | None = None,
    num_employees: int = 50,
    ceiling_status: ContributionCeilingStatus = ContributionCeilingStatus.UNKNOWN,
    period_events: dict[int, tuple[WorkEvent, ...]] | None = None,
    per_run_events: dict[str, tuple[WorkEvent, ...]] | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    family_composition: FamilyComposition | None = None,
    has_dependent_children: bool = False,
    repo: KnowledgeRepository | None = None,
) -> YearCalculationResult:
    """Compute payroll for all runs in a year.

    Derives the run sequence from the ``calendar`` via
    :class:`~ccnl_engine.payroll.domain.schedule.PayrollSchedule`.  Regular
    months (1-12) plus any extra months (tredicesima, quattordicesima) are each
    computed as separate :func:`calculate_period` calls, with the closing
    :class:`~ccnl_engine.payroll.domain.period.PeriodState` of each run passed
    as the opening state of the next.

    Args:
        year: The tax year.
        ccnl_slug: Knowledge-bundle CCNL filename (e.g.
            ``"metalmeccanico-federmeccanica.json"``).
        level_code: Worker's contractual level code (e.g. ``"C3"``).
        calendar: Year-level payroll calendar.  Governs the run sequence:
            extra months in ``calendar.extra_months`` produce additional runs
            in the month configured by
            :class:`~ccnl_engine.payroll.domain.calendar.ExtraMonthSchedule`.
            When ``None``, the calendar is derived from the CCNL
            ``additional_months`` parameter via
            :meth:`~ccnl_engine.payroll.domain.calendar.WorkCalendar.from_additional_months`.
        contract_type: Employment contract type.  Defaults to
            :class:`~ccnl_engine.engine.payroll.domain.employment.Permanent`.
        num_employees: Employer headcount for INPS rate resolution.
            Defaults to 50.
        ceiling_status: Whether the IVS massimale contribution ceiling applies.
            Defaults to
            :attr:`~ccnl_engine.payroll.domain.eligibility.ContributionCeilingStatus.UNKNOWN`
            (ceiling not applied; caller should supply the worker's enrollment status).
        period_events: Optional mapping from month number (1-12) to the
            variable work events for that regular period.  Extra-month runs
            (thirteenth, fourteenth) receive no events from this mapping;
            use ``per_run_events`` for explicit run-level allocation.
        per_run_events: Optional mapping from ``run_id`` to events for that
            specific run.  Supports any run kind (regular, thirteenth, etc.).
            A run that appears in both ``period_events`` (by month) and
            ``per_run_events`` (by run_id) raises :class:`ValueError`.
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
        per run (12, 13, or 14 depending on the CCNL) and aggregated totals.

    Raises:
        ValueError: If ``calendar.year`` does not match ``year``, or if the
            same run is allocated events in both ``period_events`` and
            ``per_run_events``.
    """
    if calendar is None:
        effective_repo = repo if repo is not None else BundledKnowledgeRepository()
        ccnl = effective_repo.load_ccnl(ccnl_slug)
        as_of = date(year, 1, 1)
        additional_months = int(ccnl.parameters.additional_months.value_at(as_of))
        calendar = WorkCalendar.from_additional_months(year, additional_months)
    elif calendar.year != year:
        msg = f"calendar.year={calendar.year} does not match year={year}"
        raise ValueError(msg)

    schedule = PayrollSchedule.from_calendar(calendar)
    effective_contract = contract_type if contract_type is not None else Permanent()
    effective_period_events: dict[int, tuple[WorkEvent, ...]] = period_events or {}
    effective_per_run_events: dict[str, tuple[WorkEvent, ...]] = per_run_events or {}

    state = PeriodState.zero()
    results: list[PeriodCalculationResult] = []

    for run in schedule.runs:
        pid = PeriodId(year=run.year, month=run.month)
        payment_date = date(run.year, run.month, 28)
        allocated_events = _allocate_events(
            run, effective_period_events, effective_per_run_events
        )
        req = PeriodCalculationRequest(
            period_id=pid,
            payment_date=payment_date,
            ccnl_slug=ccnl_slug,
            level_code=level_code,
            opening_state=state,
            contract_type=effective_contract,
            num_employees=num_employees,
            ceiling_status=ceiling_status,
            events=allocated_events,
            regione=regione,
            comune_belfiore=comune_belfiore,
            family_composition=family_composition,
            has_dependent_children=has_dependent_children,
            run=run,
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
