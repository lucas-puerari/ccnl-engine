"""Pay daily presence allowances from counted, qualifying days."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.compensation.presence.models import DailyPresenceAllowance
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.pay_item.rounding.policies import money


def add_daily_presence(
    chain: MonthlyPayChain,
    rules: tuple[DailyPresenceAllowance, ...],
    as_of: date,
    roles: frozenset[str],
    work_days: int | None,
    site_days: int | None,
) -> MonthlyPayChain:
    """Add actual daily earnings to an already-prorated regular pay chain.

    A missing count leaves only the applicable daily earning out; the
    missing-fact issue is reported independently by the employment facts.

    Returns:
        The chain with each payable daily earning added once.

    Raises:
        InvalidInputError: When incompatible daily-rate brackets both apply.
    """
    earnings = []
    groups: set[str] = set()
    for rule in rules:
        if not rule.applies(roles) or not rule.rate.applies_on(as_of):
            continue
        group = rule.exclusive_group
        if group is not None:
            if group in groups:
                msg = f"incompatible daily presence roles in {group}"
                raise InvalidInputError(msg, feature="presence_allowances")
            groups.add(group)
        days = work_days if rule.day_kind == "work" else site_days
        if days is None:
            continue
        allowance = Allowance(
            code=rule.code,
            description=rule.description,
            monthly=rule.rate,
            months_per_year=12,
            tfr_relevant=rule.tfr_relevant,
            apprenticeship_pct_relevant=False,
            part_time_proportionable=False,
            provenance=rule.provenance,
        )
        earnings.append((allowance, money(rule.rate.value_at(as_of) * Decimal(days))))
    return replace(chain, allowances=(*chain.allowances, *earnings))
