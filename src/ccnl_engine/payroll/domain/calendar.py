"""Payroll calendar: year-level schedule with extra months.

A :class:`WorkCalendar` describes when the regular 12 payroll periods fall
and how many extra contractual months (e.g. tredicesima, quattordicesima) are
paid and in which calendar month.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = ["ExtraMonthKind", "ExtraMonthSchedule", "WorkCalendar"]

_MAX_ADDITIONAL_MONTHS = 14


class ExtraMonthKind(Enum):
    """Typed kind for an extra contractual month.

    Used by :class:`ExtraMonthSchedule` and :class:`PayrollSchedule` to
    determine which :class:`~ccnl_engine.payroll.domain.run.PayrollRun`
    factory to call.  Do not infer the kind from the human-readable name.
    """

    THIRTEENTH = "thirteenth"
    FOURTEENTH = "fourteenth"


@dataclass(frozen=True)
class ExtraMonthSchedule:
    """Schedule for one extra contractual month.

    Attributes:
        kind: Typed kind identifying the extra month.  Used by the schedule
            builder to select the correct run kind without substring inference.
        name: Human-readable name (e.g. ``"tredicesima"``).
        payment_month: Calendar month (1-12) in which the extra month is paid.
    """

    kind: ExtraMonthKind
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
        seen: set[tuple[ExtraMonthKind, int]] = set()
        for sched in self.extra_months:
            key = (sched.kind, sched.payment_month)
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
        thirteenth_payment_month: int = 12,
        fourteenth_payment_month: int = 6,
    ) -> WorkCalendar:
        """Build a calendar from a CCNL ``additional_months`` parameter.

        For ``additional_months=13`` (12 regular + 1 tredicesima) this
        produces one :class:`ExtraMonthSchedule` paid in December.
        For ``additional_months=14`` it produces tredicesima (December) and
        quattordicesima in ``fourteenth_payment_month`` (default June).

        Args:
            year: Tax year.
            additional_months: Value from CCNL parameters (13 or 14).
                Values outside the range 12-14 raise :class:`ValueError`.
            thirteenth_payment_month: Calendar month for the tredicesima.
                Defaults to December (12).
            fourteenth_payment_month: Calendar month for the quattordicesima.
                Defaults to June (6).

        Returns:
            :class:`WorkCalendar` with ``max(0, additional_months - 12)``
            extra schedules.

        Raises:
            ValueError: When ``additional_months`` exceeds
                :data:`_MAX_ADDITIONAL_MONTHS` (currently 14).
        """
        if additional_months < 12:
            msg = (
                f"additional_months={additional_months} is below the minimum "
                f"of 12; a CCNL must have at least 12 regular months"
            )
            raise ValueError(msg)
        if additional_months > _MAX_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={additional_months} exceeds the maximum "
                f"supported value of {_MAX_ADDITIONAL_MONTHS}; "
                f"only CCNL contracts with up to {_MAX_ADDITIONAL_MONTHS} "
                f"months are supported"
            )
            raise ValueError(msg)
        schedules: list[ExtraMonthSchedule] = []
        if additional_months >= 13:
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=thirteenth_payment_month,
                )
            )
        if additional_months >= 14:
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.FOURTEENTH,
                    name="quattordicesima",
                    payment_month=fourteenth_payment_month,
                )
            )
        return cls(year=year, extra_months=tuple(schedules))
