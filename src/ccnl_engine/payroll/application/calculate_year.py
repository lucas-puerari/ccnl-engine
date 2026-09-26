"""Full-year payroll orchestration: chains calculate_period across all runs."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.application._calendar import effective_calendar
from ccnl_engine.payroll.application._extra_month_accrual import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.application._year_runs import (
    allocate_run_events,
    flag_partial_month,
    opening_of_year,
    select_runs,
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
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
from ccnl_engine.payroll.domain.tax_year import (
    DEFAULT_PAYMENT_DAY,
    monthly_payment_date,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.category import WorkerCategory
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.policy import PolicyResolver

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
    payment_day: int = DEFAULT_PAYMENT_DAY,
    opening_state: PeriodState | None = None,
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
        regione: Region code for regional surtax, e.g. ``"IT-45"``.  ``None`` skips.
        comune_belfiore: Belfiore code for municipal surtax.  ``None`` skips.
        family_composition: Dependent family composition for tax credits.
        has_dependent_children: Whether the worker has fiscally dependent
            children; selects the higher fringe-benefit threshold.
        payment_day: Day of the run month on which every run is paid, 1-28.
            Every payment falls in ``year``, the tax year of every run.
        opening_state: State the first run opens with.  ``None`` starts a
            new employment; pass the result of
            :func:`~ccnl_engine.payroll.application.close_tax_year\
.close_tax_year` to carry the obligations of the previous year, such as
            an installment recovery.  It must close no run of ``year``.
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

    Errors: :class:`~ccnl_engine.engine.errors.InvalidInputError` for an
    override rejected by
    :meth:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride.resolve`,
    an ``employment_period`` with no day in ``year``, a ``payment_day``
    outside 1-28 or an ``opening_state`` with a run of the year closed;
    :class:`ValueError` for a run allocated events in both
    ``period_events`` and ``per_run_events``, or ``weekly_hours`` above
    ``full_time_weekly_hours``.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    ccnl = effective_repo.load_ccnl(ccnl_slug)
    year_calendar = effective_calendar(ccnl, year, calendar)
    schedule = select_runs(year_calendar, employment_period)
    withholding_schedule = WithholdingSchedule.for_runs(schedule, year_calendar)
    effective_contract = contract_type if contract_type is not None else Permanent()
    effective_period_events: dict[int, tuple[WorkEvent, ...]] = period_events or {}
    effective_per_run_events: dict[str, tuple[WorkEvent, ...]] = per_run_events or {}
    non_accruing = non_accruing_days(effective_period_events, effective_per_run_events)
    extra_month_index = {
        (s.kind.value, s.payment_month): s for s in year_calendar.extra_months
    }
    settlements = termination_settlements(
        year_calendar, employment_period, non_accruing
    )

    state = opening_of_year(year, opening_state)
    results: list[PeriodCalculationResult] = []

    for run in schedule.runs:
        pid = PeriodId(year=run.year, month=run.month)
        payment_date = monthly_payment_date(run.year, run.month, payment_day)
        allocated_events = allocate_run_events(
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
        result = flag_partial_month(
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
