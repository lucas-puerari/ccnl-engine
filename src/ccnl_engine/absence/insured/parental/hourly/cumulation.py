"""No cumulation of the leave by the hour with the rests of the decree.

Art. 32 c. 1-ter D.Lgs. 151/2001 excludes, under its general criterion,
the cumulation of the parental leave by the hour with the other permits
and rests of the decree; INPS circ. 152/2015 par. 2.1: "Il congedo ad ore
quindi non può essere fruito nei medesimi giorni in cui il genitore fruisce
di riposi giornalieri per allattamento ex artt. 39 e 40".  A CCNL or local
agreement that regulates the leave may allow it, so the check applies only
where the criterion does.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.parental.hourly.inputs import (
    HourlyParentalLeaveEvent,
)
from ccnl_engine.absence.insured.rest.inputs import NursingRestEvent
from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.absence.insured.parental.hourly.models import (
        ParentalHourlyClause,
    )

__all__ = ["check_cumulation"]


def check_cumulation(
    events: Iterable[object], clause: ParentalHourlyClause | None
) -> None:
    """Reject a day of leave by the hour that is also a day of nursing rest.

    Raises:
        InvalidInputError: When the general criterion applies (the CCNL is
            recorded and sets no hours of its own, no local agreement) and
            a day holds both.
    """
    if clause is None:
        return
    items = tuple(events)
    rests = {
        hours.day
        for event in items
        if isinstance(event, NursingRestEvent)
        for hours in event.hours
    }
    for event in items:
        if not isinstance(event, HourlyParentalLeaveEvent):
            continue
        if event.local_hourly_agreement is not False:
            continue
        both = sorted(
            h.day
            for h in event.hours
            if h.day in rests and not clause.sets_hours_on(h.day)
        )
        if both:
            msg = (
                "HourlyParentalLeaveEvent.hours: the leave by the hour cannot "
                f"fall on a day of nursing rest ({both[0]}): art. 32 c. 1-ter "
                "D.Lgs. 151/2001"
            )
            raise InvalidInputError(
                msg, field="HourlyParentalLeaveEvent.hours", feature="parental_leave"
            )
