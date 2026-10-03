"""Runs of a payroll year: opening state, selection, requests, partial months."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.withholding._plan import late_runs
from ccnl_engine.payroll.application.year._extra_month_accrual import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.domain.accrual import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    MonthAccrualRule,
)
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.inputs import PeriodInput
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.schedule import PayrollSchedule, WithholdingSchedule
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.tax_year import monthly_payment_date
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthSchedule
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.run import PayrollRun
    from ccnl_engine.payroll.domain.year_input import YearInput

_PARTIAL_MONTH = "partial_month_not_prorated"


def opening_of_year(year: int, opening_state: PeriodState | None) -> PeriodState:
    """Return the state the first run of ``year`` opens with.

    A year calculation computes every run of competence ``year``, so its
    opening state closes no run of it: :meth:`PeriodState.zero` for a new
    employment, or the result of
    :func:`~ccnl_engine.payroll.application.close_tax_year.close_tax_year`
    to carry the obligations and the competence runs of earlier years.
    Payments of tax year ``year`` that settle an earlier competence year
    (December paid after 12 January, TUIR art. 51 c. 1) may already be
    closed: they take the first slots of the withholding schedule.

    Returns:
        ``opening_state``, or :meth:`PeriodState.zero` when it is ``None``.

    Raises:
        InvalidInputError: When ``opening_state`` is bound to another tax
            year, has a run of competence ``year`` closed, or carries
            payments or YTD amounts that are not those of payments of an
            earlier competence year identified by their payment id.
    """
    if opening_state is None:
        return PeriodState.zero()
    cash = opening_state.cash
    if (
        cash.tax_year not in {None, year}
        or opening_state.accrual.runs_of(year)
        or not _only_late_payments(cash)
    ):
        msg = (
            f"the opening state of a {year} year calculation must close no run "
            f"of {year} and hold only payments of earlier competence years: "
            "pass PeriodState.zero() or the result of close_tax_year() on the "
            "last run of the previous year, then any late payment of it"
        )
        raise InvalidInputError(
            msg, field="YearInput.opening_state", feature="tax_year"
        )
    return opening_state


def _only_late_payments(cash: TaxCashState) -> bool:
    """Whether every payment and YTD amount of ``cash`` is of a known payment.

    The payments of a state that passed :func:`opening_of_year`'s run check
    all settle an earlier competence year.

    Returns:
        ``True`` when ``cash`` identifies every slot it counts by its
        payment id, or holds no payment and no YTD amount.
    """
    if cash.payments:
        slots = sum(1 for p in cash.payments if p.run_id.kind.consumes_withholding_slot)
        return slots == cash.withholding_payments_closed
    bare = replace(cash, obligations=EmploymentObligations())
    return bare == TaxCashState(tax_year=cash.tax_year)


def select_runs(
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


def flag_partial_month(
    result: PeriodResult,
    run: PayrollRun,
    employment_period: EmploymentPeriod | None,
) -> PeriodResult:
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


@dataclass(frozen=True)
class YearPlan:
    """Runs of the year with what each run request is built from.

    Attributes:
        schedule: Runs of the year the employment overlaps.
        withholding_schedule: One withholding slot per payment of the tax
            year: the late payments already closed, then the computed runs.
        non_accruing: Days that accrue no extra-month ratei.
        extra_months: Extra-month schedule by ``(run kind, payment month)``.
        settlements: Ratei paid on a run before the termination, by run id.
        accrual_rule: Month-qualification rule of the CCNL ratei.
    """

    schedule: PayrollSchedule
    withholding_schedule: WithholdingSchedule
    non_accruing: frozenset[date]
    extra_months: dict[tuple[str, int], ExtraMonthSchedule]
    settlements: dict[str, tuple[ExtraMonthAccrual, ...]]
    accrual_rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE


def plan_year(
    request: YearInput,
    year_calendar: WorkCalendar,
    opening: PeriodState,
    accrual_rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
) -> YearPlan:
    """Select the runs of the year and the ratei their requests carry.

    The withholding schedule holds one slot per payment of the tax year:
    the late payments of an earlier competence year already closed in
    ``opening``, then the runs of the year.  The ratei are counted with
    ``accrual_rule``, the CCNL rule of the year.

    Returns:
        The plan of the year.
    """
    period = request.employment.employment_period
    schedule = select_runs(year_calendar, period)
    withholding_schedule = WithholdingSchedule.for_runs(
        schedule, year_calendar, late_runs(opening.cash.payments)
    )
    non_accruing = non_accruing_days(
        event for facts in request.facts_by_run.values() for event in facts.events
    )
    return YearPlan(
        schedule=schedule,
        withholding_schedule=withholding_schedule,
        non_accruing=non_accruing,
        extra_months={
            (s.kind.value, s.payment_month): s for s in year_calendar.extra_months
        },
        settlements=termination_settlements(
            year_calendar, period, non_accruing, accrual_rule
        ),
        accrual_rule=accrual_rule,
    )


def run_request(
    request: YearInput, plan: YearPlan, run: PayrollRun, state: PeriodState
) -> PeriodCalculationRequest:
    """Return the calculation request of ``run``, opening with ``state``.

    Returns:
        The request with the facts of the run, its extra-month rateo and
        settlements and the withholding schedule of the year.
    """
    year, period = request.year, request.employment.employment_period
    extra_sched = plan.extra_months.get((run.run_kind, run.month))
    period_input = PeriodInput(
        run=run,
        payment_date=monthly_payment_date(run.year, run.month, request.payment_day),
        employment=request.employment,
        employer=request.employer,
        facts=request.facts_for(run),
        prior_year=request.prior_year,
        opening_state=state,
    )
    return period_input.calculation_request(
        extra_month_accrual=(
            ExtraMonthAccrual.of(
                extra_sched,
                year,
                period,
                non_accruing_days=plan.non_accruing,
                rule=plan.accrual_rule,
            )
            if extra_sched is not None
            else None
        ),
        extra_month_settlements=plan.settlements.get(run.run_id, ()),
        withholding_schedule=plan.withholding_schedule,
    )
