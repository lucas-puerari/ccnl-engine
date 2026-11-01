"""Resolution of the context of one run from its request.

The loads and resolutions run in a fixed order, so that when several inputs
are invalid the same error is raised first on every call.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.compensation.change.rules import MonthChange, blended, month_change
from ccnl_engine.compensation.element.services import _resolve_chain
from ccnl_engine.compensation.hourly.services import upcoming_percentages
from ccnl_engine.compensation.proration.services import run_proration
from ccnl_engine.employment.category.rules import resolve_worker_category
from ccnl_engine.extra_month.liquidation.services import (
    run_settlements,
)
from ccnl_engine.extra_month.qualification.services import month_accrual_rule
from ccnl_engine.extra_month.services import (
    run_accrual,
    run_fraction,
)
from ccnl_engine.pay_item.facade import CompetencePeriod
from ccnl_engine.pay_item.policies import PolicyContext
from ccnl_engine.pay_item.services import (
    _apply_extra_month_policy,
    _hours_value,
)
from ccnl_engine.pension_fund.conversion.services import (
    kept_seniority_months,
    seniority_conversion,
)
from ccnl_engine.period.context.agreement.services import load_contract
from ccnl_engine.period.context.services import RunContext
from ccnl_engine.period.payslip.services import resolve_payment
from ccnl_engine.seniority.services import seniority_months_at
from ccnl_engine.withholding.plan.services import (
    resolve_withholding_schedule,
    upcoming_recurring_gross,
)

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import (
        ApprenticeshipScaling,
        MonthlyPayChain,
    )
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.pay_item.policies import PolicyResolver
    from ccnl_engine.period.context.agreement.services import RunContract
    from ccnl_engine.period.ports import KnowledgeRepository
    from ccnl_engine.period.requests import PeriodCalculationRequest

__all__ = ["build_context"]


def _base_chain(
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
    return _resolve_chain(
        contract.ccnl,
        contract.level,
        request.contract_type,
        contract.tctx.competence,
        seniority_months=months,
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
    )


def _with_change(
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
    old_chain, _ = _base_chain(before, old, worker_category)
    old_full, _ = _base_chain(before, old, worker_category, part_time=False)
    chain, full_time = chains
    return (
        blended(old_chain, chain, change.share),
        blended(old_full, full_time, change.share),
    )


def build_context(
    request: PeriodCalculationRequest,
    repo: KnowledgeRepository,
    resolver: PolicyResolver,
) -> RunContext:
    """Normalise ``request`` into the context of its run.

    Returns:
        The run context.
    """
    effective_repo, effective_resolver = repo, resolver
    contract = load_contract(request, effective_repo)
    competence, fiscal_year = contract.tctx.competence, contract.tctx.fiscal_year
    worker_category = resolve_worker_category(
        contract.ccnl, contract.level, request.category, seniority=request.seniority
    )
    chain, apprenticeship = _base_chain(request, contract, worker_category)
    full_time, _ = _base_chain(request, contract, worker_category, part_time=False)
    settlements = run_settlements(request, contract.ccnl)
    payment = resolve_payment(request)
    change = month_change(request, contract.ccnl, payment.run_id.kind)
    if change is not None:
        chain, full_time = _with_change(
            request, contract, worker_category, change, (chain, full_time)
        )
    schedule = resolve_withholding_schedule(request, payment, contract.ccnl, competence)
    opening = request.opening_state
    withholding = schedule.position(payment, opening.cash.paid_runs)
    upcoming_gross = upcoming_recurring_gross(
        chain,
        withholding.upcoming,
        request.employment_period,
        month_accrual_rule(contract.ccnl),
        request.work_pattern,
    )
    accrual = run_accrual(request, contract.ccnl, competence)
    regular_chain = chain
    proration = run_proration(
        request, contract.ccnl, payment.run_id.kind, worker_category
    )
    if proration.hourly is not None:
        upcoming_gross += upcoming_percentages(
            contract.ccnl, chain, competence, withholding.upcoming
        )
    chain = proration.apply(
        _apply_extra_month_policy(chain, payment.run_id.kind, run_fraction(accrual))
    )
    return RunContext(
        request=request,
        repo=effective_repo,
        resolver=effective_resolver,
        contract=contract,
        withholding_schedule=schedule,
        withholding=withholding,
        worker_category=worker_category,
        chain=chain,
        apprenticeship=apprenticeship,
        payment=payment,
        upcoming_gross=upcoming_gross,
        accrual=accrual,
        var_pay_rules=effective_repo.load_variable_pay_rules(fiscal_year),
        policy_context=PolicyContext(
            year=fiscal_year,
            as_of=competence,
            ccnl_id=contract.ccnl.meta.ccnl_id,
            sector=contract.ccnl.meta.tax_sector,
            gross_ytd=opening.cash.earnings.gross,
        ),
        cp=CompetencePeriod(year=request.period_id.year, month=request.period_id.month),
        regular_chain=regular_chain,
        proration=proration,
        settlements=settlements,
        full_time_chain=full_time,
    )
