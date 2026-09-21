"""Variable work events for the period-first payroll engine.

Each event type carries the data needed to compute its gross amount and
accounting treatment (INPS, IRPEF, TFR bases).  Events are passed on
:class:`~ccnl_engine.payroll.domain.period.PeriodCalculationRequest` and
processed in ``calculate_period``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

__all__ = [
    "AbsenceEvent",
    "BonusEvent",
    "FringeEvent",
    "HolidayWorkEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "SickLeaveEvent",
    "WelfareEvent",
    "WorkEvent",
]

_FRINGE_THRESHOLD_DEFAULT = Decimal("258.23")


@dataclass(frozen=True)
class OvertimeEvent:
    """Overtime hours: INPS + IRPEF + TFR on computed gross.

    Attributes:
        event_date: Calendar date the overtime was worked.
        hours: Number of overtime hours.
        hourly_rate: Base hourly rate in EUR.
        multiplier: Overtime multiplier applied to the hourly rate (e.g.
            ``1.25`` for 25% supplement).
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    multiplier: Decimal = Decimal("1.25")


@dataclass(frozen=True)
class NightShiftEvent:
    """Night-shift supplement: INPS + IRPEF + TFR on the supplement amount.

    Attributes:
        event_date: Calendar date the shift was worked.
        supplement_amount: Flat supplement for the night period in EUR.
    """

    event_date: date
    supplement_amount: Decimal


@dataclass(frozen=True)
class HolidayWorkEvent:
    """Holiday-work supplement: INPS + IRPEF on the supplement amount.

    TFR is not accrued on holiday supplements under the standard Italian
    treatment (art. 2120 c.c. excludes accidental pay).

    Attributes:
        event_date: Calendar date the holiday was worked.
        supplement_amount: Flat supplement for the holiday in EUR.
    """

    event_date: date
    supplement_amount: Decimal


@dataclass(frozen=True)
class AbsenceEvent:
    """Unpaid absence: reduces gross, INPS base, TFR base, and taxable income.

    Attributes:
        event_date: Calendar date of the absence.
        hours: Number of absent hours.
        hourly_rate: Rate at which the pay is deducted in EUR.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal


@dataclass(frozen=True)
class SickLeaveEvent:
    """Sick leave — employer-paid portion only.

    The INPS-paid portion (if any) flows outside the payroll run and is
    not included here.  The employer portion is subject to INPS and IRPEF
    but not TFR accrual.

    Attributes:
        event_date: First day of the sick-leave period.
        amount: Gross amount paid by the employer in EUR.
    """

    event_date: date
    amount: Decimal


@dataclass(frozen=True)
class BonusEvent:
    """One-off bonus (mensilità aggiuntiva, PDR, etc.): INPS + IRPEF + TFR.

    Attributes:
        event_date: Date the bonus is attributed to.
        amount: Gross bonus amount in EUR.
    """

    event_date: date
    amount: Decimal


@dataclass(frozen=True)
class FringeEvent:
    """Fringe benefit (art. 51 co. 3 TUIR).

    If the total fringe amount exceeds ``exempt_threshold``, the full amount
    is subject to INPS and IRPEF.  If it is at or below the threshold, it
    is entirely exempt from both.

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the fringe benefit in EUR.
        exempt_threshold: Exemption threshold.  Defaults to the standard
            TUIR threshold (€258.23).  Callers should pass the applicable
            threshold for the fiscal year and employee situation.
    """

    event_date: date
    amount: Decimal
    exempt_threshold: Decimal = _FRINGE_THRESHOLD_DEFAULT


@dataclass(frozen=True)
class WelfareEvent:
    """Welfare benefit: exempt from INPS and IRPEF, no TFR accrual.

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the welfare benefit in EUR.
    """

    event_date: date
    amount: Decimal


WorkEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | BonusEvent
    | FringeEvent
    | WelfareEvent
)
