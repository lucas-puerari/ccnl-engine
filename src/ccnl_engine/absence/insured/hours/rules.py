"""The pay of hours of an insured permit or rest, at the CCNL hourly base.

An hour is the hourly base of the CCNL on its day
(:class:`~ccnl_engine.working_time.hourly.policies.HourlyTerms`), deducted
and paid back alike.  Where the engine cannot derive that base the hours
post nothing and the caller records an ``incomplete`` rule issue.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus, IssueCause
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.hours.inputs import LeaveHours
    from ccnl_engine.working_time.hourly.policies import HourlyTerms

__all__ = ["hours_pay"]

_ZERO = Decimal(0)
_BASE_FIELD = "the hourly base of LeaveHours.hours"


def hours_pay(
    items: tuple[LeaveHours, ...],
    span: tuple[date, date],
    hourly: HourlyTerms,
    capability: str,
    code: str,
) -> Decimal | CalculationIssue:
    """Return the pay of the hours of ``items`` in ``span``, or why not.

    Returns:
        Each hour at the CCNL hourly base of its day, rounded once; the
        ``incomplete`` issue ``code`` when a base cannot be derived.
    """
    total = _ZERO
    for item in items:
        if not span[0] <= item.day <= span[1]:
            continue
        try:
            base = hourly.base(item.day, _BASE_FIELD, capability)
        except MissingRuleError as error:
            return CalculationIssue(
                code=code,
                message=f"the hours post nothing: {error.detail}",
                status=CalculationStatus.INCOMPLETE,
                capability=capability,
                cause=IssueCause.RULE,
            )
        total += base.rate * item.hours
    return money(total)
