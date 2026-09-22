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

    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId

__all__ = [
    "AbsenceEvent",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "HolidayWorkEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "SickLeaveEvent",
    "TerminationTFREvent",
    "WelfareEvent",
    "WorkEvent",
]


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
        event_date: Start date (or sole date) of the absence.
        hours: Number of absent hours.
        hourly_rate: Rate at which the pay is deducted in EUR.
        end_date: Last day of the absence range.  ``None`` for single-day
            absences where ``event_date`` is both start and end.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    end_date: date | None = None


@dataclass(frozen=True)
class SickLeaveEvent:
    """Sick leave — employer-paid portion only.

    The INPS-paid portion (if any) flows outside the payroll run and is
    not included here.  The employer portion is subject to INPS and IRPEF
    but not TFR accrual.

    Attributes:
        event_date: First day of the sick-leave period.
        amount: Gross amount paid by the employer in EUR.
        waiting_period_days: Number of carenza days (waiting period) at the
            start of the sick-leave period.  Defaults to 0.
    """

    event_date: date
    amount: Decimal
    waiting_period_days: int = 0


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

    The annual exemption threshold is resolved by ``calculate_period`` from
    the year-level ``VariablePayRules.fringe_benefit`` policy — it is not
    carried on the event itself.  Taxability is determined cumulatively
    across all fringe events in the year (YTD + current period).

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the fringe benefit in EUR.
    """

    event_date: date
    amount: Decimal


@dataclass(frozen=True)
class WelfareEvent:
    """Welfare benefit: exempt from INPS and IRPEF, no TFR accrual.

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the welfare benefit in EUR.
    """

    event_date: date
    amount: Decimal


@dataclass(frozen=True)
class ArrearsEvent:
    """Contract renewal arrears subject to tassazione separata (art. 17 TUIR).

    Attributes:
        event_date: Date the arrears are attributed to.
        amount: Gross arrears amount in EUR.
        separate_tax_rate: Caller-supplied average IRPEF rate from the
            two prior tax years, applied as tassazione separata.
        reference_period: The competence period from which the arrears
            originate (e.g. the period of the back-dated contract renewal).
            ``None`` when the reference period is not tracked.
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal
    reference_period: PeriodId | None = None


@dataclass(frozen=True)
class BilateralFundEvent:
    """Bilateral or health fund contribution (fondi bilaterali/sanitari).

    Both employee and employer portions are expressed as gross amounts.
    The employee portion reduces net pay; the employer portion increases
    employer cost.

    Attributes:
        event_date: Date the contribution is attributed to.
        employee_amount: Employee-side contribution in EUR.
        employer_amount: Employer-side contribution in EUR.
    """

    event_date: date
    employee_amount: Decimal
    employer_amount: Decimal


@dataclass(frozen=True)
class TerminationTFREvent:
    """TFR settlement at cessazione (art. 19 TUIR, tassazione separata).

    The caller supplies the applicable tax rate (determined via art. 19
    TUIR using the employee's prior-year average IRPEF rate).

    Attributes:
        event_date: Date of cessazione.
        amount: Total TFR payout in EUR.
        separate_tax_rate: Applicable tassazione separata rate.
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal


WorkEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | BonusEvent
    | FringeEvent
    | WelfareEvent
    | ArrearsEvent
    | BilateralFundEvent
    | TerminationTFREvent
)
