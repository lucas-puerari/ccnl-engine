"""Payroll calendar: year-level schedule with extra months.

A :class:`WorkCalendar` describes when the regular 12 payroll periods fall
and how many extra contractual months (e.g. tredicesima, quattordicesima) are
paid and in which calendar month.

Its :attr:`~WorkCalendar.entitlement` is an
:class:`~ccnl_engine.payroll.domain.extra_month_entitlement.ExtraMonthEntitlement`;
each extra month is an
:class:`~ccnl_engine.payroll.domain.extra_month_schedule.ExtraMonthSchedule`.

The standard calendar is always derived from the CCNL; a caller replaces it
only through a
:class:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ccnl_engine.payroll.domain.extra_month_entitlement import (
    MAX_ADDITIONAL_MONTHS,
    MIN_ADDITIONAL_MONTHS,
    ExtraMonthEntitlement,
)
from ccnl_engine.payroll.domain.extra_month_schedule import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)

__all__ = ["WorkCalendar"]

_WITH_THIRTEENTH = Decimal(13)


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

    @property
    def entitlement(self) -> ExtraMonthEntitlement:
        """Equivalent months of pay granted by this calendar.

        Twelve regular months plus the ``max_fraction`` of each extra month,
        so a full tredicesima and half a quattordicesima give ``13.5``.
        """
        extra = sum((s.max_fraction for s in self.extra_months), Decimal(0))
        return ExtraMonthEntitlement(MIN_ADDITIONAL_MONTHS + extra)

    @classmethod
    def from_additional_months(
        cls,
        year: int,
        additional_months: int | Decimal | ExtraMonthEntitlement,
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
            additional_months: Value from CCNL parameters (13, 13.5 or 14),
                as :class:`ExtraMonthEntitlement`, ``int`` or ``Decimal``.
                Fractional parts are preserved.
            thirteenth_payment_month: Calendar month for the tredicesima.
                Defaults to December (12).
            fourteenth_payment_month: Calendar month for the quattordicesima.
                Defaults to June (6).

        Returns:
            :class:`WorkCalendar` with up to two extra schedules.

        Raises:
            ValueError: When ``additional_months`` is outside the range
                ``[12, 14]``, or strictly between 12 and 13: a partial
                tredicesima is not a supported calendar and would otherwise
                be dropped silently.
        """
        entitlement = (
            additional_months
            if isinstance(additional_months, ExtraMonthEntitlement)
            else ExtraMonthEntitlement.of(additional_months)
        )
        am = entitlement.value
        if MIN_ADDITIONAL_MONTHS < am < _WITH_THIRTEENTH:
            msg = (
                f"additional_months={am} grants a partial tredicesima, "
                f"which is not supported; use 12, 13 or a value up to 14"
            )
            raise ValueError(msg)
        # Accrual window start for the quattordicesima: the month after the
        # payment month (wrapping at December → January).
        fourteenth_window_start = (fourteenth_payment_month % 12) + 1
        schedules: list[ExtraMonthSchedule] = []
        if am >= _WITH_THIRTEENTH:
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=thirteenth_payment_month,
                    accrual_window_start_month=1,
                    max_fraction=Decimal(1),
                )
            )
        if am >= MAX_ADDITIONAL_MONTHS:
            schedules.append(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.FOURTEENTH,
                    name="quattordicesima",
                    payment_month=fourteenth_payment_month,
                    accrual_window_start_month=fourteenth_window_start,
                    max_fraction=Decimal(1),
                )
            )
        elif am > _WITH_THIRTEENTH:
            fraction = am - _WITH_THIRTEENTH
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
