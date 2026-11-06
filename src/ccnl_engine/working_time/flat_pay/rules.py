"""The hourly divisor of a regime that pays its minimum whatever the hours."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Context, Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.fact.inputs import WeeklyHours

__all__ = ["flat_pay_divisor"]

#: Weeks of a month: a weekly schedule times 52 / 12 is its monthly hours.
_WEEKS_PER_MONTH = Context(prec=28).divide(Decimal(52), Decimal(12))
_CENT = Decimal("0.01")


def flat_pay_divisor(ccnl: CCNL, weekly_hours: WeeklyHours | None) -> CCNL:
    """Return ``ccnl`` with the hourly divisor of the hours actually worked.

    A regime that pays its minimum whatever the hours up to a ceiling
    (``flat_pay_max_weekly_hours``, CCNL lavoro domestico art. 14 c. 2) has
    an hourly rate of the monthly pay over the hours of the employment, not
    over those of the ceiling: the divisor becomes ``weekly_hours x 52 / 12``
    for the INPS hourly bracket, the overtime and the proration alike.

    Returns:
        ``ccnl`` unchanged outside such a regime or without weekly hours.
    """
    params = ccnl.parameters
    if params.flat_pay_max_weekly_hours is None or weekly_hours is None:
        return ccnl
    hours = (weekly_hours.value * _WEEKS_PER_MONTH).quantize(
        _CENT, rounding=ROUND_HALF_UP
    )
    periods = tuple(
        p.model_copy(update={"value": hours}) for p in params.hourly_divisor.periods
    )
    divisor = params.hourly_divisor.model_copy(update={"periods": periods})
    update = {"parameters": params.model_copy(update={"hourly_divisor": divisor})}
    return ccnl.model_copy(update=update)
