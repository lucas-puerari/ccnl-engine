"""Schedule of one extra contractual month and its accrual window."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

from ccnl_engine.validation import (
    reject,
    require_decimal,
    require_int,
    require_str,
)

__all__ = ["AccrualWindow", "ExtraMonthKind", "ExtraMonthSchedule"]


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
    determine which :class:`~ccnl_engine.payroll.period.models_run.PayrollRun`
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
        owner, feature = "ExtraMonthSchedule", "calendar"
        if not isinstance(self.kind, ExtraMonthKind):
            reject(f"{owner}.kind", "an ExtraMonthKind", self.kind, feature=feature)
        require_str(self.name, f"{owner}.name", feature=feature, non_blank=True)
        for name in ("payment_month", "accrual_window_start_month"):
            require_int(
                getattr(self, name),
                f"{owner}.{name}",
                feature=feature,
                minimum=1,
                maximum=12,
            )
        require_decimal(
            self.max_fraction,
            f"{owner}.max_fraction",
            feature=feature,
            positive=True,
            maximum=Decimal(1),
        )

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
