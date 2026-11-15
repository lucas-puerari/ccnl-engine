"""Validation shared by the night, holiday and shift supplement events."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_decimal, require_int

__all__ = ["check_supplement"]

_ZERO = Decimal(0)
#: Hours of a month of 31 days: no event of a month can exceed them.
_HOURS_IN_A_MONTH = Decimal(31 * 24)
#: Turns of a month of 31 days, three a day.
_SHIFTS_IN_A_MONTH = 31 * 3


def check_supplement(
    event_date: object,
    amount: object,
    hours: object,
    event: str,
    feature: str,
    shifts: object = None,
) -> None:
    """Reject a supplement event without a date, or with no amount, hours or turns.

    Raises:
        InvalidInputError: When neither the amount, nor the hours, nor the
            turns are given, or one is out of its range.
    """
    require_date(event_date, f"{event}.event_date", feature=feature)
    require_decimal(
        amount,
        f"{event}.supplement_amount",
        feature=feature,
        minimum=_ZERO,
        optional=True,
    )
    require_decimal(
        hours,
        f"{event}.hours",
        feature=feature,
        positive=True,
        maximum=_HOURS_IN_A_MONTH,
        optional=True,
    )
    require_int(
        shifts,
        f"{event}.shifts",
        feature=feature,
        minimum=1,
        maximum=_SHIFTS_IN_A_MONTH,
        optional=True,
    )
    if amount is None and hours is None and shifts is None:
        msg = (
            f"{event} needs supplement_amount, or the hours or turns the engine "
            "derives it from"
        )
        raise InvalidInputError(msg, field=f"{event}.hours", feature=feature)
