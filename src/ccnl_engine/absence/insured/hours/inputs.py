"""Hours of an insured permit or rest taken on one day."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.validators import require_date, require_decimal

__all__ = ["LeaveHours"]

_FEATURE = "insured_absence_hours"
_DAY_HOURS = Decimal(24)


@dataclass(frozen=True, slots=True)
class LeaveHours:
    """Hours of a permit or a rest taken on one day.

    Attributes:
        day: The day of the hours.
        hours: The hours taken, above 0 and at most 24.

    Raises:
        InvalidInputError: When ``day`` is not a date or ``hours`` is not a
            ``Decimal`` within its bounds.
    """

    day: date
    hours: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.day, "LeaveHours.day", feature=_FEATURE)
        require_decimal(
            self.hours,
            "LeaveHours.hours",
            feature=_FEATURE,
            positive=True,
            maximum=_DAY_HOURS,
        )
