"""Per-run helpers of the full-year orchestration: events and partial months."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.employment import EmploymentPeriod
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult
    from ccnl_engine.payroll.domain.run import PayrollRun

_PARTIAL_MONTH = "partial_month_not_prorated"


def allocate_run_events(
    run: PayrollRun,
    period_events: dict[int, tuple[WorkEvent, ...]],
    per_run_events: dict[str, tuple[WorkEvent, ...]],
) -> tuple[WorkEvent, ...]:
    """Return the events allocated to ``run`` under the two-layer policy.

    Priority: explicit ``run_id`` allocation in ``per_run_events`` takes
    precedence.  Regular runs fall back to ``period_events`` keyed by month.
    Extra-month runs (thirteenth, fourteenth, etc.) that have no explicit
    allocation receive no events.

    Args:
        run: The payroll run being processed.
        period_events: Month-keyed events (applies only to regular runs).
        per_run_events: ``run_id``-keyed events (any run kind).

    Returns:
        Tuple of :class:`~ccnl_engine.payroll.domain.events.WorkEvent` for
        this run, possibly empty.

    Raises:
        ValueError: When the same run is allocated events from both
            ``period_events`` and ``per_run_events`` (duplicate allocation).
    """
    in_per_run = run.run_id in per_run_events
    in_period = run.run_kind == "regular" and run.month in period_events
    if in_per_run and in_period:
        msg = (
            f"Duplicate event allocation for run '{run.run_id}': "
            f"events are present in both period_events[{run.month}] and "
            f"per_run_events['{run.run_id}']; supply events in one source only."
        )
        raise ValueError(msg)
    if in_per_run:
        return per_run_events[run.run_id]
    if in_period:
        return period_events[run.month]
    return ()


def flag_partial_month(
    result: PeriodCalculationResult,
    run: PayrollRun,
    employment_period: EmploymentPeriod | None,
) -> PeriodCalculationResult:
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
