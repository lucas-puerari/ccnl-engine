"""Days a domestic worker is owed a meal the employer does not give.

CCNL lavoro domestico of 28 October 2025, Art. 14 c. 8: "Al lavoratore
tenuto all'osservanza di un orario giornaliero pari o superiore alle 6 ore,
ove sia concordata la presenza continuativa sul posto di lavoro, spetta la
fruizione del pasto, ovvero, in difetto di erogazione, un'indennità pari al
suo valore convenzionale".  The event states the days of the month the
worker was owed the meal and did not have it; the engine pays them at the
valore convenzionale of Tabella F (``CCNLParameters.meal_indennity_daily``).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_int

__all__ = ["MealIndennityEvent"]

_FEATURE = "meal_indennity"


@dataclass(frozen=True, slots=True)
class MealIndennityEvent:
    """Days of the run month owed a meal the employer did not give.

    Attributes:
        event_date: A day of the month the days fall in.
        days: Days of that month on which the worker, on 6 or more hours
            with continuous presence, was owed the meal and did not have
            it, from 1 to the days of the month.

    Raises:
        InvalidInputError: When ``event_date`` is not a date or ``days`` is
            not an int from 1 to the days of its month.
    """

    event_date: date
    days: int

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.event_date, "MealIndennityEvent.event_date", feature=_FEATURE)
        require_int(self.days, "MealIndennityEvent.days", feature=_FEATURE, minimum=1)
        month = calendar.monthrange(self.event_date.year, self.event_date.month)[1]
        if self.days > month:
            msg = (
                f"MealIndennityEvent.days must be at most {month}, the days of its "
                "month"
            )
            raise InvalidInputError(
                msg, field="MealIndennityEvent.days", feature=_FEATURE
            )
