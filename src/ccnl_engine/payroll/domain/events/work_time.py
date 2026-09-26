"""Work-time supplement events: overtime, night, holiday and shift work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

__all__ = ["HolidayWorkEvent", "NightShiftEvent", "OvertimeEvent", "ShiftWorkEvent"]


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


def _check_supplement(amount: Decimal, event: str, feature: str) -> None:
    """Reject a negative supplement amount.

    Raises:
        InvalidInputError: When ``amount`` is negative.
    """
    if amount < 0:
        msg = f"{event}.supplement_amount must be >= 0; got {amount}"
        raise InvalidInputError(msg, feature=feature)


@dataclass(frozen=True)
class NightShiftEvent:
    """Night-work supplement: INPS + IRPEF on the supplement amount.

    Covers the maggiorazioni and indennita for night work (D.Lgs. 66/2003
    art. 1 c. 2 and the CCNL), eligible for the 15% substitute tax within
    the 1,500 EUR annual cap.

    Attributes:
        event_date: Calendar date the shift was worked.
        supplement_amount: Flat supplement for the night period in EUR.
            Must be >= 0.
    """

    event_date: date
    supplement_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        _check_supplement(self.supplement_amount, "NightShiftEvent", "night_shift")


@dataclass(frozen=True)
class HolidayWorkEvent:
    """Holiday or weekly rest-day supplement: INPS + IRPEF on the supplement.

    Covers the maggiorazioni and indennita for work on public holidays and on
    weekly rest days as identified by the CCNL, eligible for the 15%
    substitute tax within the 1,500 EUR annual cap.  TFR is not accrued on
    holiday supplements under the standard Italian treatment (art. 2120 c.c.
    excludes accidental pay).

    Attributes:
        event_date: Calendar date the holiday or rest day was worked.
        supplement_amount: Flat supplement for the day in EUR.  Must be >= 0.
    """

    event_date: date
    supplement_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        _check_supplement(self.supplement_amount, "HolidayWorkEvent", "holiday_work")


@dataclass(frozen=True)
class ShiftWorkEvent:
    """Shift-work allowance: INPS + IRPEF on the supplement amount.

    Covers the indennita di turno and the other shift-work pay set by the
    CCNL, eligible for the 15% substitute tax within the 1,500 EUR annual
    cap.  TFR is not accrued, as for the other work-time supplements.

    Attributes:
        event_date: Calendar date the shift was worked.
        supplement_amount: Shift allowance in EUR.  Must be >= 0.
    """

    event_date: date
    supplement_amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        _check_supplement(self.supplement_amount, "ShiftWorkEvent", "shift_work")
