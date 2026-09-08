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
