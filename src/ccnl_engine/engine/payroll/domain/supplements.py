"""Layer 3 supplement input models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.engine.primitives.domain.primitives import StrictDecimal

_ZERO = Decimal(0)

_HOUR_FIELDS: tuple[str, ...] = (
    "weekday_hours",
    "night_hours",
    "holiday_hours",
    "night_holiday_hours",
    "supplementare_hours",
)


class WeeklyOvertimeHours(BaseModel):
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

    model_config = ConfigDict(frozen=True, extra="forbid")

    weekday_hours: StrictDecimal = _ZERO
    night_hours: StrictDecimal = _ZERO
    holiday_hours: StrictDecimal = _ZERO
    night_holiday_hours: StrictDecimal = _ZERO
    supplementare_hours: StrictDecimal = _ZERO

    @model_validator(mode="after")
    def _check_non_negative(self) -> WeeklyOvertimeHours:
        for name in _HOUR_FIELDS:
            v = getattr(self, name)
            if v < _ZERO:
                msg = f"{name} must be >= 0, got {v}"
                raise ValueError(msg)
        return self


class OvertimeHours(BaseModel):
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

    model_config = ConfigDict(frozen=True, extra="forbid")

    weekday_hours: StrictDecimal = _ZERO
    night_hours: StrictDecimal = _ZERO
    holiday_hours: StrictDecimal = _ZERO
    night_holiday_hours: StrictDecimal = _ZERO
    supplementare_hours: StrictDecimal = _ZERO
    weeks: tuple[WeeklyOvertimeHours, ...] = ()

    @model_validator(mode="after")
    def _check_valid(self) -> OvertimeHours:
        for name in _HOUR_FIELDS:
            v = getattr(self, name)
            if v < _ZERO:
                msg = f"{name} must be >= 0, got {v}"
                raise ValueError(msg)
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
        return self

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


class AbsenceDays(BaseModel):
    """Caller-declared absent days for one pay period.

    Represents days for which no contractual pay is due
    (assenza non retribuita). The engine computes the deduction
    based on the per-CCNL daily divisor method and reports it
    as :attr:`~ccnl_engine.engine.payroll.domain.payroll_result\
.AnnualEstimate.absence_deduction_monthly`.

    The deduction is informational: ``gross_annual`` and ``net_annual``
    are not mutated. Use
    :attr:`~ccnl_engine.engine.payroll.domain.payroll_result\
.AnnualEstimate.effective_gross_monthly` for the net-of-absence figure.

    Attributes:
        unpaid_days: Days absent without pay in the period. Must be >= 0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    unpaid_days: StrictDecimal = _ZERO

    @model_validator(mode="after")
    def _check_non_negative(self) -> AbsenceDays:
        if self.unpaid_days < _ZERO:
            msg = f"unpaid_days must be >= 0, got {self.unpaid_days}"
            raise ValueError(msg)
        return self


class LeaveInput(BaseModel):
    """Caller-declared leave days taken in one pay period.

    Represents paid leave days (*ferie* / *permessi*) consumed during the
    period. The engine computes the monthly accrual from the CCNL annual
    entitlement and reports the net balance as informational output — it
    does not alter ``gross_annual`` or ``net_annual``.

    Attributes:
        taken_days: Leave days consumed in the period. Must be >= 0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    taken_days: StrictDecimal = _ZERO

    @model_validator(mode="after")
    def _check_non_negative(self) -> LeaveInput:
        if self.taken_days < _ZERO:
            msg = f"taken_days must be >= 0, got {self.taken_days}"
            raise ValueError(msg)
        return self


class SickInput(BaseModel):
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

    model_config = ConfigDict(frozen=True, extra="forbid")

    sick_days: StrictDecimal = _ZERO
    cumulative_sick_days: StrictDecimal | None = None

    @model_validator(mode="after")
    def _check_non_negative(self) -> SickInput:
        if self.sick_days < _ZERO:
            msg = f"sick_days must be >= 0, got {self.sick_days}"
            raise ValueError(msg)
        if self.cumulative_sick_days is not None and self.cumulative_sick_days < _ZERO:
            msg = f"cumulative_sick_days must be >= 0, got {self.cumulative_sick_days}"
            raise ValueError(msg)
        return self


class FringeBenefitInput(BaseModel):
    """Caller-declared fringe benefits for the fiscal year (Art. 51 c. 3 TUIR).

    Fringe benefits are exempt below the statutory annual threshold
    (EUR 1.000 or EUR 2.000 with dependent children).  Amounts above the
    threshold are taxable income; the engine reports the taxable portion
    informally without recomputing IRPEF.

    Attributes:
        annual_amount: Total fringe benefit value for the year. Must be >= 0.
        has_dependent_children: Whether the worker has at least one child
            fiscally at charge (figlio fiscalmente a carico).  Determines
            which threshold applies.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    annual_amount: StrictDecimal = _ZERO
    has_dependent_children: bool = False

    @model_validator(mode="after")
    def _check_non_negative(self) -> FringeBenefitInput:
        if self.annual_amount < _ZERO:
            msg = f"annual_amount must be >= 0, got {self.annual_amount}"
            raise ValueError(msg)
        return self


class WelfareInput(BaseModel):
    """Caller-declared welfare contributions for the fiscal year.

    Welfare structured under Art. 51 c. 2 TUIR is fully exempt from
    IRPEF and social contributions.  The engine echoes the amount and
    marks it as tax-exempt without verifying the platform structure.

    Attributes:
        annual_amount: Total welfare amount for the year. Must be >= 0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    annual_amount: StrictDecimal = _ZERO

    @model_validator(mode="after")
    def _check_non_negative(self) -> WelfareInput:
        if self.annual_amount < _ZERO:
            msg = f"annual_amount must be >= 0, got {self.annual_amount}"
            raise ValueError(msg)
        return self


class BonusInput(BaseModel):
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

    model_config = ConfigDict(frozen=True, extra="forbid")

    annual_amount: StrictDecimal = _ZERO
    eligible_for_pdr: bool = False
    prior_year_gross_annual: StrictDecimal | None = None

    @model_validator(mode="after")
    def _check_non_negative(self) -> BonusInput:
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
        return self
