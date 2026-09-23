"""Domain types for period and year payroll computation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PeriodId:
    """Identifies a single payroll period by calendar year and month.

    Use this instead of relying on ``structural.employment.as_of`` to
    identify the competence period.  Both :class:`PeriodPayrollRequest`
    and :class:`PeriodPayrollResult` carry a ``period_id`` so consumers can
    match requests to results without parsing dates.

    Attributes:
        year: Calendar year (e.g. ``2026``).
        month: Month of competence, 1-12.
    """

    year: int
    month: int

    def __post_init__(self) -> None:
        """Validate year and month ranges.

        Raises:
            ValueError: When ``month`` is outside 1-12 or ``year`` is zero.
        """
        if not (1 <= self.month <= 12):
            msg = f"month must be 1-12, got {self.month}"
            raise ValueError(msg)
        if self.year <= 0:
            msg = f"year must be positive, got {self.year}"
            raise ValueError(msg)
