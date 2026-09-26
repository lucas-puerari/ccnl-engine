"""Payroll calendar: year-level schedule with extra months.

A :class:`WorkCalendar` describes when the regular 12 payroll periods fall
and how many extra contractual months (e.g. tredicesima, quattordicesima) are
paid and in which calendar month.

The CCNL ``additional_months`` parameter is an :class:`ExtraMonthEntitlement`:
equivalent months of pay per year, possibly fractional (13.5).  It is not a
count of payslips; see :class:`~ccnl_engine.payroll.domain.schedule.PayrollRunCount`
and :class:`~ccnl_engine.payroll.domain.schedule.WithholdingSchedule`.

The standard calendar is always derived from the CCNL; a caller replaces it
only through a
:class:`~ccnl_engine.payroll.domain.calendar_override.CalendarOverride`.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

__all__ = [
    "AccrualWindow",
    "ExtraMonthEntitlement",
    "ExtraMonthKind",
    "ExtraMonthSchedule",
    "WorkCalendar",
]

_MAX_ADDITIONAL_MONTHS = Decimal(14)
_MIN_ADDITIONAL_MONTHS = Decimal(12)
_WITH_THIRTEENTH = Decimal(13)


def _require_decimal(value: object) -> None:
    if not isinstance(value, Decimal):
        msg = f"additional_months must be a Decimal; got {type(value).__name__}"
        raise TypeError(msg)


@dataclass(frozen=True)
class ExtraMonthEntitlement:
    """Equivalent months of pay per year: 12 regular months plus extra months.

    The value is a :class:`~decimal.Decimal` and may be fractional: ``13.5``
    means a full tredicesima plus half a quattordicesima.  It says how much
    is paid, not how many payslips are issued; a fractional extra month is
    still paid in its own run.

    Attributes:
        value: Equivalent months, between 12 and 14 inclusive.
    """

    value: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        _require_decimal(self.value)
        if not self.value.is_finite() or self.value < _MIN_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={self.value} is below the minimum "
                f"of 12; a CCNL must have at least 12 regular months"
            )
            raise ValueError(msg)
        if self.value > _MAX_ADDITIONAL_MONTHS:
            msg = (
                f"additional_months={self.value} exceeds the maximum "
                f"supported value of {_MAX_ADDITIONAL_MONTHS}; "
                f"only CCNL contracts with up to {_MAX_ADDITIONAL_MONTHS} "
                f"months are supported"
            )
            raise ValueError(msg)

    @classmethod
    def of(cls, value: int | Decimal) -> ExtraMonthEntitlement:
        """Build an entitlement from a CCNL parameter value.

        Args:
            value: Equivalent months as ``int`` or ``Decimal``.  Converted
                through ``str`` so no binary rounding is introduced.

        Returns:
            The validated :class:`ExtraMonthEntitlement`.
        """
        return cls(Decimal(str(value)))


@dataclass(frozen=True)
class AccrualWindow:
    """Dates over which one extra-month run accrues.

    Attributes:
        nominal_start: First day of the contractual 12-month window, in the
            previous year when the window crosses the year boundary.
        start: First day counted for this employment: ``nominal_start``,
            or the hire date when the worker was hired later.  Months
            before the hire date are never part of the window.
        end: Last day of the payment month.

    Raises:
        ValueError: When the dates are not ordered
            ``nominal_start <= start <= end``.
    """

    nominal_start: date
    start: date
    end: date

    def __post_init__(self) -> None:  # noqa: D105
        if not self.nominal_start <= self.start <= self.end:
            msg = (
                f"accrual window dates must satisfy nominal_start <= start <= "
                f"end; got {self.nominal_start}, {self.start}, {self.end}"
            )
            raise ValueError(msg)


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

    def accrual_window(
        self, year: int, started_on: date | None = None
    ) -> AccrualWindow:
        """Return the accrual window of this extra month paid in ``year``.

        Args:
            year: Tax year of the payment.
            started_on: Hire date, or ``None`` when not tracked.  A window
                opening before it is clipped to it.

        Returns:
            The window from ``accrual_window_start_month`` (of the previous
            year when it follows ``payment_month``) to the end of
            ``payment_month``.
        """
        crosses_year = self.accrual_window_start_month > self.payment_month
        start_year = year - 1 if crosses_year else year
        nominal_start = date(start_year, self.accrual_window_start_month, 1)
        last_day = calendar.monthrange(year, self.payment_month)[1]
        start = nominal_start if started_on is None else max(nominal_start, started_on)
        return AccrualWindow(
            nominal_start=nominal_start,
            start=start,
            end=date(year, self.payment_month, last_day),
        )


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
        return ExtraMonthEntitlement(_MIN_ADDITIONAL_MONTHS + extra)

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
        if _MIN_ADDITIONAL_MONTHS < am < _WITH_THIRTEENTH:
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
        if am >= _MAX_ADDITIONAL_MONTHS:
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
