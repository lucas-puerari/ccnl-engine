"""Payroll schedule, run count and withholding schedule for a payroll year.

A :class:`PayrollSchedule` describes exactly which payroll runs happen during
a tax year and in what order, including extra months (tredicesima, quattordicesima).
It is the single source of truth used by :func:`calculate_year` to determine
how many :class:`~ccnl_engine.payroll.domain.run.PayrollRun` to compute.

Three quantities are kept apart because they differ as soon as an extra month
is fractional (13.5 equivalent months, 14 payslips):

- :class:`~ccnl_engine.payroll.domain.calendar.ExtraMonthEntitlement`: how
  many months of pay the year grants;
- :class:`PayrollRunCount`: how many payslips the year issues;
- :class:`WithholdingSchedule`: the ordered IRPEF withholding slots that the
  annual projection and the year-end conguaglio run on.

When the employment period is known, the schedule keeps only the runs paid in
a month the employment overlaps: a regular run for each month with at least
one employed day, an extra-month run only when its payment month is such a
month.  The withholding schedule is built from those runs, so a short
employment has fewer slots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.calendar import ExtraMonthKind
from ccnl_engine.payroll.domain.run import PayrollRun

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.calendar import WorkCalendar
    from ccnl_engine.payroll.domain.employment import EmploymentPeriod

__all__ = [
    "PayrollRunCount",
    "PayrollSchedule",
    "WithholdingSchedule",
    "WithholdingSlot",
]

_ONE = Decimal(1)


@dataclass(frozen=True)
class PayrollRunCount:
    """Number of payslips issued in a payroll year.

    An integer, never derived by truncating an
    :class:`~ccnl_engine.payroll.domain.calendar.ExtraMonthEntitlement`: half
    a quattordicesima is still one payslip.

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
        run per :class:`~ccnl_engine.payroll.domain.calendar.ExtraMonthSchedule`
        in the calendar.  The extra run is inserted directly after the regular
        run for its ``payment_month``.  With ``employment``, only the runs of
        months the employment overlaps are kept.

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


@dataclass(frozen=True)
class WithholdingSlot:
    """One IRPEF withholding slot: a run and the share of monthly pay it carries.

    Attributes:
        run: The payroll run that consumes this slot.
        pay_fraction: Share of one regular monthly pay the run carries at full
            accrual: ``1`` for a regular month or a full extra month, the
            contractual fraction for a partial one (``0.5`` for half a
            quattordicesima).  Used to project the recurring pay of future
            slots; never to count them.
    """

    run: PayrollRun
    pay_fraction: Decimal = field(default_factory=lambda: _ONE)

    def __post_init__(self) -> None:  # noqa: D105
        if not self.run.run_kind.consumes_withholding_slot:
            msg = f"run {self.run.run_id} does not consume a withholding slot"
            raise ValueError(msg)
        if not Decimal(0) < self.pay_fraction <= _ONE:
            msg = f"pay_fraction must be in (0, 1]; got {self.pay_fraction}"
            raise ValueError(msg)


@dataclass(frozen=True)
class WithholdingSchedule:
    """Ordered IRPEF withholding slots of a payroll year.

    The annual IRPEF projection and the year-end conguaglio (art. 23 c. 3
    DPR 600/1973) run on these slots: the tax still due is spread over the
    slots not yet closed, and the last slot settles the balance on the final
    taxable income.  There is one slot per payslip, so a fractional extra
    month keeps its own slot.

    Attributes:
        year: The tax year.
        slots: Slots in payment order, at least one.
    """

    year: int
    slots: tuple[WithholdingSlot, ...]

    def __post_init__(self) -> None:  # noqa: D105
        if not self.slots:
            msg = "WithholdingSchedule needs at least one slot"
            raise ValueError(msg)
        PayrollSchedule(year=self.year, runs=tuple(s.run for s in self.slots))

    @classmethod
    def from_calendar(cls, calendar: WorkCalendar) -> WithholdingSchedule:
        """Build the withholding schedule of a full-year calendar.

        Args:
            calendar: Year-level payroll calendar.

        Returns:
            :meth:`for_runs` of every run of
            :meth:`PayrollSchedule.from_calendar`.
        """
        return cls.for_runs(PayrollSchedule.from_calendar(calendar), calendar)

    @classmethod
    def for_runs(
        cls, schedule: PayrollSchedule, calendar: WorkCalendar
    ) -> WithholdingSchedule:
        """Build the withholding schedule of the runs actually selected.

        Args:
            schedule: The runs of the year, possibly fewer than the calendar
                generates when the employment covers part of the year.
            calendar: Calendar of ``schedule``, which sets the extra-month
                fractions.

        Returns:
            One slot per run of ``schedule``, with the extra months carrying
            their ``max_fraction``.  An empty ``schedule`` is rejected by
            the constructor, which needs at least one slot.
        """
        fractions = {e.kind.value: e.max_fraction for e in calendar.extra_months}
        return cls(
            year=schedule.year,
            slots=tuple(
                WithholdingSlot(run, fractions.get(run.run_kind, _ONE))
                for run in schedule.runs
            ),
        )

    @property
    def run_count(self) -> PayrollRunCount:
        """Number of payslips holding a withholding slot."""
        return PayrollRunCount(len(self.slots))

    def remaining(self, slots_closed: int) -> int:
        """Return the slots left including the current one, at least 1.

        Once every slot is closed the current run is treated as the last
        one, so it still settles the balance.

        Args:
            slots_closed: Withholding slots already closed this tax year.

        Returns:
            ``max(1, len(slots) - slots_closed)``.
        """
        return max(1, len(self.slots) - slots_closed)

    def upcoming(self, slots_closed: int) -> tuple[WithholdingSlot, ...]:
        """Return the slots after the current one.

        Args:
            slots_closed: Withholding slots already closed this tax year; the
                current run takes slot ``slots_closed``.

        Returns:
            The slots still to come after the current run, possibly empty.
        """
        return self.slots[slots_closed + 1 :]
