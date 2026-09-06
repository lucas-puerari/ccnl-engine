"""Level pay chain construction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.compute.seniority import _seniority_amount
from ccnl_engine.engine.compute.types import MonthlyPayChain

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.domain.ccnl import CCNL, Allowance, Level, LevelCategory


def _allowance_active(
    allowance: Allowance,
    roles: frozenset[str],
    seniority_months: int | None,
) -> bool:
    """Return whether an allowance is active for the given roles and service time.

    Returns:
        True when the allowance's role and service-months conditions are met.
    """
    if allowance.role is not None and allowance.role not in roles:
        return False
    threshold = allowance.service_months_threshold
    if threshold is None:
        return True
    return seniority_months is not None and seniority_months >= threshold


def _level_chain(
    ccnl: CCNL,
    level: Level,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    worker_category: LevelCategory | None = None,
    is_apprentice: bool,
    seniority_months: int | None = None,
) -> MonthlyPayChain:
    seniority_rules = ccnl.parameters.seniority_increments
    seniority = _seniority_amount(
        seniority_rules,
        level.code,
        count,
        as_of,
        worker_category=worker_category,
        is_apprentice=is_apprentice,
        seniority_months=seniority_months,
    )
    allowances = tuple(
        (a, a.monthly.value_at(as_of))
        for a in level.fixed_allowances
        if _allowance_active(a, roles, seniority_months)
    )
    return MonthlyPayChain(
        base=level.base_salary.value_at(as_of),
        seniority=seniority,
        allowances=allowances,
    )
