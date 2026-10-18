"""Work-time supplement events: overtime, night, holiday and shift work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.validators import (
    parse_enum,
    require_date,
    require_decimal,
    require_int,
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
    "StandbyEvent",
    "StandbyKind",
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
        REST_DAY: Overtime on the weekly rest day (Sunday, or the day the
            rest moves to) where the CCNL pays it apart from the public
            holidays; a CCNL without a rest-day band pays it as ``HOLIDAY``.
        NIGHT_HOLIDAY: Night overtime on a public holiday (straordinario
            festivo notturno).
        SUPPLEMENTARY: Hours a part-time worker works beyond the agreed
            hours within the full-time week (lavoro supplementare, D.Lgs.
            81/2015 art. 6 c. 2), paid with the CCNL supplementare band.
    """

    WEEKDAY = "weekday"
    NIGHT = "night"
    HOLIDAY = "holiday"
    REST_DAY = "rest_day"
    NIGHT_HOLIDAY = "night_holiday"
    SUPPLEMENTARY = "supplementare"


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


class StandbyKind(StrEnum):
    """Unit of a standby period, selecting the CCNL rate.

    Attributes:
        HOURS: Hours of standby, paid at the working-day rate per hour.
        WORKED_DAY: Day of 16 hours on a working day.
        REST_DAY: Day of 24 hours on a rest day.
        HOLIDAY: Day of 24 hours on a public holiday.
        WEEK: Week of 6 days.
        WEEK_HOLIDAY: Week of 6 days with a public holiday.
        WEEK_HOLIDAY_REST_DAY: Week of 6 days with a public holiday and a
            rest day.
    """

    HOURS = "hours"
    WORKED_DAY = "worked_day"
    REST_DAY = "rest_day"
    HOLIDAY = "holiday"
    WEEK = "week"
    WEEK_HOLIDAY = "week_holiday"
    WEEK_HOLIDAY_REST_DAY = "week_holiday_rest_day"


@dataclass(frozen=True)
class StandbyEvent:
    """Standby (reperibilità) paid at the CCNL rates of the worker's level.

    The time of the calls and of the intervention is not standby: it is
    paid as overtime or ordinary hours with their own events.

    Attributes:
        event_date: Date the standby is attributed to: the rates in force
            on it apply.
        kind: Unit of the standby.
        quantity: Hours, days or weeks of the unit, above 0.
        calls: Calls followed by an intervention, each paid the CCNL fee.
    """

    event_date: date
    kind: StandbyKind
    quantity: Decimal
    calls: int = 0

    def __post_init__(self) -> None:  # noqa: D105
        feature = "standby"
        require_date(self.event_date, "StandbyEvent.event_date", feature=feature)
        object.__setattr__(
            self,
            "kind",
            parse_enum(self.kind, StandbyKind, "StandbyEvent.kind", feature=feature),
        )
        require_decimal(
            self.quantity,
            "StandbyEvent.quantity",
            feature=feature,
            positive=True,
            maximum=_HOURS_IN_A_MONTH,
        )
        require_int(self.calls, "StandbyEvent.calls", feature=feature, minimum=0)
