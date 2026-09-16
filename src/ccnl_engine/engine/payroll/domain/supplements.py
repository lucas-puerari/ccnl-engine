"""Layer 3 supplement input models."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_ZERO = Decimal(0)

_HOUR_FIELDS: tuple[str, ...] = (
    "weekday_hours",
    "night_hours",
    "holiday_hours",
    "night_holiday_hours",
    "supplementare_hours",
)


def _validate_non_negative(value: Decimal, name: str) -> None:
    """Raise ValueError when *value* is negative.

    Raises:
        ValueError: If ``value < 0``.
    """
    if value < _ZERO:
        msg = f"{name} must be >= 0, got {value}"
        raise ValueError(msg)


@dataclass(frozen=True)
class WeeklyOvertimeHours:
    """Per-week overtime hours for one calendar week inside a pay period.

    Use :class:`OvertimeHours` at the top level and attach one
    ``WeeklyOvertimeHours`` entry per calendar week to
    :attr:`OvertimeHours.weeks`.  When ``weeks`` is provided the engine
    applies CCNL band thresholds separately for each week and sums the
    results, producing an accurate supplement for CCNLs with per-week
    hour caps (e.g. "first 4 h/week at 15%, additional at 20%").

    All values represent overtime (or night/holiday) hours worked *in
    addition to* the standard schedule for that particular week.

    Attributes:
        weekday_hours: Daytime weekday overtime (straordinario diurno).
        night_hours: Weekday night hours (lavoro notturno).
        holiday_hours: Public-holiday daytime hours (lavoro festivo diurno).
        night_holiday_hours: Night hours on a public holiday.
        supplementare_hours: Part-timer extra hours (lavoro supplementare).
    """

    weekday_hours: Decimal = _ZERO
    night_hours: Decimal = _ZERO
    holiday_hours: Decimal = _ZERO
    night_holiday_hours: Decimal = _ZERO
    supplementare_hours: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that all hour values are non-negative."""
        for name in _HOUR_FIELDS:
            _validate_non_negative(getattr(self, name), name)


@dataclass(frozen=True)
class OvertimeHours:
    """Caller-declared supplement hours for one pay period.

    All values represent hours worked *in addition to* the standard
    schedule for that month. The engine applies the CCNL multiplier for
    each category to the full-time minimo tabellare hourly rate.

    **Weekly breakdown for tiered bands**

    Some CCNLs partition overtime into hourly bands that apply *per week*
    (e.g. the first 4 h/week at 15%, additional hours at 20%).  Passing a
    monthly total to such a CCNL treats the entire month as a single week,
    which overstates the contribution of the higher band.  To get accurate
    results, supply a :class:`WeeklyOvertimeHours` entry for each calendar
    week in the pay period via :attr:`weeks`.

    When ``weeks`` is non-empty:

    - Each monthly field must equal the sum of the corresponding weekly
      field across all weeks (validated in ``__post_init__``).
    - The engine processes each week through the band thresholds
      independently and sums the contributions.

    Use :meth:`from_weeks` to derive the monthly totals automatically from
    a weekly breakdown.

    Attributes:
        weekday_hours: Monthly total of daytime weekday overtime hours
            (straordinario diurno).
        night_hours: Monthly total of weekday night hours (lavoro notturno).
        holiday_hours: Monthly total of public-holiday daytime hours
            (lavoro festivo diurno).
        night_holiday_hours: Monthly total of night hours on a public holiday
            (lavoro festivo-notturno).
        supplementare_hours: Monthly total of part-timer extra hours
            (lavoro supplementare).
        weeks: Per-week breakdown.  Empty tuple (default) means no weekly
            data was supplied; all monthly totals are treated as one period.
    """

    weekday_hours: Decimal = _ZERO
    night_hours: Decimal = _ZERO
    holiday_hours: Decimal = _ZERO
    night_holiday_hours: Decimal = _ZERO
    supplementare_hours: Decimal = _ZERO
    weeks: tuple[WeeklyOvertimeHours, ...] = ()

    def __post_init__(self) -> None:
        """Validate all hour values and weekly-vs-monthly consistency.

        Raises:
            ValueError: If any hour value is negative, or if ``weeks`` is
                non-empty and a monthly field does not equal the sum of
                the corresponding weekly values.
        """
        for name in _HOUR_FIELDS:
            _validate_non_negative(getattr(self, name), name)
        if self.weeks:
            for name in _HOUR_FIELDS:
                monthly = getattr(self, name)
                weekly_sum = sum(getattr(w, name) for w in self.weeks)
                if monthly != weekly_sum:
                    msg = (
                        f"{name} monthly total {monthly} does not match "
                        f"sum of weekly values {weekly_sum}"
                    )
                    raise ValueError(msg)

    @classmethod
    def from_weeks(cls, weeks: tuple[WeeklyOvertimeHours, ...]) -> OvertimeHours:
        """Create an :class:`OvertimeHours` from a weekly breakdown.

        Derives the monthly totals by summing each field across all weeks
        so the caller does not need to compute the totals manually.

        Args:
            weeks: Per-week overtime hours, one entry per calendar week in
                the pay period.

        Returns:
            :class:`OvertimeHours` with ``weeks`` set and monthly totals
            derived from the sum of weekly values.
        """
        return cls(
            weekday_hours=sum((w.weekday_hours for w in weeks), _ZERO),
            night_hours=sum((w.night_hours for w in weeks), _ZERO),
            holiday_hours=sum((w.holiday_hours for w in weeks), _ZERO),
            night_holiday_hours=sum((w.night_holiday_hours for w in weeks), _ZERO),
            supplementare_hours=sum((w.supplementare_hours for w in weeks), _ZERO),
            weeks=weeks,
        )


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
        cumulative_sick_days: Days already elapsed in the **same illness
            episode** before this period. The engine uses this value to
            shift the carenza position and INPS band boundaries so that
            splitting one episode across multiple pay periods gives the
            same totals as computing it in a single period.

            Leave as ``None`` (or ``Decimal(0)``) for the first period
            of a new episode; the engine then starts carenza from day 1.
            For a continuation, pass the episode days already covered in
            the previous period(s) — not the year-to-date total across
            all absences.  A separate new episode restarts at ``None``.
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
        prior_year_gross_annual: Gross employment income from the
            previous fiscal year. When provided, it is used instead of
            the current-year gross to check the PdR income ceiling
            (per L. 207/2024 art. 1 c. 385). ``None`` means the
            current-year gross is used (pre-2026 behaviour). Must be
            >= 0 when provided.
    """

    annual_amount: Decimal = _ZERO
    eligible_for_pdr: bool = False
    prior_year_gross_annual: Decimal | None = None

    def __post_init__(self) -> None:
        """Validate that annual_amount and prior_year_gross_annual are non-negative.

        Raises:
            ValueError: If annual_amount or prior_year_gross_annual is negative.
        """
        if self.annual_amount < _ZERO:
            msg = f"annual_amount must be >= 0, got {self.annual_amount}"
            raise ValueError(msg)
        prior = self.prior_year_gross_annual
        if prior is not None and prior < _ZERO:
            msg = (
                f"prior_year_gross_annual must be >= 0, "
                f"got {self.prior_year_gross_annual}"
            )
            raise ValueError(msg)
