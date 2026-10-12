"""Inputs of the run steps: the variable events and the amounts input.

The steps of :mod:`._pipeline` call these helpers, which gather the run
context into the arguments of the event processing and of the amounts
computation.
"""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.amount.types import PublicTerms, _AmountsInput
from ccnl_engine.balance.obligation.models import (
    TRATTAMENTO_RECOVERY,
    ULTERIORE_RECOVERY,
)
from ccnl_engine.contribution.additional_ivs.services import (
    additional_ivs_position,
)
from ccnl_engine.contribution.domestic.services import _domestic_hourly_rate
from ccnl_engine.contribution.enam.services import enam_stipendio
from ccnl_engine.employment.spell.models import spell_days
from ccnl_engine.event.allocation.services import (
    _process_events,
    worker_facts_of,
)
from ccnl_engine.event.facade import FringeEvent
from ccnl_engine.family.child.rules import (
    children_within_income_limit,
)
from ccnl_engine.family.inputs import DependentRelationship
from ccnl_engine.fund.assistance.policies import assistance_terms
from ccnl_engine.fund.contractual.rules import contractual_run
from ccnl_engine.pay_item.services import _int_value
from ccnl_engine.pension_fund.decision.services import pension_terms
from ccnl_engine.run.models import RunKind
from ccnl_engine.severance.provision.services import (
    tfr_treasury_fund,
)
from ccnl_engine.sickness.services import sickness_terms
from ccnl_engine.variable_pay.benefit.handlers import fringe_threshold_of
from ccnl_engine.working_time.overtime.policies import CCNLOvertimeBands
from ccnl_engine.working_time.standby.handlers import StandbyTerms

if TYPE_CHECKING:
    from ccnl_engine.event.total.handlers import _EventTotals
    from ccnl_engine.family.models import FamilyDeductionRules
    from ccnl_engine.ledger.models import LedgerEntry
    from ccnl_engine.pay_item.facade import PayItem
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.surtax.models import SurtaxRules
    from ccnl_engine.tax_credit.recovery.models import RecoveryPlan

__all__ = ["amounts_input", "variable_events"]

#: Fact that leaves the children condition of the fringe threshold unknown.
OWN_INCOME = "own_income"


def variable_events(
    ctx: RunContext,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Post the variable events of the run.

    Returns:
        The event totals, and the items and entries of the events.
    """
    request, opening = ctx.request, ctx.opening
    var_pay = ctx.var_pay_rules
    return _process_events(
        request.events,
        ctx.cp,
        ctx.contract.tctx.payment,
        ctx.run_id,
        ctx.contract.date_ctx,
        ctx.resolver,
        ctx.policy_context,
        fringe_threshold_of(
            var_pay.fringe_benefit,
            var_pay.year,
            with_children=_children_within_limit(ctx),
            missing_fact=None if request.family_composition is None else OWN_INCOME,
        ),
        opening_fringe_ytd=opening.cash.fringe.value,
        opening_fringe_taxed=opening.cash.fringe.taxed,
        pdr_income_ceiling=ctx.var_pay_rules.pdr.income_ceiling,
        rinnovo_regime=ctx.var_pay_rules.rinnovo,
        work_time_regime=ctx.var_pay_rules.notte_festivi_turni,
        opening_work_time_cap=opening.cash.work_time_regime,
        worker_facts=worker_facts_of(request, withholding_agent=ctx.withholding_agent),
        overtime_bands=CCNLOvertimeBands.of(
            ctx.contract.ccnl,
            ctx.contract.tctx.competence.year,
            ctx.request.level_code,
        ),
        sickness=sickness_terms(ctx),
        travel_allowance=var_pay.travel_allowance,
        standby=_standby_terms(ctx),
    )


def _standby_terms(ctx: RunContext) -> StandbyTerms:
    ccnl = ctx.contract.ccnl
    work = ccnl.work_rules
    bands = CCNLOvertimeBands.of(ccnl, ctx.contract.tctx.competence.year)
    return StandbyTerms(
        None if work is None else work.standby_rules,
        ctx.request.level_code,
        bands.ruleset,
        bands.version,
    )


def _children_within_limit(ctx: RunContext) -> bool | None:
    """Return whether a child of the family is within the limit of art. 12 c. 2.

    Only a fringe benefit reads it: a run without one does not load the
    art. 12 rules for it.

    Returns:
        ``None`` without a fringe benefit in the run, without a family
        composition, or with a child whose own income is unknown and none
        within the limit; ``False`` without a child.
    """
    request = ctx.request
    family = request.family_composition
    if family is None or not any(isinstance(e, FringeEvent) for e in request.events):
        return None
    children = [
        d for d in family.dependents if d.relationship is DependentRelationship.CHILD
    ]
    if not children:
        return False
    year = ctx.fiscal_year
    rules = ctx.repo.load_family_deduction_rules(year)
    return children_within_income_limit(children, rules.children, year)


def _public_terms(ctx: RunContext) -> PublicTerms:
    """Return what the contributions of a public employee depend on.

    The Assicurazione Sociale Vita is the employer's statement, else the
    value the CCNL fixes.

    Returns:
        The regime, the ASV and the ENAM stipendio of the run.
    """
    stated = ctx.request.employer.public_life_insurance
    fixed = ctx.contract.ccnl.meta.public_life_insurance
    return PublicTerms(
        end_of_service=ctx.request.public_end_of_service,
        life_insurance=fixed if stated is None else stated,
        enam_stipendio=enam_stipendio(ctx),
    )


def _recovery_plans(
    ctx: RunContext, fiscal_year: int
) -> tuple[RecoveryPlan | None, RecoveryPlan | None]:
    """Return the recovery plans of the trattamento and the ulteriore.

    Returns:
        The plans of the tax year, the trattamento's first.
    """
    obligations = ctx.opening.cash.obligations
    return (
        obligations.recovery_of(fiscal_year, TRATTAMENTO_RECOVERY),
        obligations.recovery_of(fiscal_year, ULTERIORE_RECOVERY),
    )


def _sick_pay_regime(ctx: RunContext) -> str | None:
    """Return the INPS sick-pay regime the CCNL names for its workers.

    Returns:
        ``work_rules.sickness_rules.inps_regime``; ``None`` without it.
    """
    work = ctx.contract.ccnl.work_rules
    sickness = None if work is None else work.sickness_rules
    return None if sickness is None else sickness.inps_regime


def amounts_input(
    ctx: RunContext,
    totals: _EventTotals,
    surtax_rules: SurtaxRules | None,
    family_rules: FamilyDeductionRules | None,
    *,
    ivs_ceiling_applies: bool,
    inps_minimum: Decimal | None = None,  # None when not determined
) -> _AmountsInput:
    """Gather what the amounts of the run are computed from.

    Returns:
        The input of the amounts computation.
    """
    request, contract, fiscal_year = ctx.request, ctx.contract, ctx.fiscal_year
    trattamento, ulteriore = _recovery_plans(ctx, fiscal_year)
    return _AmountsInput(
        monthly_gross=ctx.monthly_gross,
        in_kind=ctx.chain.in_kind_total,
        tfr_excluded=ctx.chain.tfr_excluded_total,
        event_inps_base=totals.inps_base,
        event_tfr_base=totals.tfr_base,
        event_irpef_base=totals.irpef_base,
        event_separate_base=totals.separate_irpef_base,
        event_substitute_base=totals.substitute_base,
        opening=ctx.opening.cash,
        ytd_inps_base=ctx.ytd_inps_base,
        withholding=ctx.withholding,
        upcoming_gross=ctx.upcoming_gross,
        rules=contract.year_rules,
        contract_type=request.contract_type,
        category=ctx.worker_category,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=family_rules,
        current_year=request.current_year,
        ivs_ceiling_applies=ivs_ceiling_applies,
        inps_minimum=inps_minimum,
        pdr_rules=ctx.var_pay_rules.pdr,
        weekly_hours=_int_value(request.weekly_hours),
        contributable_hours=_contributable_hours(request),
        domestic_hourly_rate=_domestic_rate(ctx),
        eligible_work_days=spell_days(ctx.employment_spells),
        fixed_term_in_year=any(s.fixed_term for s in ctx.employment_spells),
        period_days=_period_days(ctx),
        recovery_plan=trattamento,
        ulteriore_plan=ulteriore,
        installment_run=ctx.installment_run,
        withholding_agent=ctx.withholding_agent,
        pension=pension_terms(ctx),
        contractual_fund=contractual_run(ctx),
        conguaglio=ctx.conguaglio,
        surtax_obligations=ctx.opening.cash.obligations.surtax,
        run_month=request.period_id.month,
        run_kind=ctx.run_kind,
        foreign_taxes=request.prior_year.foreign_taxes,
        deferred_irpef=_deferred_irpef(ctx),
        additional_ivs=additional_ivs_position(ctx),
        tfr_treasury_fund=tfr_treasury_fund(ctx),
        public=_public_terms(ctx),
        assistance=assistance_terms(contract.ccnl, contract.tctx.competence),
        solidarity_fund=contract.ccnl.parameters.solidarity_fund,
        sick_pay_regime=_sick_pay_regime(ctx),
    )


def _domestic_rate(ctx: RunContext) -> Decimal | None:
    """Return the hourly rate a domestic CCNL bands its contributions on.

    Returns:
        The rate of the regular monthly pay, benefits in kind included,
        ``None`` outside domestic work.
    """
    contract = ctx.contract
    return _domestic_hourly_rate(
        contract.ccnl,
        contract.year_rules,
        ctx.regular_gross + ctx.regular_chain.in_kind_total,
        _int_value(ctx.request.weekly_hours),
        contract.tctx.competence,
    )


def _contributable_hours(request: PeriodCalculationRequest) -> Decimal | None:
    """Return the contributable hours of a domestic run, if stated.

    Returns:
        The value of the request's contributable hours, or ``None``.
    """
    hours = request.contributable_hours
    return None if hours is None else hours.value


def _period_days(ctx: RunContext) -> int:
    """Return the days of the pay period the deductions are proportioned to.

    Art. 23 c. 2 lett. a) DPR 600/1973 applies the art. 12 and 13 TUIR
    deductions "rapportate al periodo stesso"; the days are the calendar
    days of the month of a regular run the employment covers.

    Returns:
        Zero for a run that is not a regular month: it takes no deduction.
    """
    if ctx.run_kind is not RunKind.REGULAR:
        return 0
    year, month = ctx.request.period_id.year, ctx.request.period_id.month
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    period = ctx.request.employment_period
    if period is not None:
        first = max(first, period.started_on)
        last = last if period.ended_on is None else min(last, period.ended_on)
    return max(0, (last - first).days + 1)


def _deferred_irpef(ctx: RunContext) -> Decimal:
    """Return the IRPEF a conguaglio of the run's tax year deferred.

    Returns:
        Zero without a deferral of the tax year.
    """
    deferred = ctx.opening.cash.obligations.deferred_of(ctx.fiscal_year)
    return Decimal(0) if deferred is None else deferred.irpef
