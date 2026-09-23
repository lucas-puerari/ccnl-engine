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

from ccnl_engine.engine.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.payroll.domain.sickness import SicknessCase

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
    "SicknessCaseEvent",
    "TerminationTFREvent",
    "WelfareEvent",
    "WorkEvent",
]


@dataclass(frozen=True)
class OvertimeEvent:
    """Overtime hours: INPS + IRPEF + TFR on computed gross.

    Attributes:
        event_date: Calendar date the overtime was worked.
        hours: Number of overtime hours.  Must be > 0.
        hourly_rate: Base hourly rate in EUR.  Must be > 0.
        multiplier: Overtime multiplier applied to the hourly rate (e.g.
            ``1.25`` for 25% supplement).  Must be > 0.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    multiplier: Decimal = Decimal("1.25")

    def __post_init__(self) -> None:  # noqa: D105
        if self.hours <= 0:
            msg = f"OvertimeEvent.hours must be > 0; got {self.hours}"
            raise InvalidInputError(msg, feature="overtime")
        if self.hourly_rate <= 0:
            msg = f"OvertimeEvent.hourly_rate must be > 0; got {self.hourly_rate}"
            raise InvalidInputError(msg, feature="overtime")
        if self.multiplier <= 0:
            msg = f"OvertimeEvent.multiplier must be > 0; got {self.multiplier}"
            raise InvalidInputError(msg, feature="overtime")


@dataclass(frozen=True)
class NightShiftEvent:
    """Night-shift supplement: INPS + IRPEF + TFR on the supplement amount.

    Attributes:
        event_date: Calendar date the shift was worked.
        supplement_amount: Flat supplement for the night period in EUR.  Must be >= 0.
    """

    event_date: date
    supplement_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.supplement_amount < 0:
            msg = (
                "NightShiftEvent.supplement_amount must be >= 0; "
                f"got {self.supplement_amount}"
            )
            raise InvalidInputError(msg, feature="night_shift")


@dataclass(frozen=True)
class HolidayWorkEvent:
    """Holiday-work supplement: INPS + IRPEF on the supplement amount.

    TFR is not accrued on holiday supplements under the standard Italian
    treatment (art. 2120 c.c. excludes accidental pay).

    Attributes:
        event_date: Calendar date the holiday was worked.
        supplement_amount: Flat supplement for the holiday in EUR.  Must be >= 0.
    """

    event_date: date
    supplement_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.supplement_amount < 0:
            msg = (
                "HolidayWorkEvent.supplement_amount must be >= 0; "
                f"got {self.supplement_amount}"
            )
            raise InvalidInputError(msg, feature="holiday_work")


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
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    end_date: date | None = None

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
class BonusEvent:
    """One-off bonus: INPS + IRPEF (ordinary or substitute) + TFR excluded.

    Attributes:
        event_date: Date the bonus is attributed to.
        amount: Gross bonus amount in EUR.  Must be >= 0.
        is_pdr: When True, the bonus is a Premio di Risultato (PdR) eligible
            for the 1% substitute tax regime under L. 208/2015 art. 1 cc.
            182-190 and L. 199/2025 art. 1 cc. 7-12.  When False (default),
            ordinary IRPEF applies.
    """

    event_date: date
    amount: Decimal
    is_pdr: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"BonusEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="bonus")


@dataclass(frozen=True)
class FringeEvent:
    """Fringe benefit (art. 51 co. 3 TUIR).

    The annual exemption threshold is resolved by ``calculate_period`` from
    the year-level ``VariablePayRules.fringe_benefit`` policy — it is not
    carried on the event itself.  Taxability is determined cumulatively
    across all fringe events in the year (YTD + current period).

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the fringe benefit in EUR.  Must be >= 0.
    """

    event_date: date
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"FringeEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="fringe")


@dataclass(frozen=True)
class WelfareEvent:
    """Welfare benefit: exempt from INPS and IRPEF, no TFR accrual.

    Attributes:
        event_date: Date the benefit is attributed to.
        amount: Value of the welfare benefit in EUR.  Must be >= 0.
    """

    event_date: date
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"WelfareEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="welfare")


@dataclass(frozen=True)
class ArrearsEvent:
    """Contract renewal arrears subject to tassazione separata (art. 17 TUIR).

    Attributes:
        event_date: Date the arrears are attributed to.
        amount: Gross arrears amount in EUR.  Must be >= 0.
        separate_tax_rate: Caller-supplied average IRPEF rate from the
            two prior tax years, applied as tassazione separata.
            Must be in [0, 1].
        reference_period: The competence period from which the arrears
            originate (e.g. the period of the back-dated contract renewal).
            ``None`` when the reference period is not tracked.
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal
    reference_period: PeriodId | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"ArrearsEvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="arrears")
        if not (0 <= self.separate_tax_rate <= 1):
            msg = (
                "ArrearsEvent.separate_tax_rate must be in [0, 1]; "
                f"got {self.separate_tax_rate}"
            )
            raise InvalidInputError(msg, feature="arrears")


@dataclass(frozen=True)
class BilateralFundEvent:
    """Bilateral or health fund contribution (fondi bilaterali/sanitari).

    Both employee and employer portions are expressed as gross amounts.
    The employee portion reduces net pay; the employer portion increases
    employer cost.

    Attributes:
        event_date: Date the contribution is attributed to.
        employee_amount: Employee-side contribution in EUR.  Must be >= 0.
        employer_amount: Employer-side contribution in EUR.  Must be >= 0.
    """

    event_date: date
    employee_amount: Decimal
    employer_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.employee_amount < 0:
            msg = (
                "BilateralFundEvent.employee_amount must be >= 0; "
                f"got {self.employee_amount}"
            )
            raise InvalidInputError(msg, feature="bilateral_fund")
        if self.employer_amount < 0:
            msg = (
                "BilateralFundEvent.employer_amount must be >= 0; "
                f"got {self.employer_amount}"
            )
            raise InvalidInputError(msg, feature="bilateral_fund")


@dataclass(frozen=True)
class TerminationTFREvent:
    """TFR settlement at cessazione (art. 19 TUIR, tassazione separata).

    The caller supplies the applicable tax rate (determined via art. 19
    TUIR using the employee's prior-year average IRPEF rate).

    Attributes:
        event_date: Date of cessazione.
        amount: Total TFR payout in EUR.  Must be >= 0.
        separate_tax_rate: Applicable tassazione separata rate.  Must be in [0, 1].
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"TerminationTFREvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="termination_tfr")
        if not (0 <= self.separate_tax_rate <= 1):
            msg = (
                "TerminationTFREvent.separate_tax_rate must be in [0, 1]; "
                f"got {self.separate_tax_rate}"
            )
            raise InvalidInputError(msg, feature="termination_tfr")


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
        if self.event_date != self.case.episode_start:
            msg = (
                f"SicknessCaseEvent.event_date ({self.event_date}) must equal "
                f"case.episode_start ({self.case.episode_start})"
            )
            raise InvalidInputError(msg, feature="sickness")


WorkEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | SicknessCaseEvent
    | BonusEvent
    | FringeEvent
    | WelfareEvent
    | ArrearsEvent
    | BilateralFundEvent
    | TerminationTFREvent
)
