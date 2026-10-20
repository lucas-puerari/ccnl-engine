"""The standby (reperibilità) event of a run."""

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

__all__ = ["StandbyEvent", "StandbyKind"]


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
