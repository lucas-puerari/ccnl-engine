"""Kinds of overtime, holiday work and rotating shifts."""

from enum import StrEnum


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
        SUNDAY: Daytime overtime on a Sunday that is not the weekly rest day
            nor a holiday, where the CCNL pays it apart (Commercio art. 149:
            "le ore straordinarie di lavoro prestato nei giorni festivi o la
            domenica", 30%); without a band, as ``WEEKDAY``.  Night, rest-day
            and holiday overtime keep their own kinds.
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
    SUNDAY = "sunday"
    SUPPLEMENTARY = "supplementare"


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
