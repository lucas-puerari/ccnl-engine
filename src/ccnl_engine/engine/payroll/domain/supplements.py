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
        night_hours: Hours worked at night on a weekday (lavoro notturno —
            the exact window, e.g. 22:00-06:00, is defined per CCNL).
        holiday_hours: Hours worked on a public holiday during the day
            (lavoro festivo diurno).
        night_holiday_hours: Hours worked at night *on* a public holiday
            (lavoro festivo-notturno).  These are classified separately
            because many CCNLs apply a higher rate than either night-only
            or holiday-only work.
        supplementare_hours: Part-timer extra hours (lavoro supplementare).
            Distinct from straordinario: applies only when part_time_pct < 1.
    """

    weekday_hours: Decimal = _ZERO
    night_hours: Decimal = _ZERO
    holiday_hours: Decimal = _ZERO
    night_holiday_hours: Decimal = _ZERO
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
            "night_holiday_hours",
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


@dataclass(frozen=True)
class SickInput:
    """Caller-declared sick days for one pay period (malattia ordinaria).

    The engine computes the INPS statutory indemnity and the CCNL
    integration top-up based on the bundled sick-pay rate table and the
    CCNL sickness rules.  All output fields are informational: neither
    ``gross_annual`` nor ``net_annual`` is mutated.

    Attributes:
        sick_days: Calendar days of illness in the period. Must be >= 0.
    """

    sick_days: Decimal = _ZERO
    cumulative_sick_days: Decimal | None = None

    def __post_init__(self) -> None:
        """Validate sick day values.

        Raises:
            ValueError: If ``sick_days`` or ``cumulative_sick_days`` is
                negative.
        """
        if self.sick_days < _ZERO:
            msg = f"sick_days must be >= 0, got {self.sick_days}"
            raise ValueError(msg)
        if self.cumulative_sick_days is not None and self.cumulative_sick_days < _ZERO:
            msg = f"cumulative_sick_days must be >= 0, got {self.cumulative_sick_days}"
            raise ValueError(msg)


@dataclass(frozen=True)
class FringeBenefitInput:
    """Caller-declared fringe benefits for the fiscal year (Art. 51 c. 3 TUIR).

    Fringe benefits are exempt below the statutory annual threshold
    (€1.000 or €2.000 with dependent children).  Amounts above the
    threshold are taxable income; the engine reports the taxable portion
    informally without recomputing IRPEF.

    Attributes:
        annual_amount: Total fringe benefit value for the year. Must be >= 0.
        has_dependent_children: Whether the worker has at least one child
            fiscally at charge (figlio fiscalmente a carico).  Determines
            which threshold applies.
    """

    annual_amount: Decimal = _ZERO
    has_dependent_children: bool = False

    def __post_init__(self) -> None:
        """Validate that annual_amount is non-negative.

        Raises:
            ValueError: If annual_amount is negative.
        """
        if self.annual_amount < _ZERO:
            msg = f"annual_amount must be >= 0, got {self.annual_amount}"
            raise ValueError(msg)


@dataclass(frozen=True)
class WelfareInput:
    """Caller-declared welfare contributions for the fiscal year.

    Welfare structured under Art. 51 c. 2 TUIR is fully exempt from
    IRPEF and social contributions.  The engine echoes the amount and
    marks it as tax-exempt without verifying the platform structure.

    Attributes:
        annual_amount: Total welfare amount for the year. Must be >= 0.
    """

    annual_amount: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that annual_amount is non-negative.

        Raises:
            ValueError: If annual_amount is negative.
        """
        if self.annual_amount < _ZERO:
            msg = f"annual_amount must be >= 0, got {self.annual_amount}"
            raise ValueError(msg)


@dataclass(frozen=True)
class BonusInput:
    """Caller-declared bonus / premio di risultato for the fiscal year.

    When ``eligible_for_pdr`` is True and the worker's gross income from
    employment does not exceed the statutory ceiling, the engine applies
    the PdR flat tax (imposta sostitutiva) up to the statutory maximum.
    The amount exceeding the ceiling is reported as ordinarily taxable.

    The engine does *not* recompute IRPEF for the ordinary-tax portion;
    that would require extending the fiscal chain.  The output is
    informational only.

    Attributes:
        annual_amount: Total bonus for the year. Must be >= 0.
        eligible_for_pdr: Whether the bonus qualifies for the PdR
            preferential tax regime (union agreement in place).
    """

    annual_amount: Decimal = _ZERO
    eligible_for_pdr: bool = False

    def __post_init__(self) -> None:
        """Validate that annual_amount is non-negative.

        Raises:
            ValueError: If annual_amount is negative.
        """
        if self.annual_amount < _ZERO:
            msg = f"annual_amount must be >= 0, got {self.annual_amount}"
            raise ValueError(msg)
