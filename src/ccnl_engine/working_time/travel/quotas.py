"""The daily trasferta of a CCNL that pays it by meals and lodging, or by a share."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
    from ccnl_engine.working_time.travel.models import (
        CcnlTravelAllowance,
        TravelDailyShare,
        TravelQuotas,
    )

__all__ = ["band_hours", "night_amount", "quota_amount", "share_amount"]

_FEATURE = "travel_allowance"
_ZERO = Decimal(0)
_DAY_HOURS = Decimal(24)


def quota_amount(
    event: TravelAllowanceEvent, quotas: TravelQuotas, ruleset: str
) -> Decimal:
    """Return the daily amount of a CCNL that pays by meals and lodging.

    Returns:
        The whole trasferta for two meals and the overnight stay, else each
        meal and the overnight stay at their quotas.

    Raises:
        MissingRuleError: When the event does not state its meals and
            overnight stay, or is abroad, for which the CCNL sets no amount.
    """
    if event.meals is None or event.overnight is None:
        msg = "the CCNL pays the trasferta by meals and lodging: state them"
        raise MissingRuleError(msg, as_of=event.event_date, feature=_FEATURE)
    if event.abroad:
        msg = "the CCNL sets no quotas for a trasferta abroad: state daily_amount"
        raise MissingRuleError(msg, as_of=event.event_date, feature=_FEATURE)
    day = event.event_date
    with rule_scope(ruleset=ruleset, feature=_FEATURE):
        if event.meals == 2 and event.overnight:
            return quotas.whole.value_at(day)
        overnight = quotas.overnight.value_at(day) if event.overnight else _ZERO
        return quotas.meal.value_at(day) * event.meals + overnight


def share_amount(
    event: TravelAllowanceEvent, share: TravelDailyShare, monthly: Decimal
) -> Decimal:
    """Return the diaria of a share of the daily pay.

    Returns:
        ``rate`` (``abroad_rate`` abroad, ``partial_rate`` for a day of
        less than 24 hours past ``partial_from_hours``, nothing below it)
        times ``monthly`` over the divisor, less the discount of a day
        without an overnight stay; zero when the hiring letter provides for
        the travel and the CCNL then pays none.  An event that does not
        state a fact the diaria depends on (``agreed_at_hiring``,
        ``overnight``, ``hours_away``) is rejected by :func:`_require`.
    """
    if share.hiring_letter_exempts:
        _require(event, "agreed_at_hiring", "whether the hiring letter provides for it")
        if event.agreed_at_hiring:
            return _ZERO
    rate = _rate(event, share)
    daily = rate * monthly / share.divisor
    if share.no_overnight_discount:
        _require(event, "overnight", "whether the day has an overnight stay away")
        if not event.overnight:
            daily *= Decimal(1) - share.no_overnight_discount
    return money(daily)


def _rate(event: TravelAllowanceEvent, share: TravelDailyShare) -> Decimal:
    """Return the share of the daily pay a day of ``event`` is paid.

    Returns:
        ``abroad_rate`` abroad, else ``rate``; for a day of fewer than 24
        hours away, ``partial_rate`` past ``partial_from_hours`` and zero
        at or below them.
    """
    rate = share.rate
    if event.abroad and share.abroad_rate is not None:
        rate = share.abroad_rate
    if share.partial_from_hours is None or share.partial_rate is None:
        return rate
    _require(event, "hours_away", "the hours away of each day")
    hours = event.hours_away or _ZERO
    if hours >= _DAY_HOURS:
        return rate
    return share.partial_rate if hours > share.partial_from_hours else _ZERO


def _require(event: TravelAllowanceEvent, field: str, what: str) -> None:
    """Reject an event that does not state ``field``.

    Raises:
        MissingRuleError: When ``field`` is ``None``.
    """
    if getattr(event, field) is None:
        msg = f"the CCNL diaria depends on {what}, and the event does not state it"
        raise MissingRuleError(
            msg,
            as_of=event.event_date,
            feature=_FEATURE,
            remediation=f"Pass TravelAllowanceEvent.{field}.",
        )


def night_amount(
    event: TravelAllowanceEvent, rules: CcnlTravelAllowance, ruleset: str
) -> Decimal:
    """Return the CCNL night allowance of the days of the event.

    Returns:
        The amount for each day of the hours the CCNL requires, zero
        without the allowance or the hours.
    """
    night, hours = rules.night_allowance, event.hours_away
    if night is None or hours is None or hours < rules.night_from_hours:
        return _ZERO
    with rule_scope(ruleset=ruleset, feature=_FEATURE):
        return money(night.value_at(event.event_date) * event.days)


def band_hours(event: TravelAllowanceEvent, rules: CcnlTravelAllowance) -> Decimal:
    """Return the hours the CCNL bands are read on.

    Returns:
        The mission hours of a CCNL with mission-duration bands, else the
        hours away of the day.

    Raises:
        MissingRuleError: When the event does not state them.
    """
    hours = event.mission_hours if rules.mission_duration else event.hours_away
    if hours is None:
        msg = (
            "the CCNL requires the total mission duration in mission_hours"
            if rules.mission_duration
            else "the CCNL requires hours_away for its daily travel bands"
        )
        raise MissingRuleError(msg, as_of=event.event_date, feature=_FEATURE)
    return hours
