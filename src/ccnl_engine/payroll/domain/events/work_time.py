"""Work-time supplement events: overtime, night, holiday and shift work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.validation import (
    parse_enum,
    require_date,
    require_decimal,
)

if TYPE_CHECKING:
    from datetime import date

_ZERO = Decimal(0)
#: Hours of a month of 31 days: no event of a month can exceed them.
_HOURS_IN_A_MONTH = Decimal(31 * 24)

__all__ = [
    "HolidayWorkEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "ShiftWorkEvent",
]


class OvertimeKind(StrEnum):
    """When overtime hours were worked, selecting the CCNL overtime band.

    The values match the work kinds the CCNL ``time_supplements`` bands
    apply to.

    Attributes:
        WEEKDAY: Daytime overtime on a working day (straordinario diurno).
        NIGHT: Night overtime (straordinario notturno).
        HOLIDAY: Overtime on a public holiday or rest day (straordinario
            festivo).
        NIGHT_HOLIDAY: Night overtime on a public holiday (straordinario
            festivo notturno).
    """

    WEEKDAY = "weekday"
    NIGHT = "night"
    HOLIDAY = "holiday"
    NIGHT_HOLIDAY = "night_holiday"


@dataclass(frozen=True)
class OvertimeEvent:
    """Overtime hours: INPS + IRPEF + TFR on computed gross.

    Attributes:
        event_date: Calendar date the overtime was worked.
        hours: Number of overtime hours, above 0 and at most the 744 hours
            of a month of 31 days.
        hourly_rate: Base hourly rate in EUR.  Must be > 0.
        multiplier: Overtime multiplier applied to the hourly rate (e.g.
            ``1.25`` for 25% supplement).  Must be > 0.  ``None`` (the
            default) derives it from the CCNL band of ``kind`` as
            ``1 + band``; the run is rejected when the CCNL has no single
            percentage band for it.  An explicit value prevails over the
            CCNL band.
        kind: When the hours were worked, selecting the CCNL band.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal
    multiplier: Decimal | None = None
    kind: OvertimeKind = OvertimeKind.WEEKDAY

    def __post_init__(self) -> None:  # noqa: D105
        feature = "overtime"
        require_date(self.event_date, "OvertimeEvent.event_date", feature=feature)
        require_decimal(
            self.hours,
            "OvertimeEvent.hours",
            feature=feature,
            positive=True,
            maximum=_HOURS_IN_A_MONTH,
        )
        require_decimal(
            self.hourly_rate,
            "OvertimeEvent.hourly_rate",
            feature=feature,
            positive=True,
        )
        require_decimal(
            self.multiplier,
            "OvertimeEvent.multiplier",
            feature=feature,
            positive=True,
            optional=True,
        )
        kind = parse_enum(
            self.kind, OvertimeKind, "OvertimeEvent.kind", feature=feature
        )
        object.__setattr__(self, "kind", kind)


def _check_supplement(
    event_date: object, amount: object, event: str, feature: str
) -> None:
    """Reject a supplement event without a date or with a negative amount."""
    require_date(event_date, f"{event}.event_date", feature=feature)
    require_decimal(
        amount, f"{event}.supplement_amount", feature=feature, minimum=_ZERO
    )


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
        _check_supplement(
            self.event_date, self.supplement_amount, "NightShiftEvent", "night_shift"
        )


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
        _check_supplement(
            self.event_date, self.supplement_amount, "HolidayWorkEvent", "holiday_work"
        )


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
        _check_supplement(
            self.event_date, self.supplement_amount, "ShiftWorkEvent", "shift_work"
        )
