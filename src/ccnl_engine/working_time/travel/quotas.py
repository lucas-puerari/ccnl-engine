"""The daily trasferta of a CCNL that pays it by meals and lodging."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.errors import MissingRuleError

if TYPE_CHECKING:
    from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
    from ccnl_engine.working_time.travel.models import TravelQuotas

__all__ = ["quota_amount"]

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
