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

    def __post_init__(self) -> None:  # noqa: D105
        if not self.name:
            msg = "ExtraMonthSchedule.name must not be empty"
            raise ValueError(msg)
        if not 1 <= self.payment_month <= 12:
            msg = (
                f"ExtraMonthSchedule.payment_month must be 1-12; "
                f"got {self.payment_month}"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class WorkCalendar:
    """Year-level payroll calendar with extra-month schedule.

    Attributes:
        year: The tax year this calendar applies to.
        extra_months: Ordered tuple of extra-month payment schedules.
    """

    year: int
    extra_months: tuple[ExtraMonthSchedule, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:  # noqa: D105
        if self.year < 1970:
            msg = f"WorkCalendar.year must be >= 1970; got {self.year}"
            raise ValueError(msg)
        seen: set[tuple[str, int]] = set()
        for sched in self.extra_months:
            key = (sched.name.lower(), sched.payment_month)
            if key in seen:
                msg = (
                    f"duplicate extra-month schedule "
                    f"'{sched.name}' in month {sched.payment_month}"
                )
                raise ValueError(msg)
            seen.add(key)

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
        For ``additional_months=14`` it produces tredicesima (December) and
        quattordicesima (``extra_payment_month``).

        Args:
            year: Tax year.
            additional_months: Value from CCNL parameters (typically 13 or 14).
            extra_month_name: Name for the first extra month (tredicesima).
                Ignored for the second extra month, which is always named
                ``"quattordicesima"``.
            extra_payment_month: Calendar month for the first extra month.
                The quattordicesima (if any) also uses this month.

        Returns:
            :class:`WorkCalendar` with ``max(0, additional_months - 12)``
            extra schedules, each with a distinct name.
        """
        extra_count = max(0, additional_months - 12)
        canonical_names = [extra_month_name, "quattordicesima", "quindicesima"]
        schedules = tuple(
            ExtraMonthSchedule(
                name=canonical_names[min(i, len(canonical_names) - 1)],
                payment_month=extra_payment_month,
            )
            for i in range(extra_count)
        )
        return cls(year=year, extra_months=schedules)
