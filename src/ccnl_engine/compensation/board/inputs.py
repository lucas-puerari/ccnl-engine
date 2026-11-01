"""Days a live-in worker does not take the board and lodging of the employer.

CCNL lavoro domestico of 28 October 2025: the convivente takes board and
lodging in kind, valued by Tabella F (Art. 36 c. 3, monthly value = daily x
30).  On the days the worker does not take them, the employer pays their
value in cash, the indennità sostitutiva: during the ferie (Art. 17 c. 7),
the sospensioni extraferiali (Art. 18 c. 1), the congedo matrimoniale
(Art. 24 c. 2) and an illness or injury spent outside hospital and outside
the employer's home (Art. 27 c. 9, Art. 29 c. 7).  The event states those
days; the engine pays them.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_int

__all__ = ["BoardLodgingEvent"]

_FEATURE = "board_lodging"


@dataclass(frozen=True, slots=True)
class BoardLodgingEvent:
    """Days of the run month without the board and lodging provided in kind.

    Attributes:
        event_date: A day of the month the days fall in.
        days: Days of that month on which the worker did not take the board
            and lodging and is owed their value in cash, from 1 to the days
            of the month.

    Raises:
        InvalidInputError: When ``event_date`` is not a date or ``days`` is
            not an int from 1 to the days of its month.
    """

    event_date: date
    days: int

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.event_date, "BoardLodgingEvent.event_date", feature=_FEATURE)
        require_int(self.days, "BoardLodgingEvent.days", feature=_FEATURE, minimum=1)
        month = calendar.monthrange(self.event_date.year, self.event_date.month)[1]
        if self.days > month:
            msg = (
                f"BoardLodgingEvent.days must be at most {month}, the days of its month"
            )
            raise InvalidInputError(
                msg, field="BoardLodgingEvent.days", feature=_FEATURE
            )
