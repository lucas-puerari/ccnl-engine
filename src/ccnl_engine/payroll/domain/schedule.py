"""Payroll schedule and run count of a payroll year.

A :class:`PayrollSchedule` describes exactly which payroll runs happen during
a tax year and in what order, including extra months (tredicesima, quattordicesima).
It is the single source of truth used by :func:`calculate_year` to determine
how many :class:`~ccnl_engine.payroll.domain.run.PayrollRun` to compute.

Three quantities are kept apart because they differ as soon as an extra month
is fractional (13.5 equivalent months, 14 payslips):

- :class:`~ccnl_engine.payroll.domain.extra_month_entitlement\
.ExtraMonthEntitlement`: how many months of pay the year grants;
- :class:`PayrollRunCount`: how many payslips the year issues;
- :class:`~ccnl_engine.payroll.domain.withholding_schedule\
.WithholdingSchedule`: the IRPEF withholding slots that the annual
  projection and the year-end conguaglio run on: the payments of the tax
  year, a late payment of an earlier competence year included.

When the employment period is known, the schedule keeps only the runs paid in
a month the employment overlaps: a regular run for each month with at least
one employed day, an extra-month run only when its payment month is such a
month.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.domain.run import PayrollRun

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod

__all__ = ["PayrollRunCount", "PayrollSchedule"]


@dataclass(frozen=True)
class PayrollRunCount:
    """Number of payslips issued in a payroll year.

    An integer, never derived by truncating an
    :class:`~ccnl_engine.payroll.domain.extra_month_entitlement\
.ExtraMonthEntitlement`: half a quattordicesima is still one payslip.

    Attributes:
        value: Number of runs, at least 1.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            msg = f"run count must be an int; got {type(self.value).__name__}"
            raise TypeError(msg)
        if self.value < 1:
            msg = f"run count must be >= 1; got {self.value}"
            raise ValueError(msg)


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
    def from_calendar(
        cls, calendar: WorkCalendar, employment: EmploymentPeriod | None = None
    ) -> PayrollSchedule:
        """Build a :class:`PayrollSchedule` from a :class:`WorkCalendar`.

        Generates twelve regular runs (one per calendar month) plus one extra
        run per :class:`~ccnl_engine.payroll.domain.extra_month_schedule\
.ExtraMonthSchedule` in the calendar.  The extra run is inserted directly
        after the regular run for its ``payment_month``.  With
        ``employment``, only the runs of months the employment overlaps are
        kept.

        Args:
            calendar: Year-level payroll calendar.
            employment: Employment period, or ``None`` for a worker employed
                all year.

        Returns:
            A :class:`PayrollSchedule` with the selected runs in payment
            order, empty when the employment does not overlap the year.
        """
        year = calendar.year
        runs: list[PayrollRun] = []
        for month in range(1, 13):
            if employment is not None and not employment.overlaps_month(year, month):
                continue
            runs.append(PayrollRun.regular(year, month))
            runs.extend(
                _extra_run(extra.kind, year, month)
                for extra in calendar.extra_months
                if extra.payment_month == month
            )
        return cls(year=year, runs=tuple(runs))

    @property
    def run_count(self) -> PayrollRunCount:
        """Number of payslips in this schedule."""
        return PayrollRunCount(len(self.runs))


def _extra_run(kind: ExtraMonthKind, year: int, month: int) -> PayrollRun:
    """Return the extra-month run of ``kind`` paid in ``month``.

    Returns:
        A fourteenth run for :attr:`ExtraMonthKind.FOURTEENTH`, a thirteenth
        run otherwise.
    """
    if kind == ExtraMonthKind.FOURTEENTH:
        return PayrollRun.fourteenth(year, month)
    return PayrollRun.thirteenth(year, month)
