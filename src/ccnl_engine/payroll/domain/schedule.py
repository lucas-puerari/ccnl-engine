"""PayrollSchedule: the ordered run sequence for a payroll year.

A :class:`PayrollSchedule` describes exactly which payroll runs happen during
a tax year and in what order, including extra months (tredicesima, quattordicesima).
It is the single source of truth used by :func:`calculate_year` to determine
how many :class:`~ccnl_engine.payroll.domain.run.PayrollRun` to compute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.calendar import ExtraMonthKind
from ccnl_engine.payroll.domain.run import PayrollRun

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.calendar import WorkCalendar

__all__ = ["PayrollSchedule"]


@dataclass(frozen=True)
class PayrollSchedule:
    """Ordered sequence of payroll runs for one tax year.

    The schedule is built once per year and is consumed by
    :func:`~ccnl_engine.payroll.application.calculate_year.calculate_year`
    to determine how many periods to compute and in what order.

    Attributes:
        year: The tax year.
        runs: Ordered tuple of :class:`~ccnl_engine.payroll.domain.run.PayrollRun`
            for this year.  Regular runs appear before extra runs in the month
            in which the extra run is paid.
    """

    year: int
    runs: tuple[PayrollRun, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:  # noqa: D105
        seen: set[str] = set()
        for run in self.runs:
            if run.run_id in seen:
                msg = f"duplicate run_id '{run.run_id}' in PayrollSchedule"
                raise ValueError(msg)
            seen.add(run.run_id)
            if run.year != self.year:
                msg = (
                    f"run {run.run_id} belongs to year {run.year} "
                    f"but schedule is for year {self.year}"
                )
                raise ValueError(msg)

    @classmethod
    def from_calendar(cls, calendar: WorkCalendar) -> PayrollSchedule:
        """Build a :class:`PayrollSchedule` from a :class:`WorkCalendar`.

        Generates twelve regular runs (one per calendar month) plus one extra
        run per :class:`~ccnl_engine.payroll.domain.calendar.ExtraMonthSchedule`
        in the calendar.  The extra run is inserted directly after the regular
        run for its ``payment_month``.

        Args:
            calendar: Year-level payroll calendar.

        Returns:
            A :class:`PayrollSchedule` with all runs in payment order.
        """
        year = calendar.year
        runs: list[PayrollRun] = []
        for month in range(1, 13):
            runs.append(PayrollRun.regular(year, month))
            for extra in calendar.extra_months:
                if extra.payment_month == month:
                    if extra.kind == ExtraMonthKind.FOURTEENTH:
                        runs.append(PayrollRun.fourteenth(year, month))
                    else:
                        runs.append(PayrollRun.thirteenth(year, month))
        return cls(year=year, runs=tuple(runs))
