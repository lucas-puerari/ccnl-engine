"""Withholding schedules of a whole calendar, paid on one day of each month.

Unit and integration tests that pass a schedule to a run build it here
instead of from the payments of a plan.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.schedule import PayrollSchedule
from ccnl_engine.payroll.domain.tax_year import monthly_payment_date
from ccnl_engine.payroll.domain.withholding_schedule import WithholdingSchedule

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.run import PayrollRun

__all__ = ["calendar_schedule", "identified", "paid_before", "paid_on_day"]


def paid_on_day(run: PayrollRun, day: int = 28) -> PaymentId:
    """Return the payment of ``run`` on ``day`` of its own month.

    Returns:
        The payment id.
    """
    return PaymentId(run.identifier, monthly_payment_date(run.year, run.month, day))


def calendar_schedule(
    calendar: WorkCalendar,
    *,
    day: int = 28,
    before: tuple[PaymentId, ...] = (),
) -> WithholdingSchedule:
    """Return the schedule of every run of ``calendar``, paid on ``day``.

    Args:
        calendar: The calendar of the tax year.
        day: Day of the month each run is paid on.
        before: Payments of the tax year before the runs of the calendar,
            such as a late December of the year before.

    Returns:
        One slot per payment, the extra months carrying their fraction.
    """
    fractions = {e.kind.value: e.max_fraction for e in calendar.extra_months}
    runs = PayrollSchedule.from_calendar(calendar).runs
    return WithholdingSchedule.of_payments(
        calendar.year, (*before, *(paid_on_day(r, day) for r in runs)), fractions
    )


def paid_before(
    run: PayrollRun, additional_months: int | Decimal = 13, *, day: int = 27
) -> tuple[PaymentId, ...]:
    """Return the standard payments of the year of ``run`` that precede it.

    Args:
        run: The run about to be computed.
        additional_months: Months of pay the CCNL grants: 13 for a
            tredicesima, 14 with a quattordicesima.
        day: Day of the month each earlier run was paid on.

    Returns:
        The payments of the standard calendar ordered before ``run``, for an
        opening state that identifies them.
    """
    calendar = WorkCalendar.from_additional_months(run.year, Decimal(additional_months))
    key = run.identifier.order_key
    return tuple(
        paid_on_day(r, day)
        for r in PayrollSchedule.from_calendar(calendar).runs
        if r.identifier.order_key < key
    )


def identified(state: PeriodState, payments: tuple[PaymentId, ...]) -> PeriodState:
    """Return ``state`` with ``payments`` closed: the runs its totals came from.

    Args:
        state: A state with YTD totals and no payment.
        payments: The payments those totals come from, of one tax year.

    Returns:
        The state with the runs closed and the payments listed, bound to
        their tax year.
    """
    runs = tuple(p.run_id for p in payments)
    return replace(
        state,
        accrual=replace(state.accrual, competence_runs=runs),
        cash=replace(state.cash, tax_year=payments[0].tax_year, payments=payments),
    )
