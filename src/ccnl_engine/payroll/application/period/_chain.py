"""Monthly pay chain of a run: level or apprentice chain, part-time scaling."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.payroll.service.chain import _level_chain
from ccnl_engine.payroll.service.seniority import _resolve_seniority_count
from ccnl_engine.payroll.service.types import ApprenticeshipScaling

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
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Resolve the elementary pay chain for the period.

    For a percentage apprenticeship the percentage reduces the base salary,
    the seniority and the allowances flagged ``apprenticeship_pct_relevant``;
    the other allowances are paid in full.  Part-time scaling then applies
    when ``weekly_hours < full_time_weekly_hours``.

    Returns:
        :class:`~ccnl_engine.payroll.service.types.MonthlyPayChain` with each
        component rounded and ready for pay-item emission, and the
        apprenticeship scaling applied, ``None`` unless the worker is on a
        percentage apprenticeship track.
    """
    with rule_scope(ruleset=ccnl.meta.ccnl_id):
        chain, scaling = _contract_chain(
            ccnl,
            level,
            contract_type,
            as_of,
            seniority_months=seniority_months,
            roles=roles,
            worker_category=worker_category,
        )
    return _part_time(chain, weekly_hours, full_time_weekly_hours), scaling


def _contract_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
    *,
    seniority_months: int | None,
    roles: frozenset[str],
    worker_category: WorkerCategory | None,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Return the level or apprentice chain of the contract, full time.

    Returns:
        The chain and the apprenticeship scaling, as :func:`_resolve_chain`.
    """
    count = _seniority_count(ccnl, level, seniority_months, worker_category)
    scaling: ApprenticeshipScaling | None = None
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
        if pct is not None:
            scaling = ApprenticeshipScaling.of(chain, pct)
            chain = chain.scaled_for_apprenticeship(pct)
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
    return chain, scaling
