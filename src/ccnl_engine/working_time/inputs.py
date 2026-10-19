"""Work-time supplement events: overtime, night, holiday and shift work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
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
    "HolidayWorkKind",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "ShiftKind",
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
        hourly_rate: Base hourly rate in EUR, above 0.  ``None`` (the
            default) derives it from the CCNL: the monthly pay elements of
            its ``hourly_base_method`` divided by its hourly divisor, when
            the CCNL hourly base is sourced; otherwise the run is rejected.
            An explicit value prevails and is reported as caller-supplied.
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
    hourly_rate: Decimal | None = None
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
            optional=True,
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


class HolidayWorkKind(StrEnum):
    """Which holiday or rest-day work a :class:`HolidayWorkEvent` pays.

    Attributes:
        HOLIDAY: Hours worked on a public holiday (festività).
        HOLIDAY_COMPENSATORY_REST: Hours worked on a public holiday or rest
            day for which the worker takes a compensatory rest day.
        SUNDAY: Ordinary hours worked on a Sunday by a worker whose weekly
            rest falls on another day.
        REST_DAY: Hours worked on the weekly rest day.
    """

    HOLIDAY = "holiday"
    HOLIDAY_COMPENSATORY_REST = "holiday_compensatory_rest"
    SUNDAY = "sunday"
    REST_DAY = "rest_day"


class ShiftKind(StrEnum):
    """Rotating shift a :class:`ShiftWorkEvent` pays.

    Attributes:
        DAY: A day shift of a rotation (turno diurno).
        NIGHT: A night shift of a rotation (turno notturno).
    """

    DAY = "day"
    NIGHT = "night"


def _check_supplement(
    event_date: object,
    amount: object,
    hours: object,
    event: str,
    feature: str,
) -> None:
    """Reject a supplement event without a date, or with neither amount nor hours.

    Raises:
        InvalidInputError: When neither the amount nor the hours are given.
    """
    require_date(event_date, f"{event}.event_date", feature=feature)
    require_decimal(
        amount,
        f"{event}.supplement_amount",
        feature=feature,
        minimum=_ZERO,
        optional=True,
    )
    require_decimal(
        hours,
        f"{event}.hours",
        feature=feature,
        positive=True,
        maximum=_HOURS_IN_A_MONTH,
        optional=True,
    )
    if amount is None and hours is None:
        msg = f"{event} needs supplement_amount or the hours the engine derives it from"
        raise InvalidInputError(msg, field=f"{event}.hours", feature=feature)


@dataclass(frozen=True)
class NightShiftEvent:
    """Night-work supplement: INPS + IRPEF on the supplement amount.

    Covers the maggiorazioni and indennita for ordinary night work (D.Lgs.
    66/2003 art. 1 c. 2 and the CCNL), eligible for the 15% substitute tax
    within the 1,500 EUR annual cap.  Night overtime is an
    :class:`OvertimeEvent`.

    Attributes:
        event_date: Calendar date the night hours were worked.
        supplement_amount: Supplement for the night hours in EUR, >= 0;
            reported as caller-supplied.  ``None`` (the default) derives it
            from the CCNL night band and hourly base, ``hours`` required;
            the run is rejected when the CCNL has none the engine applies.
        hours: Ordinary night hours, above 0 and at most 744.
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        _check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "NightShiftEvent",
            "night_shift",
        )


@dataclass(frozen=True)
class HolidayWorkEvent:
    """Holiday or weekly rest-day supplement: INPS + IRPEF on the supplement.

    Covers the maggiorazioni and indennita for work on public holidays and on
    weekly rest days as identified by the CCNL, eligible for the 15%
    substitute tax within the 1,500 EUR annual cap.  TFR is not accrued on
    holiday supplements under the standard Italian treatment (art. 2120 c.c.
    excludes accidental pay).  Where the CCNL also pays the hours themselves,
    the engine does not post them: the run reports it.

    Attributes:
        event_date: Calendar date the holiday or rest day was worked.
        supplement_amount: Supplement for the day in EUR, >= 0; reported as
            caller-supplied.  ``None`` (the default) derives it from the
            CCNL band of ``kind`` and hourly base, ``hours`` required.
        hours: Hours worked that day, above 0 and at most 744.
        kind: Which holiday or rest-day work the hours are.
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None
    kind: HolidayWorkKind = HolidayWorkKind.HOLIDAY

    def __post_init__(self) -> None:  # noqa: D105
        feature = "holiday_work"
        _check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "HolidayWorkEvent",
            feature,
        )
        kind = parse_enum(
            self.kind, HolidayWorkKind, "HolidayWorkEvent.kind", feature=feature
        )
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True)
class ShiftWorkEvent:
    """Shift-work allowance: INPS + IRPEF on the supplement amount.

    Covers the indennita di turno and the other shift-work pay set by the
    CCNL, eligible for the 15% substitute tax within the 1,500 EUR annual
    cap.  TFR is not accrued, as for the other work-time supplements.

    Attributes:
        event_date: Calendar date the shift was worked.
        supplement_amount: Shift allowance in EUR, >= 0; reported as
            caller-supplied.  ``None`` (the default) derives it from the
            CCNL band of ``kind`` and hourly base, ``hours`` and ``kind``
            required.
        hours: Hours of the shift, above 0 and at most 744.
        kind: The shift of the rotation; ``None`` when not stated.
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None
    kind: ShiftKind | None = None

    def __post_init__(self) -> None:  # noqa: D105
        feature = "shift_work"
        _check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "ShiftWorkEvent",
            feature,
        )
        if self.kind is not None:
            kind = parse_enum(
                self.kind, ShiftKind, "ShiftWorkEvent.kind", feature=feature
            )
            object.__setattr__(self, "kind", kind)


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
