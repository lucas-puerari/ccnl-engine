"""Seniority increment resolution functions."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        LevelCategory,
        SeniorityIncrements,
        SeniorityTier,
    )

_ZERO = Decimal(0)


def _count_from_tiers(tiers: list[SeniorityTier], seniority_months: int) -> int:
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
        remaining -= tier.maximum_count * tier.cadence_months
        if remaining < 0:
            break
    return total


def _resolve_tier_amount(
    tiers: list[SeniorityTier],
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
    """
    if count_override is not None:
        remaining = count_override
        total = _ZERO
        for tier in tiers:
            if remaining <= 0:
                break
            amount_ts = tier.amount_by_level.get(level_code)
            amount = amount_ts.value_at(as_of) if amount_ts is not None else _ZERO
            tier_count = min(remaining, tier.maximum_count)
            total += amount * Decimal(tier_count)
            remaining -= tier_count
        return money(total)
    # month-based path
    assert seniority_months is not None
    remaining_m = seniority_months
    total = _ZERO
    for tier in tiers:
        amount_ts = tier.amount_by_level.get(level_code)
        amount = amount_ts.value_at(as_of) if amount_ts is not None else _ZERO
        count = min(remaining_m // tier.cadence_months, tier.maximum_count)
        total += amount * Decimal(count)
        remaining_m -= tier.maximum_count * tier.cadence_months
        if remaining_m < 0:
            break
    return money(total)


def seniority_maximum(
    increments: SeniorityIncrements,
    level_code: str,
    worker_category: LevelCategory | None = None,
) -> int:
    """Return the maximum increment count applicable to a level/category.

    Category overrides take precedence over per-level and global values.
    In tiered mode returns the sum of all tier maximums.

    Returns:
        The maximum seniority increment count for the given level.
    """
    if increments.tiers:
        return sum(t.maximum_count for t in increments.tiers)
    if (
        worker_category is not None
        and worker_category in increments.maximum_count_by_category
    ):
        return increments.maximum_count_by_category[worker_category]
    return increments.maximum_count_by_level.get(level_code, increments.maximum_count)


def seniority_first_cadence(
    increments: SeniorityIncrements,
    level_code: str,
    worker_category: LevelCategory | None = None,
) -> int:
    """Return the months of service required for the first increment.

    Category overrides take precedence over per-level and global values.

    Returns:
        The months of service required for the first seniority increment.
    """
    if (
        worker_category is not None
        and worker_category in increments.first_cadence_months_by_category
    ):
        return increments.first_cadence_months_by_category[worker_category]
    return increments.first_cadence_months_by_level.get(
        level_code, increments.first_cadence_months or increments.cadence_months
    )


def _resolve_seniority_count(
    seniority_rules: SeniorityIncrements,
    level_code: str,
    seniority_count: int | None,
    seniority_months: int | None,
    *,
    worker_category: LevelCategory | None = None,
) -> int:
    """Resolve the seniority increment count from either explicit input.

    Also applies the ``excluded_categories`` guard: returns 0 when
    ``worker_category`` is in ``seniority_rules.excluded_categories``.

    Returns:
        The resolved seniority increment count, clamped to the level maximum.

    Raises:
        ValueError: If seniority_count exceeds the maximum for the level.
    """
    maximum = seniority_maximum(seniority_rules, level_code, worker_category)
    if seniority_months is not None:
        if seniority_rules.tiers:
            count = _count_from_tiers(seniority_rules.tiers, seniority_months)
        else:
            first = seniority_first_cadence(
                seniority_rules, level_code, worker_category
            )
            if seniority_months < first:
                count = 0
            else:
                count = 1 + (seniority_months - first) // seniority_rules.cadence_months
                count = min(count, maximum)
    else:
        count = seniority_count or 0
        if count > maximum:
            msg = (
                f"seniority_count {count} exceeds the maximum of {maximum} "
                f"for level {level_code!r}"
            )
            raise ValueError(msg)
    if worker_category in seniority_rules.excluded_categories:
        return 0
    return count


def _seniority_amount(
    seniority_rules: SeniorityIncrements,
    level_code: str,
    count: int,
    as_of: date,
    *,
    worker_category: LevelCategory | None,
    is_apprentice: bool,
    seniority_months: int | None,
) -> Decimal:
    """Resolve the monthly seniority amount for one level on one date.

    Handles apprentice amounts, category-specific amounts, tiered ladders,
    flat amounts, and the absent (zero) case. Tiered ladders prefer
    ``seniority_months`` when available; fall back to count-based
    distribution otherwise.

    Returns:
        Rounded monthly seniority amount in EUR.
    """
    # SIMPLIFICATION: apprentices accrue only the CCNL apprentice-specific
    # increment (if any); the level increments start after qualification.
    if is_apprentice:
        raw = (
            seniority_rules.apprentice_amount.value_at(as_of)
            if seniority_rules.apprentice_amount is not None
            else _ZERO
        )
        return money(raw * count)
    if seniority_rules.tiers:
        if seniority_months is not None:
            return _resolve_tier_amount(
                seniority_rules.tiers,
                level_code,
                as_of,
                seniority_months=seniority_months,
            )
        # seniority_count was given directly (no months info); distribute
        # count across tiers sequentially.
        return _resolve_tier_amount(
            seniority_rules.tiers, level_code, as_of, count_override=count
        )
    if worker_category is not None:
        cat_amounts = seniority_rules.amount_by_level_by_category.get(worker_category)
        if cat_amounts is not None and level_code in cat_amounts:
            raw = cat_amounts[level_code].value_at(as_of)
            return money(raw * count)
    if level_code in seniority_rules.amount_by_level:
        raw = seniority_rules.amount_by_level[level_code].value_at(as_of)
        return money(raw * count)
    return _ZERO
