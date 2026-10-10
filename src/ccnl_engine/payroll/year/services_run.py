"""Runs of a competence year: selection and requests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.accrual.models import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    MonthAccrualRule,
)
from ccnl_engine.payroll.accrual.services_extra_month_qualification import (
    non_accruing_days,
    termination_settlements,
    unknown_accrual_days,
)
from ccnl_engine.payroll.period.inputs import PeriodInput
from ccnl_engine.payroll.year.models_schedule import PayrollSchedule

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.accrual.models_extra_month_schedule import (
        ExtraMonthSchedule,
    )
    from ccnl_engine.payroll.employment.inputs_fact import EmploymentPeriod
    from ccnl_engine.payroll.period.models_run import PayrollRun, PayrollRunId
    from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
    from ccnl_engine.payroll.state.models import PeriodState
    from ccnl_engine.payroll.withholding.models_schedule import WithholdingSchedule
    from ccnl_engine.payroll.year.inputs_competence_plan import CompetenceYearPlan
    from ccnl_engine.payroll.year.models_calendar import WorkCalendar
    from ccnl_engine.payroll.year.models_payment import PaymentId


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


@dataclass(frozen=True)
class YearPlan:
    """Runs of a competence year with what each run request is built from.

    Attributes:
        schedule: Runs of the year the employment overlaps.
        non_accruing: Days that accrue no extra-month ratei.
        unknown_accrual: Days of absences whose suspension of accrual is
            not stated.
        extra_months: Extra-month schedule by ``(run kind, payment month)``.
        settlements: Ratei paid on a run before the termination, by run id.
        accrual_rule: Month-qualification rule of the CCNL ratei.
    """

    schedule: PayrollSchedule
    non_accruing: frozenset[date]
    extra_months: dict[tuple[str, int], ExtraMonthSchedule]
    settlements: dict[str, tuple[ExtraMonthAccrual, ...]]
    accrual_rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE
    unknown_accrual: frozenset[date] = frozenset()


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
    events = tuple(
        event for facts in plan.facts_by_run.values() for event in facts.events
    )
    non_accruing = non_accruing_days(events)
    unknown_days = unknown_accrual_days(events)
    return YearPlan(
        schedule=schedule,
        non_accruing=non_accruing,
        extra_months={
            (s.kind.value, s.payment_month): s for s in year_calendar.extra_months
        },
        settlements=termination_settlements(
            year_calendar, period, non_accruing, accrual_rule, unknown_days
        ),
        accrual_rule=accrual_rule,
        unknown_accrual=unknown_days,
    )


def run_request(
    plan: CompetenceYearPlan,
    year_plan: YearPlan,
    run: PayrollRun,
    payment: PaymentId,
    state: PeriodState,
    withholding_schedule: WithholdingSchedule | None,
    planned_payments: tuple[PaymentId, ...] | None = None,
    uncovered: tuple[PayrollRunId, ...] = (),
) -> PeriodCalculationRequest:
    """Return the calculation request of ``run``, opening with ``state``.

    Returns:
        The request with the facts and payment date of the run, its
        extra-month rateo and settlements, the withholding schedule of its
        tax year or the payments planned after it, and the runs of the year
        left out as ``uncovered``.
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
                unknown_days=year_plan.unknown_accrual,
            )
            if extra_sched is not None
            else None
        ),
        extra_month_settlements=year_plan.settlements.get(run.run_id, ()),
        withholding_schedule=withholding_schedule,
        uncovered_runs=uncovered,
    )
