"""The una tantum installments a run pays, as arrears of their covered months.

Each installment of a CCNL una tantum paid in the month of a regular or
termination run is owed to the worker (:class:`~.models.UnaTantum`): the
amount of the level, its share for a worker hired within the covered
period, in proportion to the part-time hours.  It is paid as the arrears
of the months it covers (:class:`~ccnl_engine.variable_pay.inputs.ArrearsEvent`):
the share of the covered months of earlier years is taxed apart at the rate
of the income of the biennio (art. 17 c. 1 lett. b, art. 21 TUIR; Agenzia
delle Entrate, risposte 367/2020 and 243/2021 on the una tantum of a
renewal), the rest with the run.

The texts read leave open how a month of service is counted and how a part
time is paid; the engine counts a month in which the worker was employed at
least 15 days, over the months of the covered period, and reduces a part
time by its hours; a run whose employment period is not stated is paid
none.  These readings are the engine limitation :data:`UNA_TANTUM`.
"""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId
from ccnl_engine.variable_pay.inputs import ArrearsEvent

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.period.requests import PeriodCalculationRequest

__all__ = ["UNA_TANTUM", "una_tantum_events"]

#: Engine limitation of a run that pays, or would pay, an una tantum.
UNA_TANTUM = "una_tantum_readings"
_PAYING = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_HALF_MONTH = 15


def _months(first: date, last: date) -> list[tuple[int, int]]:
    """Return the months from ``first`` to ``last`` counted as served.

    Returns:
        ``(year, month)`` of each month with at least 15 days from
        ``first`` to ``last``, or all of them.
    """
    months: list[tuple[int, int]] = []
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        end = calendar.monthrange(year, month)[1]
        start = first.day if (year, month) == (first.year, first.month) else 1
        stop = last.day if (year, month) == (last.year, last.month) else end
        if stop - start + 1 >= min(_HALF_MONTH, end):
            months.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return months


def _ratio(request: PeriodCalculationRequest) -> Decimal:
    weekly, full = request.weekly_hours, request.full_time_weekly_hours
    if weekly is None or full is None or weekly.value >= full.value:
        return Decimal(1)
    return weekly.value / full.value


def _arrears(
    paid: date, amount: Decimal, served: list[tuple[int, int]], tax_year: int
) -> tuple[ArrearsEvent, ...]:
    """Return ``amount`` as the arrears of the earlier years and of the year.

    Returns:
        One event for the share of the served months of earlier years and
        one for the rest, each only when above zero.
    """
    earlier = [m for m in served if m[0] < tax_year]
    before = money(amount * len(earlier) / len(served))
    events = []
    if before:
        year, month = earlier[-1]
        events.append(
            ArrearsEvent(paid, before, reference_period=PeriodId(year, month))
        )
    if amount - before:
        year, month = served[-1]
        events.append(
            ArrearsEvent(paid, amount - before, reference_period=PeriodId(year, month))
        )
    return tuple(events)


def una_tantum_events(
    request: PeriodCalculationRequest, ccnl: CCNL, run_kind: RunKind
) -> tuple[tuple[ArrearsEvent, ...], bool]:
    """Return the arrears of the una tantum the run pays.

    Returns:
        The arrears events and whether the run met an una tantum, paid or
        not for want of the employment period (the path of :data:`UNA_TANTUM`).
    """
    month = request.period_id
    events: list[ArrearsEvent] = []
    met = False
    for una in ccnl.parameters.una_tantum if run_kind in _PAYING else ():
        for installment in una.installments:
            paid = installment.paid_in
            base = installment.amounts.get(request.level_code)
            if (paid.year, paid.month) != (month.year, month.month) or base is None:
                continue
            met = True
            period = request.employment_period
            if period is None or period.started_on > una.covers_until:
                continue
            covered = _months(una.covers_from, una.covers_until)
            served = _months(max(period.started_on, una.covers_from), una.covers_until)
            if not served:
                continue
            amount = money(base * len(served) / len(covered) * _ratio(request))
            tax_year = request.payment_date.year
            events.extend(_arrears(paid, amount, served, tax_year))
    return tuple(events), met
