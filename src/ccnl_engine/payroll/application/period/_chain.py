"""Monthly pay chain of a run: level or apprentice chain, part-time scaling."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.payroll.service.chain import _level_chain
from ccnl_engine.payroll.service.seniority import _resolve_seniority_count

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import Level
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.service.types import MonthlyPayChain


def _seniority_count(
    ccnl: CCNL,
    level: Level,
    seniority_months: int | None,
    worker_category: WorkerCategory | None,
) -> int:
    """Return the seniority increments matured by the worker.

    Returns:
        Zero when the seniority is not declared.
    """
    if seniority_months is None:
        return 0
    return _resolve_seniority_count(
        ccnl.parameters.seniority_increments,
        level.code,
        None,
        seniority_months,
        worker_category=worker_category,
    )


def _part_time(
    chain: MonthlyPayChain,
    weekly_hours: int | None,
    full_time_weekly_hours: int | None,
) -> MonthlyPayChain:
    """Scale ``chain`` to the part-time ratio of the weekly hours.

    Returns:
        ``chain`` unchanged unless ``weekly_hours < full_time_weekly_hours``.
    """
    # Both values are positive: WeeklyHours validates them on construction.
    if (
        full_time_weekly_hours is not None
        and weekly_hours is not None
        and weekly_hours < full_time_weekly_hours
    ):
        return chain.scaled_for_part_time(
            Decimal(weekly_hours) / Decimal(full_time_weekly_hours)
        )
    return chain


def _resolve_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
    *,
    seniority_months: int | None = None,
    roles: frozenset[str] = frozenset(),
    worker_category: WorkerCategory | None = None,
    weekly_hours: int | None = None,
    full_time_weekly_hours: int | None = None,
) -> MonthlyPayChain:
    """Resolve the elementary pay chain for the period.

    Applies part-time scaling when ``weekly_hours < full_time_weekly_hours``.

    Returns:
        :class:`~ccnl_engine.payroll.service.types.MonthlyPayChain` with each
        component rounded and ready for pay-item emission.
    """
    count = _seniority_count(ccnl, level, seniority_months, worker_category)
    if isinstance(contract_type, Apprentice):
        chain, pct, _ = _apprentice_chain(
            ccnl,
            level,
            contract_type,
            count,
            roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
        chain = chain.scaled(pct) if pct is not None else chain
    else:
        chain = _level_chain(
            ccnl,
            level,
            count,
            roles,
            as_of,
            is_apprentice=False,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
    return _part_time(chain, weekly_hours, full_time_weekly_hours)
