"""Level pay chain construction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.seniority import (
    APPRENTICE_SENIORITY,
    _seniority_amount,
)
from ccnl_engine.payroll.service.types import MonthlyPayChain

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import Allowance, Level
    from ccnl_engine.contract.domain.identity import CCNL


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


def service_gated_allowances(
    level: Level, roles: frozenset[str]
) -> tuple[Allowance, ...]:
    """Return the allowances of the level gated by months of service.

    Returns:
        The allowances with a ``service_months_threshold`` whose role, if
        any, the worker holds.
    """
    return tuple(
        a
        for a in level.fixed_allowances
        if a.service_months_threshold is not None
        and (a.role is None or a.role in roles)
    )


def _level_seniority(
    ccnl: CCNL,
    level: Level,
    count: int,
    as_of: date,
    worker_category: WorkerCategory | None,
    seniority_months: int | None,
) -> Decimal | None:
    """Return the seniority the level pays a qualified worker, if readable.

    An apprentice with matured increments is paid the apprentice amount;
    the run records the simplification when the level pays otherwise.

    Returns:
        The level amount, ``None`` when its rule has no value at *as_of*:
        the amounts cannot be shown equal, so the simplification is kept.
    """
    try:
        return _seniority_amount(
            ccnl.parameters.seniority_increments,
            level.code,
            count,
            as_of,
            worker_category=worker_category,
            is_apprentice=False,
            seniority_months=seniority_months,
        )
    except ValueError:
        return None


def _level_chain(
    ccnl: CCNL,
    level: Level,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    worker_category: WorkerCategory | None = None,
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
    simplified = (
        is_apprentice
        and count > 0
        and seniority
        != _level_seniority(
            ccnl, level, count, as_of, worker_category, seniority_months
        )
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
        limitations=(APPRENTICE_SENIORITY,) if simplified else (),
    )
