"""Seniority increments of a tiered ladder: counts and amounts."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.amount.policies_rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.seniority.models import SeniorityTier

__all__ = ["count_from_tiers", "resolve_tier_amount"]

_ZERO = Decimal(0)


def count_from_tiers(tiers: tuple[SeniorityTier, ...], seniority_months: int) -> int:
    """Sum increments earned across all tiers from service months.

    Tiers are consumed in order. Each tier's full capacity
    (``cadence_months * maximum_count``) of service months is exhausted
    before advancing to the next tier.

    Returns:
        Total increment count across all tiers.
    """
    remaining = seniority_months
    total = 0
    for tier in tiers:
        count = min(remaining // tier.cadence_months, tier.maximum_count)
        total += count
        # Consume the tier's full capacity (not just the months used) so the
        # remainder correctly reflects when the worker has passed the tier
        # boundary and entered the next one.  After the break, `remaining` is
        # negative and intentionally ignored — only `total` is returned.
        remaining -= tier.maximum_count * tier.cadence_months
        if remaining < 0:
            break
    return total


def _tier_amount(
    tier: SeniorityTier, level_code: str, count: int, as_of: date
) -> Decimal:
    """Return ``count`` increments of a tier, reading its amount only if due.

    Returns:
        Zero without increments or without an amount for the level.
    """
    amount = tier.amount_by_level.get(level_code)
    if count <= 0 or amount is None:
        return _ZERO
    return amount.value_at(as_of) * Decimal(count)


def resolve_tier_amount(
    tiers: tuple[SeniorityTier, ...],
    level_code: str,
    as_of: date,
    *,
    seniority_months: int | None = None,
    count_override: int | None = None,
) -> Decimal:
    """Compute total seniority amount from tiered rules.

    Dispatches to count-based distribution when ``count_override`` is given,
    otherwise uses month-based distribution from ``seniority_months``.

    Returns:
        Rounded total monthly seniority amount for the level.

    Raises:
        InvalidInputError: If both ``seniority_months`` and ``count_override``
            are ``None``.
    """
    if count_override is not None:
        remaining = count_override
        total = _ZERO
        for tier in tiers:
            if remaining <= 0:
                break
            tier_count = min(remaining, tier.maximum_count)
            total += _tier_amount(tier, level_code, tier_count, as_of)
            remaining -= tier_count
        return money(total)
    # month-based path
    if seniority_months is None:
        msg = "seniority_months is required when count_override is not given"
        raise InvalidInputError(msg, feature="seniority")
    remaining_m = seniority_months
    total = _ZERO
    for tier in tiers:
        count = min(remaining_m // tier.cadence_months, tier.maximum_count)
        total += _tier_amount(tier, level_code, count, as_of)
        remaining_m -= tier.maximum_count * tier.cadence_months
        if remaining_m < 0:
            break
    return money(total)
