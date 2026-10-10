"""Absence and sick-leave events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import (
    require_bool,
    require_date,
    require_decimal,
    require_int,
)

if TYPE_CHECKING:
    from datetime import date

_ZERO = Decimal(0)

__all__ = ["AbsenceEvent", "SickLeaveEvent"]


@dataclass(frozen=True)
class AbsenceEvent:
    """Unpaid absence: deducted via EMPLOYEE_DEDUCTIONS; reduces INPS and TFR base.

    Attributes:
        event_date: Start date (or sole date) of the absence.
        hours: Number of absent hours.  Must be > 0.
        hourly_rate: Rate at which the pay is deducted in EUR.  Must be > 0.
        end_date: Last day of the absence range.  ``None`` for single-day
            absences where ``event_date`` is both start and end.
            When set must be >= ``event_date``.
        suspends_accrual: ``True`` when the absence suspends the
            employment, so its calendar days do not accrue tredicesima and
            quattordicesima ratei (for example aspettativa non retribuita,
            or the congedo for serious family reasons of art. 4 c. 2
            L. 53/2000); ``False`` when its days accrue the ratei.  The
            caller states it: the engine does not decide which absences
            suspend accrual under the CCNL.  ``None`` means not known: the
            days count as accruing, and a rateo they could change has a
            ``missing_fact`` blocker.
        no_pay_due: ``True`` when no pay at all is due for every calendar
            day of the absence (aspettativa senza assegni): the days leave
            the days of the art. 13 TUIR deductions (AdE circ. 15/E/2007 par.
            1.5.1: "vanno sottratti i giorni per i quali non spetta alcuna
            retribuzione").  ``False`` for a strike, an absence of hours or
            one whose days stay paid in part, which reduce nothing ("nessuna
            riduzione [...] in caso di giornate di sciopero").  ``None`` means
            not known: the days stay counted and a withholding run has a
            ``missing_fact`` blocker.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    end_date: date | None = None
    suspends_accrual: bool | None = None
    no_pay_due: bool | None = None

    def __post_init__(self) -> None:  # noqa: D105
        feature = "absence"
        require_date(self.event_date, "AbsenceEvent.event_date", feature=feature)
        require_decimal(
            self.hours, "AbsenceEvent.hours", feature=feature, positive=True
        )
        require_decimal(
            self.hourly_rate, "AbsenceEvent.hourly_rate", feature=feature, positive=True
        )
        require_date(
            self.end_date, "AbsenceEvent.end_date", feature=feature, optional=True
        )
        for name in ("suspends_accrual", "no_pay_due"):
            if getattr(self, name) is not None:
                require_bool(
                    getattr(self, name), f"AbsenceEvent.{name}", feature=feature
                )
        if self.end_date is not None and self.end_date < self.event_date:
            msg = (
                f"AbsenceEvent.end_date ({self.end_date}) must be "
                f">= event_date ({self.event_date})"
            )
            raise InvalidInputError(msg, field="AbsenceEvent.end_date", feature=feature)

    @property
    def days(self) -> tuple[date, ...]:
        """Calendar days of the absence, first to last."""
        last = self.end_date or self.event_date
        count = (last - self.event_date).days + 1
        return tuple(self.event_date + timedelta(days=n) for n in range(count))


@dataclass(frozen=True)
class SickLeaveEvent:
    """Sick pay amount set by the caller: an explicit, never payable override.

    The engine computes sickness from a
    :class:`~ccnl_engine.payroll.domain.sickness.SicknessEpisode`.  This
    event overrides that computation with an employer-paid amount the
    caller computed; the run records a caller-supplied decision for the
    ``sickness`` capability, so its result is not payable.  The amount is
    subject to INPS and IRPEF but not TFR accrual.

    The engine deducts the carenza (waiting-period) portion from *amount*:
    ``net = amount - (amount / sick_days * waiting_period_days)``.

    Attributes:
        event_date: First day of the sick-leave period.
        amount: Total employer-liable sick-leave gross in EUR, before carenza
            deduction.
        sick_days: Total working days of the sick-leave spell.  Must be >= 1.
            Used to compute the daily rate for the carenza deduction.
            Defaults to 1.
        waiting_period_days: Number of carenza days (waiting period) at the
            start of the sick-leave period.  Must not exceed sick_days.
            Defaults to 0 (no carenza).
    """

    event_date: date
    amount: Decimal
    sick_days: int = 1
    waiting_period_days: int = 0

    def __post_init__(self) -> None:  # noqa: D105
        feature = "sick_leave"
        require_date(self.event_date, "SickLeaveEvent.event_date", feature=feature)
        require_decimal(
            self.amount, "SickLeaveEvent.amount", feature=feature, minimum=_ZERO
        )
        require_int(
            self.sick_days, "SickLeaveEvent.sick_days", feature=feature, minimum=1
        )
        require_int(
            self.waiting_period_days,
            "SickLeaveEvent.waiting_period_days",
            feature=feature,
            minimum=0,
        )
        if self.waiting_period_days > self.sick_days:
            msg = (
                f"SickLeaveEvent.waiting_period_days ({self.waiting_period_days}) "
                f"must not exceed sick_days ({self.sick_days})"
            )
            raise InvalidInputError(
                msg, field="SickLeaveEvent.waiting_period_days", feature=feature
            )
