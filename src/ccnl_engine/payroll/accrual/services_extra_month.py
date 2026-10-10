"""Extra-month rateo of a run: what an extra-month run pays of a monthly pay.

An extra-month run pays its accrued share of a monthly pay: the months of
the 12 ending in the payment month that qualify under the CCNL rule, with
the CCNL fraction of that extra month.  The ratei paid at termination are
selected in :mod:`._extra_month_qualification` and paid by
:mod:`._extra_month_settlement`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.accrual.models import ExtraMonthAccrual
from ccnl_engine.payroll.accrual.models_extra_month_schedule import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.payroll.accrual.services_rule import month_accrual_rule
from ccnl_engine.payroll.year.services_calendar import standard_calendar

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.period.requests import PeriodCalculationRequest

__all__ = ["run_accrual", "run_fraction", "run_schedule"]


def run_accrual(
    request: PeriodCalculationRequest, ccnl: CCNL, competence: date
) -> ExtraMonthAccrual | None:
    """Return the rateo an extra-month run pays.

    Args:
        request: The period request.  Its ``extra_month_accrual`` is used
            when given; otherwise an extra-month run counts its rateo from
            ``employment_period`` over the 12 months ending in the run month,
            with the CCNL fraction of that extra month and the CCNL
            month-qualification rule.
        ccnl: The contract, whose standard calendar gives the fraction.
        competence: Date the CCNL entitlement is read at.

    Returns:
        The accrual of an extra-month run, ``None`` for any other run.
    """
    run = request.run
    if run is None or run.run_kind not in {k.value for k in ExtraMonthKind}:
        return None
    if request.extra_month_accrual is not None:
        return request.extra_month_accrual
    kind = ExtraMonthKind(run.run_kind.value)
    standard = standard_calendar(ccnl, run.year, competence)
    max_fraction = next(
        (s.max_fraction for s in standard.extra_months if s.kind is kind),
        Decimal(1),
    )
    schedule = run_schedule(kind, run.month, max_fraction)
    return ExtraMonthAccrual.of(
        schedule, run.year, request.employment_period, rule=month_accrual_rule(ccnl)
    )


def run_schedule(
    kind: ExtraMonthKind, payment_month: int, max_fraction: Decimal
) -> ExtraMonthSchedule:
    """Return the schedule of an extra month paid in ``payment_month``.

    Returns:
        The schedule whose accrual window is the 12 months ending in the
        payment month.
    """
    return ExtraMonthSchedule(
        kind=kind,
        name=kind.value,
        payment_month=payment_month,
        accrual_window_start_month=payment_month % 12 + 1,
        max_fraction=max_fraction,
    )


def run_fraction(accrual: ExtraMonthAccrual | None) -> Decimal:
    """Return the share of a monthly pay the run pays.

    Args:
        accrual: The rateo of an extra-month run from :func:`run_accrual`,
            ``None`` for any other run.

    Returns:
        ``1`` for a regular run, the accrued fraction for an extra run.
    """
    return Decimal(1) if accrual is None else accrual.fraction
