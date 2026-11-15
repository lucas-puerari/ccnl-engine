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
        TravelQuotas,
    )

__all__ = ["band_hours", "minimum_share", "night_amount", "quota_amount"]

_FEATURE = "travel_allowance"
_ZERO = Decimal(0)


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


def minimum_share(
    event: TravelAllowanceEvent, rules: CcnlTravelAllowance, monthly: Decimal
) -> Decimal:
    """Return the diaria of a share of the daily minimum, none when agreed at hiring.

    Lavoro domestico art. 33 c. 2: no diaria "nel caso in cui il relativo
    obbligo fosse stato contrattualmente previsto nella lettera di assunzione".

    Returns:
        The share of ``monthly`` over the divisor of the daily minimum; zero
        when the hiring letter provides for the duty to travel.

    Raises:
        MissingRuleError: When the event does not state ``agreed_at_hiring``.
    """
    if event.agreed_at_hiring is None:
        msg = (
            "the CCNL pays no diaria when the hiring letter provides for the "
            "duty to travel, and the event does not state it"
        )
        raise MissingRuleError(
            msg,
            as_of=event.event_date,
            feature=_FEATURE,
            remediation="Pass TravelAllowanceEvent.agreed_at_hiring.",
        )
    if event.agreed_at_hiring or rules.minimum_share is None:
        return _ZERO
    return money(rules.minimum_share * monthly / rules.minimum_divisor)


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
