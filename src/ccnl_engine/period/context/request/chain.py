"""The regular pay chain of a run: the month's, and the one of its ratei."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.apprenticeship.dual.settlement import ratei_apprentice
from ccnl_engine.compensation.change.rules import blended
from ccnl_engine.compensation.element.services import _resolve_chain
from ccnl_engine.pay_item.services import _hours_value
from ccnl_engine.pension_fund.conversion.services import (
    kept_seniority_months,
    seniority_conversion,
)
from ccnl_engine.seniority.age.rules import months_from_age
from ccnl_engine.seniority.credit import credited_increment_months
from ccnl_engine.seniority.freeze.rules import (
    months_in_cohort,
    months_without_freeze,
)
from ccnl_engine.seniority.services import seniority_months_at

if TYPE_CHECKING:
    from ccnl_engine.compensation.change.rules import MonthChange
    from ccnl_engine.compensation.element.types import (
        ApprenticeshipScaling,
        MonthlyPayChain,
    )
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.extra_month.models import ExtraMonthAccrual
    from ccnl_engine.period.context.agreement.services import RunContract
    from ccnl_engine.period.requests import PeriodCalculationRequest

__all__ = ["base_chain", "ratei_chain", "with_change"]


def base_chain(
    request: PeriodCalculationRequest,
    contract: RunContract,
    worker_category: WorkerCategory | None,
    *,
    part_time: bool = True,
) -> tuple[MonthlyPayChain, ApprenticeshipScaling | None]:
    """Return the pay chain of a regular month for the worker.

    A worker who converted the seniority increments into fund
    contributions is paid only those matured by the request, frozen
    (:mod:`._seniority_conversion`).  ``part_time`` false leaves the chain
    at full time whatever the weekly hours.

    Returns:
        The chain before any extra-month adjustment, and the apprenticeship
        scaling applied to it.
    """
    months = seniority_months_at(request.seniority, contract.tctx.competence)
    if months is not None and seniority_conversion(contract.ccnl, request):
        months = kept_seniority_months(request)
    elif months is not None and request.seniority is not None:
        period = request.employment_period
        increments = contract.ccnl.parameters.seniority_increments
        months = months_without_freeze(
            months_from_age(
                months,
                increments.counted_from_age,
                request.seniority.birth_date,
                None if period is None else period.started_on,
                contract.tctx.competence,
            ),
            increments.freezes,
            request.seniority.as_of,
            contract.tctx.competence,
        )
        months = months_in_cohort(
            months,
            increments.hired_until,
            contract.tctx.competence,
            None if period is None else period.started_on,
        )
    # An unknown apprenticeship duration counts the service alone (a lower
    # bound); other service-gated elements use the ordinary service months.
    increment_months = credited_increment_months(
        months, contract.ccnl.parameters.seniority_increments, request
    )
    return _resolve_chain(
        contract.ccnl,
        contract.level,
        request.contract_type,
        contract.tctx.competence,
        seniority_months=months,
        increment_months=increment_months,
        roles=request.roles or frozenset(),
        worker_category=worker_category,
        weekly_hours=_hours_value(request.weekly_hours) if part_time else None,
        full_time_weekly_hours=_hours_value(request.full_time_weekly_hours),
        hired_on=(
            None
            if request.employment_period is None
            else request.employment_period.started_on
        ),
        seniority=request.seniority,
        level_started_on=request.level_started_on,
        career_months=(
            None
            if request.seniority is None
            else request.seniority.career_months_in_month(
                contract.tctx.competence.year, contract.tctx.competence.month
            )
        ),
    )


def with_change(
    request: PeriodCalculationRequest,
    contract: RunContract,
    worker_category: WorkerCategory | None,
    change: MonthChange,
    chains: tuple[MonthlyPayChain, MonthlyPayChain],
) -> tuple[MonthlyPayChain, MonthlyPayChain]:
    """Return the chain and the full-time chain of a month split by a promotion.

    The level before is priced with the seniority before the promotion.

    Returns:
        Each chain shared between the level before and the level of the run.
    """
    seniority = request.seniority
    before = replace(
        request,
        seniority=None if seniority is None else replace(seniority, promotion=None),
    )
    old = replace(contract, level=contract.ccnl.level_by_code(change.from_level))
    old_chain, _ = base_chain(before, old, worker_category)
    old_full, _ = base_chain(before, old, worker_category, part_time=False)
    chain, full_time = chains
    return (
        blended(old_chain, chain, change.share),
        blended(old_full, full_time, change.share),
    )


def ratei_chain(
    request: PeriodCalculationRequest,
    contract: RunContract,
    worker_category: WorkerCategory | None,
    change: MonthChange | None,
    chains: tuple[MonthlyPayChain, tuple[ExtraMonthAccrual, ...]],
) -> MonthlyPayChain:
    """Return the regular chain the ratei the run liquidates are paid at.

    A first- or third-level apprentice's final settlement weighs them by
    the hours they accrued over, the promotion of the month included.

    Returns:
        The chain of ``chains`` but for such a settlement.
    """
    chain, settlements = chains
    ccnl_id = contract.ccnl.meta.ccnl_id
    apprentice = ratei_apprentice(request.contract_type, settlements, ccnl_id)
    if apprentice is None:
        return chain
    request = replace(request, contract_type=apprentice)
    ratei, _ = base_chain(request, contract, worker_category)
    if change is not None:
        pair = (ratei, ratei)
        ratei, _ = with_change(request, contract, worker_category, change, pair)
    return ratei
