"""Full-year payroll orchestration: chains calculate_period across all runs."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.year._calendar import effective_calendar
from ccnl_engine.payroll.application.year._runs import (
    flag_partial_month,
    opening_of_year,
    plan_year,
    run_request,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.period import PeriodResult, PeriodState
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.knowledge_repository import KnowledgeRepository
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.calendar_override import CalendarOverride
    from ccnl_engine.payroll.domain.inputs import YearInput
    from ccnl_engine.payroll.domain.policy import PolicyResolver

__all__ = ["YearResult", "calculate_year"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class YearResult:
    """Aggregated result for a full payroll year.

    Attributes:
        year: The tax year.
        period_results: One :class:`PeriodResult` per computed run,
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
    period_results: tuple[PeriodResult, ...]
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
        """Issues of every period in payment order, each reported once.

        A run repeats the issue of an assumption that holds for the whole
        year (e.g. ``somma_esente_income_assumed``) on every payslip; the
        year lists it once, at its first occurrence.  Issues with the same
        code and a different message (e.g. two shortfall amounts) are kept.
        The issues of a single run stay on :attr:`period_results`.
        """
        seen: set[tuple[str, str]] = set()
        issues: list[CalculationIssue] = []
        for issue in (i for r in self.period_results for i in r.issues):
            if (issue.code, issue.message) not in seen:
                seen.add((issue.code, issue.message))
                issues.append(issue)
        return tuple(issues)

    @property
    def decisions(self) -> tuple[CalculationDecision, ...]:
        """Decisions of every period, concatenated in payment order."""
        return tuple(d for r in self.period_results for d in r.decisions)

    @property
    def closing_state(self) -> PeriodState:
        """State after the last run of the year.

        Pass it to ``close_tax_year()`` to open the next tax year.
        """
        return self.period_results[-1].closing_state


def _year_result(
    request: YearInput,
    year_calendar: WorkCalendar,
    period_results: tuple[PeriodResult, ...],
    bundle_version: str | None,
) -> YearResult:
    """Aggregate the period results of the year.

    Returns:
        The year result with its annual totals.
    """
    return YearResult(
        year=request.year,
        period_results=period_results,
        annual_gross=sum((r.period_gross for r in period_results), _ZERO),
        annual_net=sum((r.period_net for r in period_results), _ZERO),
        annual_employer_cost=sum(
            (r.period_employer_cost for r in period_results), _ZERO
        ),
        calendar=year_calendar,
        calendar_override=request.calendar_override,
        bundle_version=bundle_version,
    )


def calculate_year(
    request: YearInput,
    *,
    repo: KnowledgeRepository | None = None,
    resolver: PolicyResolver | None = None,
    bundle_version: str | None = None,
) -> YearResult:
    """Compute payroll for all runs in a year.

    Derives the run sequence from the effective calendar via
    :class:`~ccnl_engine.payroll.domain.schedule.PayrollSchedule`: the CCNL
    standard calendar, or ``request.calendar_override`` once validated
    against it.  Regular months (1-12) plus any extra months (tredicesima,
    quattordicesima) are each computed as separate :func:`calculate_period`
    calls, with the closing
    :class:`~ccnl_engine.payroll.domain.period.PeriodState` of each run passed
    as the opening state of the next.  Every run receives the same
    :class:`~ccnl_engine.payroll.domain.schedule.WithholdingSchedule`, one
    slot per computed run, so the IRPEF conguaglio settles on the last run
    even when an extra month is fractional.  Each run is mapped to its
    request by :meth:`~ccnl_engine.payroll.domain.inputs.PeriodInput\
.calculation_request`, with the facts of
    :meth:`~ccnl_engine.payroll.domain.inputs.YearInput.facts_for`.

    Runs are selected from the employment period: a regular run for each
    month with at least one employed day, an extra-month run only when its
    payment month is such a month.  A partly employed month keeps the full
    monthly pay with a provisional ``partial_month_not_prorated`` issue.
    Extra months accrue per qualifying month of their window
    (:class:`~ccnl_engine.payroll.domain.accrual.ExtraMonthAccrual`); an
    absence with ``suspends_accrual`` in any entry of ``request.periods``
    removes its days from every window.  The ratei of an extra month not
    paid before the termination are paid on the last regular run.  CCNL and
    level validity is not a run filter.

    Args:
        request: Employment, employer, prior-year facts, facts per run,
            calendar override, payment day and opening state of the year.
        repo: Optional knowledge repository.  Uses the bundled repository
            when ``None``.
        resolver: Optional pre-loaded policy resolver.  When ``None``,
            the bundled ruleset is loaded on each :func:`calculate_period` call.
        bundle_version: Knowledge-bundle version string propagated to each
            :class:`~ccnl_engine.payroll.domain.period.PeriodResult` and to
            :class:`YearResult`.

    Returns:
        :class:`YearResult` with one
        :class:`~ccnl_engine.payroll.domain.period.PeriodResult` per selected
        run (12, 13, or 14 for a full year depending on the CCNL) and
        aggregated totals.

    Errors: :class:`~ccnl_engine.shared.domain.errors.InvalidInputError` for an
    override rejected by
    :meth:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride.resolve`,
    an employment period with no day in the year or an ``opening_state``
    with a run of the year closed.
    """
    year = request.year
    period = request.employment.employment_period
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    ccnl = effective_repo.load_ccnl(request.employment.ccnl_slug)
    year_calendar = effective_calendar(ccnl, year, request.calendar_override)
    plan = plan_year(request, year_calendar)
    state = opening_of_year(year, request.opening_state)
    results: list[PeriodResult] = []
    for run in plan.schedule.runs:
        req = run_request(request, plan, run, state)
        result = flag_partial_month(
            calculate_period(
                req, repo=repo, resolver=resolver, bundle_version=bundle_version
            ),
            run,
            period,
        )
        results.append(result)
        state = result.closing_state
    return _year_result(request, year_calendar, tuple(results), bundle_version)
