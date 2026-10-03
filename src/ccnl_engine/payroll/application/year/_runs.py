"""Runs of a competence year: selection, requests, partial months."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

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
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.schedule import PayrollSchedule
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthSchedule
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.run import PayrollRun
    from ccnl_engine.payroll.domain.withholding_schedule import WithholdingSchedule

_PARTIAL_MONTH = "partial_month_not_prorated"


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
    """Runs of a competence year with what each run request is built from.

    Attributes:
        schedule: Runs of the year the employment overlaps.
        non_accruing: Days that accrue no extra-month ratei.
        extra_months: Extra-month schedule by ``(run kind, payment month)``.
        settlements: Ratei paid on a run before the termination, by run id.
        accrual_rule: Month-qualification rule of the CCNL ratei.
    """

    schedule: PayrollSchedule
    non_accruing: frozenset[date]
    extra_months: dict[tuple[str, int], ExtraMonthSchedule]
    settlements: dict[str, tuple[ExtraMonthAccrual, ...]]
    accrual_rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE


def plan_year(
    plan: CompetenceYearPlan,
    year_calendar: WorkCalendar,
    accrual_rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
) -> YearPlan:
    """Select the runs of the year and the ratei their requests carry.

    The ratei are counted with ``accrual_rule``, the CCNL rule of the year.

    Returns:
        The plan of the year.

    Raises:
        InvalidInputError: When ``plan.payment_dates`` names a run the year
            does not compute.
    """
    period = plan.employment.employment_period
    schedule = select_runs(year_calendar, period)
    unknown = plan.dated_runs - {run.run_id for run in schedule.runs}
    if unknown:
        msg = (
            f"payment_dates names {sorted(unknown)}, not a run of "
            f"{plan.year} for this calendar and employment"
        )
        raise InvalidInputError(
            msg, field="CompetenceYearPlan.payment_dates", feature="tax_year"
        )
    non_accruing = non_accruing_days(
        event for facts in plan.facts_by_run.values() for event in facts.events
    )
    return YearPlan(
        schedule=schedule,
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
    plan: CompetenceYearPlan,
    year_plan: YearPlan,
    run: PayrollRun,
    payment: PaymentId,
    state: PeriodState,
    withholding_schedule: WithholdingSchedule | None,
    planned_payments: tuple[PaymentId, ...] | None = None,
) -> PeriodCalculationRequest:
    """Return the calculation request of ``run``, opening with ``state``.

    Returns:
        The request with the facts and payment date of the run, its
        extra-month rateo and settlements, and the withholding schedule of
        its tax year or the payments planned after it.
    """
    period = plan.employment.employment_period
    extra_sched = year_plan.extra_months.get((run.run_kind, run.month))
    period_input = PeriodInput(
        run=run,
        payment_date=payment.payment_date,
        employment=plan.employment,
        employer=plan.employer,
        facts=plan.facts_for(run),
        prior_year=plan.prior_year,
        current_year=plan.current_year,
        opening_state=state,
        planned_payments=planned_payments,
    )
    return period_input.calculation_request(
        extra_month_accrual=(
            ExtraMonthAccrual.of(
                extra_sched,
                plan.year,
                period,
                non_accruing_days=year_plan.non_accruing,
                rule=year_plan.accrual_rule,
            )
            if extra_sched is not None
            else None
        ),
        extra_month_settlements=year_plan.settlements.get(run.run_id, ()),
        withholding_schedule=withholding_schedule,
    )
