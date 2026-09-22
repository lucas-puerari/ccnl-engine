"""Payroll calendar: year-level schedule with extra months.

A :class:`WorkCalendar` describes when the regular 12 payroll periods fall
and how many extra contractual months (e.g. tredicesima, quattordicesima) are
paid and in which calendar month.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["ExtraMonthSchedule", "WorkCalendar"]


@dataclass(frozen=True)
class ExtraMonthSchedule:
    """Schedule for one extra contractual month.

    Attributes:
        name: Human-readable name (e.g. ``"tredicesima"``).
        payment_month: Calendar month (1-12) in which the extra month is paid.
    """

    name: str
    payment_month: int


@dataclass(frozen=True)
class WorkCalendar:
    """Year-level payroll calendar with extra-month schedule.

    Attributes:
        year: The tax year this calendar applies to.
        extra_months: Ordered tuple of extra-month payment schedules.
    """

    year: int
    extra_months: tuple[ExtraMonthSchedule, ...] = field(default_factory=tuple)

    @classmethod
    def from_additional_months(
        cls,
        year: int,
        additional_months: int,
        *,
        extra_month_name: str = "tredicesima",
        extra_payment_month: int = 12,
    ) -> WorkCalendar:
        """Build a calendar from a CCNL ``additional_months`` parameter.

        For ``additional_months=13`` (12 regular + 1 tredicesima) this
        produces one :class:`ExtraMonthSchedule` paid in December.

        Args:
            year: Tax year.
            additional_months: Value from CCNL parameters (typically 13 or 14).
            extra_month_name: Name applied to each extra month schedule.
            extra_payment_month: Calendar month in which extra months are paid.

        Returns:
            :class:`WorkCalendar` with ``max(0, additional_months - 12)``
            extra schedules.
        """
        extra_count = max(0, additional_months - 12)
        schedules = tuple(
            ExtraMonthSchedule(name=extra_month_name, payment_month=extra_payment_month)
            for _ in range(extra_count)
        )
        return cls(year=year, extra_months=schedules)
