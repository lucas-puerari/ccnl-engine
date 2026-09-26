"""Lifecycle invariants: runs and ratei within the employment.

Implemented invariants:
    run_within_employment: a regular run is for a month with at least one
        day of employment.
    extra_month_accrual_limit: the ratei a run pays for one extra month and
        accrual window add up to at most 12 months.  The limit is checked
        within the run: no state records the ratei paid by earlier runs, and
        a run after the termination is caught by ``run_within_employment``.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import (
    InvariantCode,
    ReconciliationViolation,
)
from ccnl_engine.payroll.application.state_invariants import run_id_of
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.application._reconcile_types import RunFacts
    from ccnl_engine.payroll.domain.calendar import ExtraMonthKind
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__: list[str] = []

_MONTHS_PER_WINDOW = 12


def check_run_within_employment(
    result: PeriodResult, facts: RunFacts
) -> list[ReconciliationViolation]:
    """Check that a regular run falls in a month of the employment.

    Returns:
        A violation when the run is regular and the employment has no day
        in its month; nothing when the employment is not tracked.
    """
    employment = facts.employment_period
    run_id = run_id_of(result)
    if (
        employment is None
        or run_id.kind is not RunKind.REGULAR
        or employment.overlaps_month(run_id.year, run_id.month)
    ):
        return []
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.RUN_WITHIN_EMPLOYMENT,
            message=(
                f"regular run '{run_id}' is outside the employment "
                f"{employment.started_on} to {employment.ended_on}"
            ),
        )
    ]


def check_extra_month_accrual_limit(
    facts: RunFacts,
) -> list[ReconciliationViolation]:
    """Check that the ratei of one extra month and window reach at most 12.

    Returns:
        One violation per extra month and window paid for more than 12
        months in the run.
    """
    months: defaultdict[tuple[ExtraMonthKind, date], int] = defaultdict(int)
    for accrual in facts.accruals:
        months[accrual.kind, accrual.window.nominal_start] += accrual.months
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.EXTRA_MONTH_ACCRUAL_LIMIT,
            message=(
                f"{kind.value} of the window from {start} pays {total} months "
                f"of ratei, above {_MONTHS_PER_WINDOW}"
            ),
            expected=Decimal(_MONTHS_PER_WINDOW),
            actual=Decimal(total),
        )
        for (kind, start), total in months.items()
        if total > _MONTHS_PER_WINDOW
    ]
