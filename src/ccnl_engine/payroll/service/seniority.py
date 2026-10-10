"""Seniority increment resolution functions."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.seniority_tiers import (
    count_from_tiers,
    resolve_tier_amount,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.employment.models_category import WorkerCategory
    from ccnl_engine.contract.seniority.models import SeniorityIncrements

_ZERO = Decimal(0)

#: Variant of the CCNL limitation of an apprentice whose CCNL declares no
#: apprentice seniority amount: the engine pays none, and the CCNL text read
#: for the ruleset does not settle whether the level increments are due.
APPRENTICE_SENIORITY_VARIANT = "apprentice_seniority"

#: Reason of a seniority decision when the level pays the worker no
#: increment: the capability does not apply to the run.
NOT_APPLICABLE_BY_CONTRACT = "not_applicable_by_contract"


def seniority_maximum(
    increments: SeniorityIncrements,
    level_code: str,
    worker_category: WorkerCategory | None = None,
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


def increments_apply(
    increments: SeniorityIncrements,
    level_code: str,
    worker_category: WorkerCategory | None,
    *,
    apprentice: bool,
) -> bool:
    """Return whether the level can pay seniority increments to the worker.

    Read from the shape of the rules, never from a value of their series.
    An unknown category counts when any category is paid on the level.

    Args:
        increments: Seniority rules of the CCNL.
        level_code: Level whose increments are paid.
        worker_category: Category of the worker, ``None`` when unknown.
        apprentice: Whether the worker is an apprentice, paid the
            apprentice amount when the CCNL declares one.

    Returns:
        ``False`` for an excluded category, a zero maximum or a level
        without an amount; ``True`` otherwise.
    """
    if (
        worker_category in increments.excluded_categories
        or seniority_maximum(increments, level_code, worker_category) <= 0
    ):
        return False
    if apprentice and increments.apprentice_amount is not None:
        return True
    return _level_has_amount(increments, level_code, worker_category)


def _level_has_amount(
    increments: SeniorityIncrements,
    level_code: str,
    worker_category: WorkerCategory | None,
) -> bool:
    """Return whether the rules carry an increment amount for the level.

    Returns:
        Whether a tier, the level table or a category table lists it.
    """
    if increments.tiers:
        return any(level_code in tier.amount_by_level for tier in increments.tiers)
    by_category = increments.amount_by_level_by_category
    if worker_category is None:
        by_category_listed = any(level_code in a for a in by_category.values())
    else:
        by_category_listed = level_code in by_category.get(worker_category, {})
    return level_code in increments.amount_by_level or by_category_listed


def seniority_first_cadence(
    increments: SeniorityIncrements,
    level_code: str,
    worker_category: WorkerCategory | None = None,
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
    worker_category: WorkerCategory | None = None,
) -> int:
    """Resolve the seniority increment count from either explicit input.

    Also applies the ``excluded_categories`` guard: returns 0 when
    ``worker_category`` is in ``seniority_rules.excluded_categories``.

    Returns:
        The resolved seniority increment count, clamped to the level maximum.

    Raises:
        InvalidInputError: If seniority_count exceeds the maximum for the level.
    """
    maximum = seniority_maximum(seniority_rules, level_code, worker_category)
    if seniority_months is not None:
        if seniority_rules.tiers:
            count = count_from_tiers(seniority_rules.tiers, seniority_months)
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
            remediation = (
                f"Use a seniority_count of at most {maximum} for level {level_code!r}."
            )
            raise InvalidInputError(msg, feature="seniority", remediation=remediation)
    if worker_category in seniority_rules.excluded_categories:
        return 0
    return count


def _seniority_amount(
    seniority_rules: SeniorityIncrements,
    level_code: str,
    count: int,
    as_of: date,
    *,
    worker_category: WorkerCategory | None,
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
    # No increment due, or an excluded category: no amount is read, so a
    # series not yet in force on ``as_of`` does not matter.
    if count <= 0 or worker_category in seniority_rules.excluded_categories:
        return _ZERO
    # Apprentices accrue only the CCNL apprentice-specific increment (if
    # any); the level increments start after qualification.  Without an
    # apprentice amount the chain records the CCNL limitation of the
    # APPRENTICE_SENIORITY_VARIANT when it matters.
    if is_apprentice:
        raw = (
            seniority_rules.apprentice_amount.value_at(as_of)
            if seniority_rules.apprentice_amount is not None
            else _ZERO
        )
        return money(raw * count)
    if seniority_rules.tiers:
        # Use months-based distribution when available; fall back to count.
        return resolve_tier_amount(
            seniority_rules.tiers,
            level_code,
            as_of,
            seniority_months=seniority_months,
            count_override=count if seniority_months is None else None,
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
