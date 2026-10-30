"""A parental leave (congedo parentale) and the leave already taken for the child.

The event is one span of leave of a parent for one child born to the
couple; its Saturdays, Sundays and holidays are days of leave.  Leave in
pieces is one event per piece, but the Saturdays, Sundays and holidays
between two pieces belong to the leave unless the worker resumes work
between them (holidays or another absence do not): include them in a
piece (INPS FAQ congedo parentale 2023, n. 10).  Pass the event to every
regular run whose month it touches, and each run pays the days of its
month within the employment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.base.inputs import InpsSicknessBase
from ccnl_engine.validators import (
    require_bool,
    require_date,
    require_instance,
    require_int,
)

__all__ = ["ParentalLeaveEvent", "ParentalLeaveTaken"]

_PARENTAL = "parental_leave"


@dataclass(frozen=True, slots=True)
class ParentalLeaveTaken:
    """The indemnified parental leave taken for the child before the event.

    The counters are in days, thirty a month, as INPS keeps them (the
    *contatori* of the congedo parentale): a calendar month of a span is
    thirty days.  They have no default: a counter left at zero would pay
    days at a higher rate than INPS does.

    Attributes:
        own_days: Days the parent took of their months not transferable to
            the other parent (of the nine months of a sole parent).
        enhanced_days: Days of the couple paid at the enhanced rate.
        shared_days: Days the couple took of the further months they share.

    Raises:
        InvalidInputError: When a counter is not a non-negative ``int``.
    """

    own_days: int
    enhanced_days: int
    shared_days: int

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("own_days", "enhanced_days", "shared_days"):
            require_int(
                getattr(self, name),
                f"ParentalLeaveTaken.{name}",
                feature=_PARENTAL,
                minimum=0,
            )


@dataclass(frozen=True, slots=True)
class ParentalLeaveEvent:
    """A span of parental leave of an employee (art. 32 D.Lgs. 151/2001).

    Attributes:
        started_on: First day of the leave.
        ended_on: Last day of the leave.
        child_born_on: Birth day of the child.
        taken: The indemnified leave taken for the child before the event.
        protection_ended_on: Last day of the maternity or paternity leave of
            either parent that ended last, which sets the months paid at
            the enhanced rate; ``None`` when not stated.
        single_parent: Whether the parent is the only one (art. 32 c. 1
            letter c), with nine indemnified months.
        parental_base_pay: Pay of the month before the leave, which the
            INPS indemnity is computed on (art. 23, which art. 34 c. 1
            applies); ``None`` when not stated.

    Raises:
        InvalidInputError: When a day is not a date, the leave ends before
            it starts or starts before the birth, or a field is of the
            wrong type.
    """

    started_on: date
    ended_on: date
    child_born_on: date
    taken: ParentalLeaveTaken
    protection_ended_on: date | None = None
    single_parent: bool = False
    parental_base_pay: InpsSicknessBase | None = None

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("started_on", "ended_on", "child_born_on"):
            require_date(
                getattr(self, name), f"ParentalLeaveEvent.{name}", feature=_PARENTAL
            )
        if self.protection_ended_on is not None:
            require_date(
                self.protection_ended_on,
                "ParentalLeaveEvent.protection_ended_on",
                feature=_PARENTAL,
            )
        require_instance(
            self.taken,
            ParentalLeaveTaken,
            "ParentalLeaveEvent.taken",
            feature=_PARENTAL,
        )
        require_bool(
            self.single_parent, "ParentalLeaveEvent.single_parent", feature=_PARENTAL
        )
        require_instance(
            self.parental_base_pay,
            InpsSicknessBase,
            "ParentalLeaveEvent.parental_base_pay",
            feature=_PARENTAL,
            optional=True,
        )
        if self.ended_on < self.started_on:
            msg = "ParentalLeaveEvent.ended_on must not precede started_on"
            raise InvalidInputError(
                msg, field="ParentalLeaveEvent.ended_on", feature=_PARENTAL
            )
        if self.started_on < self.child_born_on:
            msg = "ParentalLeaveEvent.started_on must not precede child_born_on"
            raise InvalidInputError(
                msg, field="ParentalLeaveEvent.started_on", feature=_PARENTAL
            )

    @property
    def event_date(self) -> date:
        """First day of the leave."""
        return self.started_on

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the days of the leave within ``first``-``last``.

        Returns:
            The first and last day in common, ``None`` when none.
        """
        start, end = max(self.started_on, first), min(self.ended_on, last)
        return None if end < start else (start, end)
