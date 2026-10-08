"""Extra-month ratei liquidated at the termination on a single run.

A year plan passes the ratei each run liquidates.  A run computed on its own
(``PeriodCalculationRequest.extra_month_settlements`` left ``None``) derives
them from the CCNL calendar with the same rule
(:func:`~ccnl_engine.payroll.application.year._extra_month_qualification\
.termination_settlements`): the run that pays the termination month
liquidates every extra month whose next payment falls outside the
employment, so chained runs pay what the year plan pays.  An extra-month run
those ratei cover is refused: it would pay them a second time.

Two cases a run computed on its own cannot settle, each an issue that
blocks payment: an extra month of the window already paid by an earlier
run of the state (only the residual would be due, and the state does not
record the amount paid), and the absences of the earlier months of the
window, which suspend the accrual but are not in the state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.year._accrual_rule import month_accrual_rule
from ccnl_engine.payroll.application.year._calendar import effective_calendar
from ccnl_engine.payroll.application.year._extra_month_qualification import (
    non_accruing_days,
    termination_settlements,
)
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
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
    from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthKind
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest

__all__ = ["run_settlements", "settlement_issues"]

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
    paid = _paid_early(request, ended_on.month, accruals)
    return tuple(accrual for accrual in accruals if accrual.kind not in paid)


def settlement_issues(
    request: PeriodCalculationRequest,
    ccnl: CCNL,
    settlements: tuple[ExtraMonthAccrual, ...],
) -> tuple[CalculationIssue, ...]:
    """Return the issues of the ratei a run computed on its own liquidates.

    Args:
        request: The period request.
        ccnl: The contract.
        settlements: The ratei :func:`run_settlements` returned.

    Returns:
        An incomplete issue per extra month of the window an earlier run
        already paid, and a provisional issue when the window holds months
        closed before this run, whose suspending absences the state does
        not record; empty when a year plan passed the ratei.
    """
    if request.extra_month_settlements is not None:
        return ()
    period = request.employment_period
    ended_on = None if period is None else period.ended_on
    month = request.period_id
    if ended_on is None or month.month != ended_on.month:
        return ()
    year = ended_on.year
    regular = PayrollRun.regular(year, ended_on.month).identifier
    calendar = effective_calendar(ccnl, year, None)
    settled = termination_settlements(
        calendar, period, non_accruing_days(request.events), month_accrual_rule(ccnl)
    ).get(str(regular), ())
    run_id = run_identifier(request.run, month.year, month.month)
    if not settled or not _pays_month(request, run_id, regular):
        return ()
    paid = _paid_early(request, ended_on.month, settled)
    issues = tuple(
        _paid_issue(kind.value) for kind in sorted(paid, key=lambda k: k.value)
    )
    closed_before = any(
        r.kind is RunKind.REGULAR and r.year == year and r.month < ended_on.month
        for r in request.opening_state.accrual.competence_runs
    )
    if settlements and closed_before:
        issues += (_absences_issue(),)
    return issues


def _window_months(payment_month: int, ended_month: int) -> range:
    """Return the months of the termination year in the liquidated window.

    Returns:
        The months up to the termination month that the window of the
        extra month's next payment covers.
    """
    first = payment_month + 1 if payment_month < ended_month else 1
    return range(first, ended_month + 1)


def _paid_early(
    request: PeriodCalculationRequest,
    ended_month: int,
    accruals: tuple[ExtraMonthAccrual, ...],
) -> frozenset[ExtraMonthKind]:
    """Return the kinds of the accruals an earlier closed run already paid.

    Returns:
        The kinds with a closed extra-month run of the termination year
        inside the window the termination liquidates.
    """
    year = request.period_id.year
    closed = request.opening_state.accrual.competence_runs
    paid: set[ExtraMonthKind] = set()
    for accrual in accruals:
        months = _window_months(accrual.window.end.month, ended_month)
        if any(
            r.kind.value == accrual.kind.value and r.year == year and r.month in months
            for r in closed
        ):
            paid.add(accrual.kind)
    return frozenset(paid)


def _paid_issue(kind: str) -> CalculationIssue:
    return CalculationIssue(
        code="extra_month_paid_before_termination",
        message=(
            f"a {kind} run closed earlier in the window already paid ratei the "
            "termination liquidates; the state does not record its amount, so "
            "the residual is not computed: settle the window with a "
            "CompetenceYearPlan or outside the engine"
        ),
        status=CalculationStatus.INCOMPLETE,
    )


def _absences_issue() -> CalculationIssue:
    return CalculationIssue(
        code="termination_window_absences_unknown",
        message=(
            "the ratei liquidated at the termination count the absences of this "
            "run only: those of the earlier months of the window, which can "
            "suspend the accrual, are not in the opening state; compute the "
            "employment with a CompetenceYearPlan to count them"
        ),
        status=CalculationStatus.PROVISIONAL,
    )


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
