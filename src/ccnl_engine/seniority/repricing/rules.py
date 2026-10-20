"""Increments that keep an amount: stated as earned, or matured before a promotion.

The CCNL table prices the increments of a run at its level.  Two cases keep
another amount: the increments a worker states as earned at a fixed amount
(:func:`earned_seniority`), and, under a CCNL that reprices them only when
the next increment matures, those matured before a promotion
(:func:`promoted_seniority`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.seniority.rules import (
    _resolve_seniority_count,
    _seniority_amount,
    seniority_maximum,
)

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.seniority.inputs import EarnedIncrements
    from ccnl_engine.seniority.models import SeniorityIncrements

__all__ = ["earned_seniority", "promoted_seniority"]


def earned_seniority(
    increments: SeniorityIncrements,
    level_code: str,
    earned: EarnedIncrements,
    months_then: int,
    months_now: int,
    as_of: date,
    *,
    worker_category: WorkerCategory | None,
) -> Decimal:
    """Return the seniority of a worker who stated the increments matured.

    Args:
        increments: Seniority rules of the CCNL.
        level_code: Level of the run.
        earned: The increments matured and their amount on the fact date.
        months_then: Months of service on the fact date.
        months_now: Months of service on the run.
        as_of: Date the CCNL amounts are read at.
        worker_category: Category of the worker.

    Returns:
        The stated amount plus the CCNL amount of the increments matured
        since the fact date, never beyond the maximum count of the level.
    """
    then = _resolve_seniority_count(
        increments, level_code, None, months_then, worker_category=worker_category
    )
    now = _resolve_seniority_count(
        increments, level_code, None, months_now, worker_category=worker_category
    )
    room = seniority_maximum(increments, level_code, worker_category) - earned.count
    extra = max(0, min(now - then, room))
    if not extra:
        return earned.monthly

    def priced(count: int) -> Decimal:
        return _seniority_amount(
            increments,
            level_code,
            count,
            as_of,
            worker_category=worker_category,
            is_apprentice=False,
            seniority_months=None,
        )

    return money(earned.monthly + priced(then + extra) - priced(then))


def promoted_seniority(
    increments: SeniorityIncrements,
    level_code: str,
    from_level: str,
    months_then: int,
    months_now: int,
    as_of: date,
    *,
    worker_category: WorkerCategory | None,
) -> Decimal:
    """Return the seniority of a worker promoted since the last increment.

    The CCNL reprices the increments matured before the promotion only when
    the next one matures: until then they keep the amount of
    ``from_level``; from it every increment takes the amount of the level
    of the run.

    Args:
        increments: Seniority rules of the CCNL.
        level_code: Level of the run.
        from_level: Level before the promotion.
        months_then: Months of service on the promotion date.
        months_now: Months of service on the run.
        as_of: Date the CCNL amounts are read at.
        worker_category: Category of the worker.

    Returns:
        The increments matured on the promotion at the amounts of
        ``from_level`` while no increment matured since, else every
        increment at the amounts of ``level_code``.
    """
    then = _resolve_seniority_count(
        increments, from_level, None, months_then, worker_category=worker_category
    )
    now = _resolve_seniority_count(
        increments, level_code, None, months_now, worker_category=worker_category
    )
    level, count = (from_level, then) if now <= then else (level_code, now)
    return _seniority_amount(
        increments,
        level,
        count,
        as_of,
        worker_category=worker_category,
        is_apprentice=False,
        seniority_months=None,
    )
