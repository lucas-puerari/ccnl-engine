"""Leave-taken event: paid leave the worker took in the period."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.validators import parse_enum, require_date, require_decimal

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

__all__ = ["LeaveTakenEvent"]

_FEATURE = "leave"


@dataclass(frozen=True)
class LeaveTakenEvent:
    """Paid leave taken in the period: ferie in days, permits in hours.

    The time off is paid at the normal rate: the monthly pay of the period
    already holds it, so the event adds no pay and deducts none; it
    consumes the balance of its bucket
    (:class:`~ccnl_engine.leave.balance.models.LeaveAccount`).  An unpaid
    absence is an :class:`~ccnl_engine.absence.inputs.AbsenceEvent`.

    Attributes:
        event_date: First day of the leave, within the period.
        bucket: Bucket the leave is taken from.
        quantity: Working days of ferie, on the week of the CCNL (six days
            for a CCNL that counts the week on six whatever the schedule),
            or hours of a permit bucket.  Must be > 0.
    """

    event_date: date
    bucket: LeaveBucket
    quantity: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_date(self.event_date, "LeaveTakenEvent.event_date", feature=_FEATURE)
        bucket = parse_enum(
            self.bucket, LeaveBucket, "LeaveTakenEvent.bucket", feature=_FEATURE
        )
        object.__setattr__(self, "bucket", bucket)
        require_decimal(
            self.quantity, "LeaveTakenEvent.quantity", feature=_FEATURE, positive=True
        )
