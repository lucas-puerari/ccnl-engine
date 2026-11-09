"""Overtime events and their work kinds."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.validators import (
    parse_enum,
    require_bool,
    require_date,
    require_decimal,
)

if TYPE_CHECKING:
    from datetime import date

_HOURS_IN_A_MONTH = Decimal(31 * 24)


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
        hourly_rate: Base hourly rate in EUR, above 0; ``None`` derives it
            from the CCNL hourly base (the run is rejected without one).
        multiplier: Overtime multiplier applied to the hourly rate (e.g.
            ``1.25`` for 25% supplement).  Must be > 0.  ``None`` (the
            default) derives it from the CCNL band of ``kind`` as
            ``1 + band``; the run is rejected when the CCNL has no single
            percentage band for it.  An explicit value prevails over the
            CCNL band.
        kind: When the hours were worked, selecting the CCNL band.
        non_occasional: Whether the overtime is worked 'a titolo non
            occasionale', which a CCNL may count in the TFR (operai agricoli
            OTD: 10%); ``False`` is occasional overtime.
        banked: Whether the worker elected compensatory rest for these hours.
            Only an agreement with an overtime bank rule can pay the premium
            alone; the hours remain a separate rest balance outside this event.
    """

    event_date: date
    hours: Decimal
    hourly_rate: Decimal | None = None
    multiplier: Decimal | None = None
    kind: OvertimeKind = OvertimeKind.WEEKDAY
    non_occasional: bool = False
    banked: bool = False

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
        for name in ("hourly_rate", "multiplier"):
            require_decimal(
                getattr(self, name),
                f"OvertimeEvent.{name}",
                feature=feature,
                positive=True,
                optional=True,
            )
        require_bool(
            self.non_occasional, "OvertimeEvent.non_occasional", feature=feature
        )
        require_bool(self.banked, "OvertimeEvent.banked", feature=feature)
        kind = parse_enum(
            self.kind, OvertimeKind, "OvertimeEvent.kind", feature=feature
        )
        object.__setattr__(self, "kind", kind)
