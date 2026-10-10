"""Domain types for period and year payroll computation."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.validation import require_int


@dataclass(frozen=True)
class PeriodId:
    """Identifies a single payroll period by calendar year and month.

    Use this instead of relying on ``structural.employment.as_of`` to
    identify the competence period.  Both the period calculation request and
    :class:`~ccnl_engine.payroll.period.results.PeriodResult` carry a
    ``period_id`` so consumers can match requests to results without parsing
    dates.

    Attributes:
        year: Calendar year (e.g. ``2026``).
        month: Month of competence, 1-12.
    """

    year: int
    month: int

    def __post_init__(self) -> None:
        """Validate year and month ranges.

        A ``month`` outside 1-12 or a ``year`` below 1 raises
        :class:`~ccnl_engine.errors.InvalidInputError`.
        """
        require_int(
            self.month, "PeriodId.month", feature="payroll_run", minimum=1, maximum=12
        )
        require_int(self.year, "PeriodId.year", feature="payroll_run", minimum=1)
