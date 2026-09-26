"""Full-year payroll orchestration: chains calculate_period across all runs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.application._calendar import effective_calendar
from ccnl_engine.payroll.application._extra_month_accrual import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.eligibility import (
    ContributionCeilingStatus,
)
from ccnl_engine.payroll.domain.employer import Employer
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    Permanent,
    SeniorityMonths,
    WeeklyHours,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.schedule import PayrollSchedule, WithholdingSchedule

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.category import WorkerCategory
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.policy import PolicyResolver
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["YearCalculationResult", "calculate_year"]

_ZERO = Decimal(0)
_DEFAULT_EMPLOYER = Employer()
_PARTIAL_MONTH = "partial_month_not_prorated"


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
        calendar: The calendar the year ran on: the CCNL standard calendar,
            or the accepted override.
        calendar_override: The override that replaced the standard calendar,
            with its reason and note, or ``None`` when the standard applied.
        bundle_version: Knowledge-bundle version of the calculation.
    """

    year: int
    period_results: tuple[PeriodCalculationResult, ...]
    annual_gross: Decimal
    annual_net: Decimal
    annual_employer_cost: Decimal
    calendar: WorkCalendar
    calendar_override: CalendarOverride | None = None
    bundle_version: str | None = None

    @property
    def status(self) -> CalculationStatus:
        """Worst status across :attr:`period_results`; final when empty."""
        return CalculationStatus.worst(r.status for r in self.period_results)

    @property
    def issues(self) -> tuple[CalculationIssue, ...]:
        """Issues of every period, concatenated in payment order."""
        return tuple(issue for r in self.period_results for issue in r.issues)


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


def _select_runs(
    calendar: WorkCalendar, employment_period: EmploymentPeriod | None
) -> PayrollSchedule:
    """Return the runs of the year the employment overlaps.

    Returns:
        :meth:`PayrollSchedule.from_calendar` restricted to the employment.

    Raises:
        InvalidInputError: When the employment has no day in the year.
    """
    schedule = PayrollSchedule.from_calendar(calendar, employment_period)
    if not schedule.runs:
        msg = (
            f"employment period {employment_period} has no day in "
            f"{calendar.year}: there is no payroll run to compute"
        )
        raise InvalidInputError(msg, feature="employment_facts")
    return schedule


def _flag_partial_month(
    result: PeriodCalculationResult,
    run: PayrollRun,
    employment_period: EmploymentPeriod | None,
) -> PeriodCalculationResult:
    """Mark a regular run of a partly employed month as provisional.

    The bundled CCNL data define no daily divisor for a partial month, so
    the run carries the full monthly pay and a provisional issue.

    Returns:
        ``result``, with one more issue when the employment covers only part
        of the run month.
    """
    if (
        employment_period is None
        or run.run_kind is not RunKind.REGULAR
        or employment_period.covers_month(run.year, run.month)
    ):
        return result
    issue = CalculationIssue(
        code=_PARTIAL_MONTH,
        message=(
            f"employment covers only part of {run.year}-{run.month:02d}; the "
            "full monthly pay is computed because the CCNL data define no "
            "daily divisor for a partial month"
        ),
        status=CalculationStatus.PROVISIONAL,
    )
    return replace(result, issues=(*result.issues, issue))


def calculate_year(
    year: int,
    ccnl_slug: str,
    level_code: str,
    *,
    calendar: CalendarOverride | None = None,
    contract_type: Permanent | Apprentice | FixedTerm | None = None,
    employer: Employer = _DEFAULT_EMPLOYER,
    ceiling_status: ContributionCeilingStatus = ContributionCeilingStatus.UNKNOWN,
    weekly_hours: WeeklyHours | None = None,
    contributable_hours: ContributableHours | None = None,
    full_time_weekly_hours: WeeklyHours | None = None,
    employment_period: EmploymentPeriod | None = None,
    seniority_months: SeniorityMonths | None = None,
    roles: frozenset[str] = frozenset(),
    category: WorkerCategory | None = None,
    period_events: dict[int, tuple[WorkEvent, ...]] | None = None,
    per_run_events: dict[str, tuple[WorkEvent, ...]] | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    family_composition: FamilyComposition | None = None,
    has_dependent_children: bool = False,
    repo: KnowledgeRepository | None = None,
    resolver: PolicyResolver | None = None,
    bundle_version: str | None = None,
) -> YearCalculationResult:
    """Compute payroll for all runs in a year.

    Derives the run sequence from the effective calendar via
    :class:`~ccnl_engine.payroll.domain.schedule.PayrollSchedule`: the CCNL
    standard calendar, or ``calendar`` once validated against it.  Regular
    months (1-12) plus any extra months (tredicesima, quattordicesima) are each
    computed as separate :func:`calculate_period` calls, with the closing
    :class:`~ccnl_engine.payroll.domain.period.PeriodState` of each run passed
    as the opening state of the next.  Every run receives the same
    :class:`~ccnl_engine.payroll.domain.schedule.WithholdingSchedule`, one
    slot per computed run, so the IRPEF conguaglio settles on the last run
    even when an extra month is fractional.

    Runs are selected from ``employment_period``: a regular run for each
    month with at least one employed day, an extra-month run only when its
    payment month is such a month.  A partly employed month keeps the full
    monthly pay with a provisional ``partial_month_not_prorated`` issue.
    Extra months accrue per qualifying month of their window
    (:class:`~ccnl_engine.payroll.domain.accrual.ExtraMonthAccrual`); the
    ratei of an extra month not paid before the termination are paid on the
    last regular run.  CCNL and level validity is not a run filter.

    Args:
        year: The tax year.
        ccnl_slug: Knowledge-bundle CCNL filename (e.g.
            ``"metalmeccanico-federmeccanica.json"``).
        level_code: Worker's contractual level code (e.g. ``"C3"``).
        calendar: Optional
            :class:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride`.
            When ``None``, the calendar is derived from the CCNL
            ``additional_months`` parameter read on 1 January via
            :meth:`~ccnl_engine.payroll.domain.calendar.WorkCalendar.from_additional_months`.
            An override is accepted only when
            :meth:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride.resolve`
            validates it against that standard calendar.  The run sequence
            and the withholding schedule are both built from the effective
            calendar.
        contract_type: Employment contract type.  Defaults to
            :class:`~ccnl_engine.engine.payroll.domain.employment.Permanent`.
        employer: The employer; its headcount resolves INPS rates.
            Defaults to an employer with 50 employees.
        ceiling_status: Whether the IVS massimale contribution ceiling applies.
            Defaults to
            :attr:`~ccnl_engine.payroll.domain.eligibility.ContributionCeilingStatus.UNKNOWN`
            (ceiling not applied; caller should supply the worker's enrollment status).
        weekly_hours: Contracted weekly hours.  Required for domestic CCNLs to
            select the INPS contribution bracket.  ``None`` for non-domestic CCNLs.
            Must not exceed ``full_time_weekly_hours``.
        contributable_hours: Actual hours worked per period.  Required for domestic
            CCNLs to compute flat-rate INPS contributions.  ``None`` otherwise.
        full_time_weekly_hours: Standard full-time weekly hours for the CCNL,
            used to compute the part-time fraction.  ``None`` when not applicable.
        employment_period: Employment start and optional end.  ``None``
            computes every run of the calendar with full ratei.  Otherwise it
            selects the runs and bounds the accrual windows.
        seniority_months: Months of continuous service for seniority resolution.
            ``None`` means seniority increments are not applied.
        roles: Role codes that unlock role-specific contractual allowances.
        category: Worker category declared on the employment.  ``None``
            takes the category fixed by the level, if any.
        period_events: Optional mapping from month number (1-12) to the
            variable work events for that regular period.  Extra-month runs
            receive no events from it.  An absence with ``suspends_accrual``
            in either mapping removes its days from every accrual window.
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
        resolver: Optional pre-loaded policy resolver.  When ``None``,
            the bundled ruleset is loaded on each :func:`calculate_period` call.
        bundle_version: Knowledge-bundle version string propagated to each
            :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`
            and to :class:`YearCalculationResult`.

    Returns:
        :class:`YearCalculationResult` with one
        :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`
        per selected run (12, 13, or 14 for a full year depending on the
        CCNL) and aggregated totals.

    Errors: an override for another year, or one that drops or lowers an
    extra month the CCNL grants or does not match its reason, raises
    :class:`~ccnl_engine.engine.errors.InvalidInputError` (see
    :meth:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride.resolve`).
    The same run allocated events in both ``period_events`` and
    ``per_run_events``, or ``weekly_hours`` above ``full_time_weekly_hours``,
    raises :class:`ValueError`.  An ``employment_period`` with no day in
    ``year`` raises :class:`~ccnl_engine.engine.errors.InvalidInputError`.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    ccnl = effective_repo.load_ccnl(ccnl_slug)
    year_calendar = effective_calendar(ccnl, year, calendar)
    schedule = _select_runs(year_calendar, employment_period)
    withholding_schedule = WithholdingSchedule.for_runs(schedule, year_calendar)
    effective_contract = contract_type if contract_type is not None else Permanent()
    effective_period_events: dict[int, tuple[WorkEvent, ...]] = period_events or {}
    effective_per_run_events: dict[str, tuple[WorkEvent, ...]] = per_run_events or {}
    non_accruing = non_accruing_days(effective_period_events, effective_per_run_events)
    # Build a lookup from (run_kind, payment_month) to ExtraMonthSchedule.
    extra_month_index = {
        (s.kind.value, s.payment_month): s for s in year_calendar.extra_months
    }
    settlements = termination_settlements(
        year_calendar, employment_period, non_accruing
    )

    state = PeriodState.zero()
    results: list[PeriodCalculationResult] = []

    for run in schedule.runs:
        pid = PeriodId(year=run.year, month=run.month)
        payment_date = date(run.year, run.month, 28)
        allocated_events = _allocate_events(
            run, effective_period_events, effective_per_run_events
        )
        extra_sched = extra_month_index.get((run.run_kind, run.month))
        req = PeriodCalculationRequest(
            period_id=pid,
            payment_date=payment_date,
            ccnl_slug=ccnl_slug,
            level_code=level_code,
            opening_state=state,
            contract_type=effective_contract,
            employer=employer,
            ceiling_status=ceiling_status,
            weekly_hours=weekly_hours,
            contributable_hours=contributable_hours,
            full_time_weekly_hours=full_time_weekly_hours,
            employment_period=employment_period,
            seniority_months=seniority_months,
            roles=roles,
            category=category,
            extra_month_accrual=(
                ExtraMonthAccrual.of(
                    extra_sched, year, employment_period, non_accruing_days=non_accruing
                )
                if extra_sched is not None
                else None
            ),
            extra_month_settlements=settlements.get(run.run_id, ()),
            events=allocated_events,
            regione=regione,
            comune_belfiore=comune_belfiore,
            family_composition=family_composition,
            has_dependent_children=has_dependent_children,
            run=run,
            withholding_schedule=withholding_schedule,
        )
        result = _flag_partial_month(
            calculate_period(
                req, repo=repo, resolver=resolver, bundle_version=bundle_version
            ),
            run,
            employment_period,
        )
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
        calendar=year_calendar,
        calendar_override=calendar,
        bundle_version=bundle_version,
    )
