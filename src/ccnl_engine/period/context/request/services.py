"""Resolution of the context of one run from its request.

The loads and resolutions run in a fixed order, so that when several inputs
are invalid the same error is raised first on every call.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.compensation.allowance.hourly import pay_hourly_allowances
from ccnl_engine.compensation.change.rules import month_change
from ccnl_engine.compensation.equalisation.rules import equalisation_outcome
from ccnl_engine.compensation.hourly.services import upcoming_percentages
from ccnl_engine.compensation.presence.rules import add_daily_presence
from ccnl_engine.compensation.proration.services import run_proration
from ccnl_engine.compensation.una_tantum.rules import UNA_TANTUM, una_tantum_events
from ccnl_engine.employment.category.rules import resolve_worker_category
from ccnl_engine.extra_month.liquidation.services import run_settlements
from ccnl_engine.extra_month.offset.services import offset_fourteenth
from ccnl_engine.extra_month.qualification.services import month_accrual_rule
from ccnl_engine.extra_month.services import (
    run_accrual,
    run_fraction,
)
from ccnl_engine.pay_item.facade import CompetencePeriod
from ccnl_engine.pay_item.policies import PolicyContext
from ccnl_engine.pay_item.services import (
    _apply_extra_month_policy,
)
from ccnl_engine.period.context.agreement.services import load_contract
from ccnl_engine.period.context.request.chain import (
    base_chain,
    ratei_chain,
    with_change,
)
from ccnl_engine.period.context.services import RunContext
from ccnl_engine.period.payslip.services import resolve_payment
from ccnl_engine.withholding.plan.services import (
    resolve_withholding_schedule,
    upcoming_recurring_gross,
)

if TYPE_CHECKING:
    from ccnl_engine.pay_item.policies import PolicyResolver
    from ccnl_engine.period.context.agreement.services import RunContract
    from ccnl_engine.period.ports import KnowledgeRepository
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.run.models import RunKind

__all__ = ["build_context"]


def _with_equalisation(
    request: PeriodCalculationRequest, contract: RunContract, kind: RunKind
) -> tuple[PeriodCalculationRequest, RunContract]:
    """Add the elemento perequativo the run pays to its events.

    Returns:
        The request with the bonus of the element, and the contract naming
        the element left out when the employer does not state whether it
        has second-level bargaining. Multiple omitted elements are named.
    """
    outcome = equalisation_outcome(request, contract.ccnl, kind)
    if outcome.events:
        request = replace(request, events=(*request.events, *outcome.events))
    unknown_codes = outcome.unknown_codes or (
        (outcome.unknown,) if outcome.unknown is not None else ()
    )
    if unknown_codes:
        unknown = (*contract.premium_unknown, *unknown_codes)
        contract = replace(contract, premium_unknown=unknown)
    return request, contract


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
    chain, apprenticeship = base_chain(request, contract, worker_category)
    full_time, _ = base_chain(request, contract, worker_category, part_time=False)
    settlements = run_settlements(request, contract.ccnl)
    payment = resolve_payment(request)
    change = month_change(request, contract.ccnl, payment.run_id.kind)
    if change is not None:
        chain, full_time = with_change(
            request, contract, worker_category, change, (chain, full_time)
        )
    ratei = ratei_chain(
        request, contract, worker_category, change, (chain, settlements)
    )
    una_tantum, met = una_tantum_events(request, contract.ccnl, payment.run_id.kind)
    if met:
        chain = replace(chain, limitations=(*chain.limitations, UNA_TANTUM))
        request = replace(request, events=(*request.events, *una_tantum))
    request, contract = _with_equalisation(request, contract, payment.run_id.kind)
    schedule = resolve_withholding_schedule(request, payment, contract.ccnl, competence)
    opening = request.opening_state
    withholding = schedule.position(payment, opening.cash.paid_runs)
    upcoming_gross = upcoming_recurring_gross(
        chain,
        withholding.upcoming,
        request.employment_period,
        month_accrual_rule(contract.ccnl),
        request.work_pattern,
        contract.ccnl.parameters.fourteenth_prior_extra_offset,
        request.prior_extra_month_amount,
    )
    accrual = run_accrual(request, contract.ccnl, competence)
    regular_chain = chain
    proration = run_proration(
        request, contract.ccnl, payment.run_id.kind, worker_category
    )
    if proration.hourly is not None:
        upcoming_gross += upcoming_percentages(
            contract.ccnl,
            chain,
            competence,
            withholding.upcoming,
            request.contract_type,
        )
    chain = proration.apply(
        _apply_extra_month_policy(chain, payment.run_id.kind, run_fraction(accrual))
    )
    if payment.run_id.kind in {"regular", "termination"} and proration.posts_pay:
        paid = request.contributable_hours or request.ordinary_hours_worked
        hours = None if paid is None else paid.value
        chain = pay_hourly_allowances(chain, hours, competence)
    if payment.run_id.kind == "fourteenth":
        chain = offset_fourteenth(
            chain,
            contract.ccnl.parameters.fourteenth_prior_extra_offset,
            request.employment_period,
            request.prior_extra_month_amount,
            run_fraction(accrual),
        )
    if payment.run_id.kind == "regular":
        chain = add_daily_presence(
            chain,
            contract.ccnl.parameters.daily_presence_allowances,
            competence,
            request.roles or frozenset(),
            request.presence_days,
            request.site_presence_days,
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
        ratei_chain=ratei,
        proration=proration,
        settlements=settlements,
        full_time_chain=full_time,
    )
