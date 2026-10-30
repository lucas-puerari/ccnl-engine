"""The extraordinary leave to assist a disabled person (art. 42 c. 5).

Up to two years in a working life for each person assisted, continuous or
in pieces; its Saturdays, Sundays and holidays are days of leave.  Pass the
event to every regular run whose month it touches, and each run pays the
days of its month within the employment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_decimal

__all__ = ["ExtraordinaryLeaveEvent"]

_LEAVE = "extraordinary_leave"


@dataclass(frozen=True, slots=True)
class ExtraordinaryLeaveEvent:
    """A span of extraordinary leave (D.Lgs. 151/2001 art. 42 c. 5).

    INPS pays an indemnity equal to the last pay of fixed and continuous
    items, the employer advancing it, up to a yearly maximum (c. 5-ter);
    the span accrues no leave, 13th or TFR (c. 5-quinquies).

    Attributes:
        started_on: First day of the leave.
        ended_on: Last day of the leave.
        last_fixed_pay: The pay of the fixed and continuous items of the
            last month before the leave; ``None`` when not stated.

    Raises:
        InvalidInputError: When a day is not a date, the leave ends before
            it starts or ``last_fixed_pay`` is not a positive ``Decimal``.
    """

    started_on: date
    ended_on: date
    last_fixed_pay: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        for name in ("started_on", "ended_on"):
            require_date(
                getattr(self, name), f"ExtraordinaryLeaveEvent.{name}", feature=_LEAVE
            )
        require_decimal(
            self.last_fixed_pay,
            "ExtraordinaryLeaveEvent.last_fixed_pay",
            feature=_LEAVE,
            positive=True,
            optional=True,
        )
        if self.ended_on < self.started_on:
            msg = "ExtraordinaryLeaveEvent.ended_on must not precede started_on"
            raise InvalidInputError(
                msg, field="ExtraordinaryLeaveEvent.ended_on", feature=_LEAVE
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
