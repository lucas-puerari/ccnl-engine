"""Absence and sick-leave events."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.sickness import SicknessCase

__all__ = ["AbsenceEvent", "SickLeaveEvent", "SicknessCaseEvent"]


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
            L. 53/2000).  The caller states it: the engine does not decide
            which absences suspend accrual under the CCNL.  Defaults to
            ``False``: an unpaid absence reduces pay, not the ratei.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    end_date: date | None = None
    suspends_accrual: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        if self.hours <= 0:
            msg = f"AbsenceEvent.hours must be > 0; got {self.hours}"
            raise InvalidInputError(msg, feature="absence")
        if self.hourly_rate <= 0:
            msg = f"AbsenceEvent.hourly_rate must be > 0; got {self.hourly_rate}"
            raise InvalidInputError(msg, feature="absence")
        if self.end_date is not None and self.end_date < self.event_date:
            msg = (
                f"AbsenceEvent.end_date ({self.end_date}) must be "
                f">= event_date ({self.event_date})"
            )
            raise InvalidInputError(msg, feature="absence")


@dataclass(frozen=True)
class SickLeaveEvent:
    """Sick leave — employer-paid portion only.

    The INPS-paid portion (if any) flows outside the payroll run and is
    not included here.  The employer portion is subject to INPS and IRPEF
    but not TFR accrual.

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
        if self.amount < 0:
            msg = f"SickLeaveEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="sick_leave")
        if self.sick_days < 1:
            msg = f"SickLeaveEvent.sick_days must be >= 1; got {self.sick_days}"
            raise InvalidInputError(msg, feature="sick_leave")
        if self.waiting_period_days < 0:
            msg = (
                f"SickLeaveEvent.waiting_period_days must be >= 0; "
                f"got {self.waiting_period_days}"
            )
            raise InvalidInputError(msg, feature="sick_leave")
        if self.waiting_period_days > self.sick_days:
            msg = (
                f"SickLeaveEvent.waiting_period_days ({self.waiting_period_days}) "
                f"must not exceed sick_days ({self.sick_days})"
            )
            raise InvalidInputError(msg, feature="sick_leave")


@dataclass(frozen=True)
class SicknessCaseEvent:
    """Structured sick-leave episode with INPS indemnity and employer integration.

    Wraps a :class:`~ccnl_engine.payroll.domain.sickness.SicknessCase` to
    participate in the event pipeline.  Unlike :class:`SickLeaveEvent`, which
    requires the caller to pre-compute amounts, this event lets the engine
    derive the absence deduction, INPS indemnity, and employer integration
    from the episode details.

    Attributes:
        event_date: First day of the sick-leave episode (= ``case.episode_start``).
            Must equal ``case.episode_start``.
        case: The full sickness episode model.
    """

    event_date: date
    case: SicknessCase

    def __post_init__(self) -> None:  # noqa: D105
        if self.event_date < self.case.episode_start:
            msg = (
                f"SicknessCaseEvent.event_date ({self.event_date}) must be >= "
                f"case.episode_start ({self.case.episode_start})"
            )
            raise InvalidInputError(msg, feature="sickness")
