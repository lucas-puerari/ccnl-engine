"""A week of a yearly programme of flexible working time."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.validators import require_date, require_decimal

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

__all__ = ["FlexibilityWeekEvent"]

_FEATURE = "leave"


@dataclass(frozen=True)
class FlexibilityWeekEvent:
    """A week of the employer's programme of flexibility and its hours.

    The hours of the week are paid as the normal week (the pay of the month
    does not change); a week over the normal hours earns the permit of the
    CCNL band it falls in (``LeaveRules.flexibility``), credited to the
    ``flessibilita`` bucket of the programme year
    (``EmployerProfile.flexibility_programme_month``).

    Attributes:
        event_date: First day of the week, within the period.
        hours_worked: Hours worked in the week.  Must be > 0.
    """

    event_date: date
    hours_worked: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_date(
            self.event_date, "FlexibilityWeekEvent.event_date", feature=_FEATURE
        )
        require_decimal(
            self.hours_worked,
            "FlexibilityWeekEvent.hours_worked",
            feature=_FEATURE,
            positive=True,
        )
