"""Work-time supplement events: overtime, night, holiday and shift work."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    parse_enum,
    require_bool,
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
    "HolidayWorkKind",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "ShiftKind",
    "ShiftWorkEvent",
]


class OvertimeKind(StrEnum):
    """When overtime was worked, selecting the CCNL band of the same work kind.

    Attributes:
        WEEKDAY: Daytime overtime on a working day (straordinario diurno).
        NIGHT: Night overtime (straordinario notturno).
        HOLIDAY: Overtime on a public holiday or rest day (straordinario festivo).
        REST_DAY: Overtime on the weekly rest day where the CCNL pays it
            apart from the holidays; without a rest-day band, as ``HOLIDAY``.
        SATURDAY: Overtime on Saturday where the CCNL pays it apart
            (Metalmeccanico artigianato); without a band, as ``WEEKDAY``.
        NIGHT_HOLIDAY: Night overtime on a public holiday (festivo notturno).
        SUPPLEMENTARY: Part-time hours beyond the agreed ones within the full
            week (D.Lgs. 81/2015 art. 6 c. 2), at the supplementare band.
    """

    WEEKDAY = "weekday"
    NIGHT = "night"
    HOLIDAY = "holiday"
    REST_DAY = "rest_day"
    NIGHT_HOLIDAY = "night_holiday"
    SATURDAY = "saturday"
    SUPPLEMENTARY = "supplementare"


@dataclass(frozen=True)
class OvertimeEvent:
    """Overtime hours: INPS + IRPEF + TFR on computed gross.

    Attributes:
        event_date: Calendar date the overtime was worked.
        hours: Overtime hours, above 0 and at most 744 (a month of 31 days).
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
        NIGHT_HOLIDAY: Hours worked on a public holiday at night (lavoro
            festivo notturno), which a CCNL may pay at a rate of its own.
        SATURDAY_SIXTH_DAY: Ordinary hours worked on Saturday or the sixth
            day of the week (Alimentari art. 31).
    """

    HOLIDAY = "holiday"
    HOLIDAY_COMPENSATORY_REST = "holiday_compensatory_rest"
    SUNDAY = "sunday"
    REST_DAY = "rest_day"
    NIGHT_HOLIDAY = "night_holiday"
    SATURDAY_SIXTH_DAY = "saturday_sixth_day"


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
        before_22: Whether the hours fall before 22:00, which a CCNL may pay
            at a lower night rate (Confapi art. 29 row b).
    """

    event_date: date
    supplement_amount: Decimal | None = None
    hours: Decimal | None = None
    before_22: bool = False

    def __post_init__(self) -> None:  # noqa: D105
        _check_supplement(
            self.event_date,
            self.supplement_amount,
            self.hours,
            "NightShiftEvent",
            "night_shift",
        )
        require_bool(self.before_22, "NightShiftEvent.before_22", feature="night_shift")


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
