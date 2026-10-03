"""Withholding plan of a period: its slots, the pay still to come, per-slot shares.

The IRPEF projection and the year-end conguaglio run on the
:class:`~ccnl_engine.payroll.domain.withholding_schedule.WithholdingSchedule`,
one slot per payment of the tax year.  The CCNL ``additional_months``
parameter is an equivalent-months entitlement (13.5 for Cooperative Sociali)
and is never used as a slot count.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _apply_extra_month_policy
from ccnl_engine.payroll.application.year._calendar import standard_calendar
from ccnl_engine.payroll.application.year._extra_month_accrual import run_schedule
from ccnl_engine.payroll.domain.accrual import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    ExtraMonthAccrual,
    MonthAccrualRule,
)
from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.schedule import PayrollSchedule
from ccnl_engine.payroll.domain.tax_year import LAST_PAYMENT_DAY, monthly_payment_date
from ccnl_engine.payroll.domain.withholding_schedule import WithholdingSchedule
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.run import PayrollRunId
    from ccnl_engine.payroll.domain.withholding_schedule import WithholdingSlot
    from ccnl_engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)
_FEATURE = "withholding_schedule"


def resolve_withholding_schedule(
    request: PeriodCalculationRequest,
    payment: PaymentId,
    ccnl: CCNL,
    competence: date,
) -> WithholdingSchedule:
    """Return the withholding schedule the period must use.

    The schedule holds the payments of the tax year already closed in the
    opening state, the payment of the run when it takes a slot, then the
    payments still planned: ``request.planned_payments`` when the caller
    states them, otherwise every run of the CCNL standard calendar of the
    tax year not yet paid, in a month of the employment, each paid on the
    day of the month of this payment.  A payment the standard calendar
    does not foresee in the year (a December paid after 12 January, which
    leaves the tredicesima last in December) is stated with
    ``planned_payments``.

    Args:
        request: The period request: its schedule, supplied by a year or
            tax-year plan, its planned payments and its opening state.
        payment: The payment the run closes.
        ccnl: The contract, whose ``additional_months`` gives the standard
            calendar and the extra-month fractions.
        competence: Competence date used to read ``additional_months``.

    Returns:
        ``request.withholding_schedule`` when given, else the schedule
        described above.

    A planned payment of another tax year, already paid, or of the run of
    this payment raises
    :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
    """
    if request.withholding_schedule is not None:
        return request.withholding_schedule
    tax_year = payment.tax_year
    calendar = standard_calendar(ccnl, tax_year, competence)
    paid = request.opening_state.cash.payments
    planned = request.planned_payments
    if planned is None:
        planned = _projected(calendar, payment, request)
    else:
        _check_planned(planned, payment, request)
    fractions = {e.kind.value: e.max_fraction for e in calendar.extra_months}
    return WithholdingSchedule.of_payments(
        tax_year, (*paid, payment, *planned), fractions
    )


def _projected(
    calendar: WorkCalendar, payment: PaymentId, request: PeriodCalculationRequest
) -> tuple[PaymentId, ...]:
    """Return the standard runs still to pay after ``payment``.

    Returns:
        :func:`standard_payments` after the run of ``payment``, on its day.
    """
    return standard_payments(
        calendar,
        exclude=request.opening_state.cash.paid_runs | {payment.run_id},
        employment=request.employment_period,
        day=payment.payment_date.day,
    )


def standard_payments(
    calendar: WorkCalendar,
    *,
    exclude: frozenset[PayrollRunId],
    employment: EmploymentPeriod | None,
    day: int,
) -> tuple[PaymentId, ...]:
    """Return the runs of a standard calendar still to pay.

    Args:
        calendar: Standard calendar of the tax year.
        exclude: Runs left out: those already paid and the current one.
            An extra month is left out when the extra month of its kind and
            year is, whatever month it was paid in
            (:attr:`~ccnl_engine.payroll.domain.run.PayrollRunId.payment_key`).
        employment: Employment period; runs of months outside it are left
            out.
        day: Day of the month each projected run is paid on, capped at 28.

    Returns:
        The projected payments, in calendar order.
    """
    on_day = min(day, LAST_PAYMENT_DAY)
    keys = {run_id.payment_key for run_id in exclude}
    return tuple(
        PaymentId(run.identifier, monthly_payment_date(run.year, run.month, on_day))
        for run in PayrollSchedule.from_calendar(calendar, employment).runs
        if run.identifier.payment_key not in keys
    )


def _check_planned(
    planned: tuple[PaymentId, ...],
    payment: PaymentId,
    request: PeriodCalculationRequest,
) -> None:
    """Reject a planned payment that cannot follow ``payment``.

    Raises:
        InvalidInputError: When a planned payment is of another tax year,
            already paid, or pays the run of ``payment``.
    """
    paid = request.opening_state.cash.paid_runs
    for planned_payment in planned:
        if (
            planned_payment.tax_year != payment.tax_year
            or planned_payment.run_id in paid
            or planned_payment.run_id == payment.run_id
        ):
            msg = (
                f"planned payment '{planned_payment}' cannot follow payment "
                f"'{payment}': a planned payment is of tax year "
                f"{payment.tax_year}, not yet paid and of another run"
            )
            raise InvalidInputError(
                msg, field="PeriodInput.planned_payments", feature=_FEATURE
            )


def upcoming_recurring_gross(
    regular_chain: MonthlyPayChain,
    upcoming: tuple[WithholdingSlot, ...],
    employment: EmploymentPeriod | None = None,
    rule: MonthAccrualRule = DEFAULT_MONTH_ACCRUAL_RULE,
) -> Decimal:
    """Project the recurring gross of the slots after the current one.

    Each upcoming slot is valued with the pay chain its run kind would pay:
    the regular chain for a regular month, the extra-month chain scaled by
    the rateo the slot's run will pay for a tredicesima or quattordicesima.
    The rateo is counted on ``employment`` as the run will count it, so a
    worker hired during the year is not projected at full accrual; absences
    still to come are unknown and settle at the conguaglio.

    Args:
        regular_chain: Pay chain of a regular month, before any extra-month
            adjustment of the current run.
        upcoming: Slots of the tax year still to pay after the current
            payment.
        employment: Employment period, or ``None`` for a worker employed
            over every accrual window.
        rule: Month-qualification rule of the CCNL ratei.

    Returns:
        Sum of the projected gross of the upcoming slots, zero on the last.
    """
    total = _ZERO
    for slot in upcoming:
        chain = _apply_extra_month_policy(
            regular_chain, slot.run.run_kind, _slot_fraction(slot, employment, rule)
        )
        total += money(chain.base + chain.seniority + chain.allowances_total)
    return total


def _slot_fraction(
    slot: WithholdingSlot, employment: EmploymentPeriod | None, rule: MonthAccrualRule
) -> Decimal:
    """Return the share of a monthly pay the run of ``slot`` will pay.

    Returns:
        ``slot.pay_fraction`` for a regular run; for an extra-month run the
        rateo accrued on ``employment`` up to its payment month.
    """
    kind = slot.run.run_kind.value
    if kind not in {k.value for k in ExtraMonthKind}:
        return slot.pay_fraction
    extra = run_schedule(ExtraMonthKind(kind), slot.run.month, slot.pay_fraction)
    return ExtraMonthAccrual.of(extra, slot.run.year, employment, rule=rule).fraction


def slot_share(annual: Decimal, slots: int) -> Decimal:
    """Split an annual amount evenly over the ``slots`` payments of the year.

    Returns:
        ``annual / slots`` rounded to cents.
    """
    return money(annual / slots)
