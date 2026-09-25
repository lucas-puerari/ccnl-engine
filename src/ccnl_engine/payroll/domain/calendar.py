"""Payroll calendar: year-level schedule with extra months.

A :class:`WorkCalendar` describes when the regular 12 payroll periods fall
and how many extra contractual months (e.g. tredicesima, quattordicesima) are
paid and in which calendar month.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

__all__ = ["ExtraMonthKind", "ExtraMonthSchedule", "WorkCalendar"]

_MAX_ADDITIONAL_MONTHS = Decimal(14)
_MIN_ADDITIONAL_MONTHS = Decimal(12)


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
        accrual_window_start_month: First calendar month of the 12-month
            accrual window.  When ``1``, the window is entirely within the
            current tax year (January-December).  When greater than
            ``payment_month``, the window crosses the year boundary (e.g. 7
            for a July-June quattordicesima paid in June).  Defaults to ``1``.
        max_fraction: Maximum entitlement fraction of one base monthly salary.
            ``Decimal("1")`` for a full extra month, ``Decimal("0.5")`` for a
            CCNL granting half a month (e.g. cooperative-sociali-style
            ``additional_months=13.5``).  Defaults to ``Decimal("1")``.
    """

    kind: ExtraMonthKind
    name: str
    payment_month: int
    accrual_window_start_month: int = 1
    max_fraction: Decimal = field(default_factory=lambda: Decimal(1))

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
        if not 1 <= self.accrual_window_start_month <= 12:
            msg = (
                f"ExtraMonthSchedule.accrual_window_start_month must be 1-12; "
                f"got {self.accrual_window_start_month}"
            )
            raise ValueError(msg)
        if not (Decimal(0) < self.max_fraction <= Decimal(1)):
            msg = (
                f"ExtraMonthSchedule.max_fraction must be in (0, 1]; "
                f"got {self.max_fraction}"
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
        seen_kinds: set[ExtraMonthKind] = set()
        for sched in self.extra_months:
            if sched.kind in seen_kinds:
                msg = (
                    f"duplicate extra-month kind {sched.kind.value!r}: "
                    f"each ExtraMonthKind may appear at most once"
                )
                raise ValueError(msg)
            seen_kinds.add(sched.kind)
        if (
            ExtraMonthKind.FOURTEENTH in seen_kinds
            and ExtraMonthKind.THIRTEENTH not in seen_kinds
        ):
            msg = (
                "a fourteenth month requires a thirteenth month: "
                "add ExtraMonthKind.THIRTEENTH to the calendar first"
            )
            raise ValueError(msg)

    @classmethod
    def from_additional_months(
        cls,
        year: int,
        additional_months: int | Decimal,
        *,
        thirteenth_payment_month: int = 12,
        fourteenth_payment_month: int = 6,
    ) -> WorkCalendar:
        """Build a calendar from a CCNL ``additional_months`` parameter.

        Accepts fractional values (e.g. ``Decimal("13.5")``).  A fractional
        fourteenth month is added with :attr:`ExtraMonthSchedule.max_fraction`
        set to the fractional part so the caller receives the correct partial
        entitlement without discarding it.

        For ``additional_months=13`` (12 regular + 1 tredicesima) this
        produces one :class:`ExtraMonthSchedule` paid in December.
        For ``additional_months=14`` it produces tredicesima (December) and
        quattordicesima in ``fourteenth_payment_month`` (default June).
        For ``additional_months=13.5`` it produces tredicesima (full) and a
        half quattordicesima (``max_fraction=Decimal("0.5")``).

        Args:
            year: Tax year.
            additional_months: Value from CCNL parameters (13, 13.5 or 14).
                Values outside the range 12-14 raise :class:`ValueError`.
                Accepts ``int`` or ``Decimal``; fractional parts are preserved.
            thirteenth_payment_month: Calendar month for the tredicesima.
                Defaults to December (12).
            fourteenth_payment_month: Calendar month for the quattordicesima.
                Defaults to June (6).

        Returns:
            :class:`WorkCalendar` with up to two extra schedules.

        Raises:
            ValueError: When ``additional_months`` is outside the range
                ``[12, 14]``.
        """
        am = Decimal(str(additional_months))
        if am < _MIN_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={am} is below the minimum "
                f"of 12; a CCNL must have at least 12 regular months"
            )
            raise ValueError(msg)
        if am > _MAX_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={am} exceeds the maximum "
                f"supported value of {_MAX_ADDITIONAL_MONTHS}; "
                f"only CCNL contracts with up to {_MAX_ADDITIONAL_MONTHS} "
                f"months are supported"
            )
            raise ValueError(msg)
        # Accrual window start for the quattordicesima: the month after the
        # payment month (wrapping at December → January).
        fourteenth_window_start = (fourteenth_payment_month % 12) + 1
        schedules: list[ExtraMonthSchedule] = []
        if am >= 13:
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=thirteenth_payment_month,
                    accrual_window_start_month=1,
                    max_fraction=Decimal(1),
                )
            )
        if am >= 14:
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.FOURTEENTH,
                    name="quattordicesima",
                    payment_month=fourteenth_payment_month,
                    accrual_window_start_month=fourteenth_window_start,
                    max_fraction=Decimal(1),
                )
            )
        elif am > 13:
            fraction = am - 13
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.FOURTEENTH,
                    name="quattordicesima",
                    payment_month=fourteenth_payment_month,
                    accrual_window_start_month=fourteenth_window_start,
                    max_fraction=fraction,
                )
            )
        return cls(year=year, extra_months=tuple(schedules))
