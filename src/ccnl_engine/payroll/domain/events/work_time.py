"""Work-time supplement events: overtime, night shift, holiday work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

__all__ = ["HolidayWorkEvent", "NightShiftEvent", "OvertimeEvent"]


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
