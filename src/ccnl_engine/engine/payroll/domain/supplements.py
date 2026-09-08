"""Layer 3 supplement input models."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_ZERO = Decimal(0)


@dataclass(frozen=True)
class OvertimeHours:
    """Caller-declared supplement hours for one pay period.

    All values represent hours worked *in addition to* the standard
    schedule for that month. The engine applies the CCNL multiplier for
    each category to the full-time minimo tabellare hourly rate.

    Attributes:
        weekday_hours: Daytime weekday overtime hours (straordinario diurno).
        night_hours: Hours worked at night (lavoro notturno — the exact
            window, e.g. 22:00-06:00, is defined per CCNL).
        holiday_hours: Hours worked on a public holiday or mandatory rest
            day (lavoro festivo).
        supplementare_hours: Part-timer extra hours (lavoro supplementare).
            Distinct from straordinario: applies only when part_time_pct < 1.
    """

    weekday_hours: Decimal = _ZERO
    night_hours: Decimal = _ZERO
    holiday_hours: Decimal = _ZERO
    supplementare_hours: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that all hour values are non-negative.

        Raises:
            ValueError: If any hour value is negative.
        """
        for name in (
            "weekday_hours",
            "night_hours",
            "holiday_hours",
            "supplementare_hours",
        ):
            value = getattr(self, name)
            if value < _ZERO:
                msg = f"{name} must be >= 0, got {value}"
                raise ValueError(msg)


@dataclass(frozen=True)
class AbsenceDays:
    """Caller-declared absent days for one pay period.

    Represents days for which no contractual pay is due
    (assenza non retribuita). The engine computes the deduction
    based on the per-CCNL daily divisor method and reports it
    as :attr:`~ccnl_engine.engine.payroll.domain.payroll_result\
.PayrollResult.absence_deduction_monthly`.

    The deduction is informational: ``gross_annual`` and ``net_annual``
    are not mutated. Use
    :attr:`~ccnl_engine.engine.payroll.domain.payroll_result\
.PayrollResult.effective_gross_monthly` for the net-of-absence figure.

    Attributes:
        unpaid_days: Days absent without pay in the period. Must be >= 0.
    """

    unpaid_days: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that unpaid_days is non-negative.

        Raises:
            ValueError: If unpaid_days is negative.
        """
        if self.unpaid_days < _ZERO:
            msg = f"unpaid_days must be >= 0, got {self.unpaid_days}"
            raise ValueError(msg)


@dataclass(frozen=True)
class LeaveInput:
    """Caller-declared leave days taken in one pay period.

    Represents paid leave days (*ferie* / *permessi*) consumed during the
    period. The engine computes the monthly accrual from the CCNL annual
    entitlement and reports the net balance as informational output — it
    does not alter ``gross_annual`` or ``net_annual``.

    Attributes:
        taken_days: Leave days consumed in the period. Must be >= 0.
    """

    taken_days: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that taken_days is non-negative.

        Raises:
            ValueError: If taken_days is negative.
        """
        if self.taken_days < _ZERO:
            msg = f"taken_days must be >= 0, got {self.taken_days}"
            raise ValueError(msg)
