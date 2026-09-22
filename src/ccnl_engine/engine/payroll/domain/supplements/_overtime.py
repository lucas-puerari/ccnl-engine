"""WeeklyOvertimeHours and OvertimeHours input models."""

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
