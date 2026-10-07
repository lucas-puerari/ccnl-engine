"""Extra-month ratei liquidated at the termination on a single run.

A year plan passes the ratei each run liquidates.  A run computed on its own
(``PeriodCalculationRequest.extra_month_settlements`` left ``None``) derives
them from the CCNL calendar with the same rule
(:func:`~ccnl_engine.payroll.application.year._extra_month_qualification\
.termination_settlements`): the run that pays the termination month
liquidates every extra month whose next payment falls outside the
employment, so chained runs pay what the year plan pays.  An extra-month run
those ratei cover is refused: it would pay them a second time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.year._accrual_rule import month_accrual_rule
from ccnl_engine.payroll.application.year._calendar import effective_calendar
from ccnl_engine.payroll.application.year._extra_month_qualification import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.domain.run import (
    PayrollRun,
    PayrollRunId,
    RunKind,
    run_identifier,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest

__all__ = ["run_settlements"]

_EXTRA_MONTHS = frozenset({RunKind.THIRTEENTH, RunKind.FOURTEENTH})


def run_settlements(
    request: PeriodCalculationRequest, ccnl: CCNL
) -> tuple[ExtraMonthAccrual, ...]:
    """Return the ratei the run liquidates at the termination.

    Args:
        request: The period request.  Its ``extra_month_settlements`` are
            used when given; ``None`` derives them from the CCNL calendar.
        ccnl: The contract, whose calendar and accrual rule count the ratei.

    Returns:
        The ratei of the extra months the run liquidates: on the regular run
        of the termination month, or on a termination run of that month
        when its regular run is not closed; empty on any other run.  When
        ``extra_month_settlements`` is ``None``, an extra-month run at or
        after the termination month of an extra month the run of that month
        liquidates raises
        :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
    """
    if request.extra_month_settlements is not None:
        return request.extra_month_settlements
    month = request.period_id
    run_id = run_identifier(request.run, month.year, month.month)
    period = request.employment_period
    ended_on = None if period is None else period.ended_on
    if ended_on is None or ended_on.year != run_id.year:
        return ()
    calendar = effective_calendar(ccnl, run_id.year, None)
    settled = termination_settlements(
        calendar, period, non_accruing_days(request.events), month_accrual_rule(ccnl)
    )
    regular = PayrollRun.regular(run_id.year, ended_on.month).identifier
    accruals = settled[str(regular)]
    if run_id.kind in _EXTRA_MONTHS:
        _check_not_settled(run_id, accruals, ended_on.month)
    if run_id.month != ended_on.month or not _pays_month(request, run_id, regular):
        return ()
    return accruals


def _pays_month(
    request: PeriodCalculationRequest, run_id: PayrollRunId, regular: PayrollRunId
) -> bool:
    """Return whether the run pays its month: the one that liquidates ratei.

    Returns:
        ``True`` for the regular run, and for a termination run when the
        regular run of the month is not closed.
    """
    if run_id.kind is RunKind.REGULAR:
        return True
    closed = request.opening_state.accrual.competence_runs
    return run_id.kind is RunKind.TERMINATION and regular not in closed


def _check_not_settled(
    run_id: PayrollRunId, accruals: tuple[ExtraMonthAccrual, ...], ended_month: int
) -> None:
    """Refuse an extra-month run whose ratei the termination month liquidates.

    Raises:
        InvalidInputError: When ``run_id`` is at or after the termination
            month and its kind is among ``accruals``.
    """
    kinds = {accrual.kind.value for accrual in accruals}
    if run_id.month < ended_month or run_id.kind.value not in kinds:
        return
    msg = (
        f"run '{run_id}' pays the {run_id.kind} ratei the employment liquidates "
        f"on the run of its termination month ({ended_month:02d}): compute that "
        "run, which pays them as extra-month earnings"
    )
    raise InvalidInputError(msg, field="PayrollRun.run_kind", feature="payroll_run")
