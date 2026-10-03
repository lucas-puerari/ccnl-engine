"""Steps of one run: events, amounts and decisions.

The credits, the withholding cap and the base posting follow in
:mod:`~ccnl_engine.payroll.application.period._posting`.  Each step reads
the :class:`~ccnl_engine.payroll.application.period._context.RunContext`
and the outputs of the steps before it.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _int_value
from ccnl_engine.payroll.application.allocate_events import (
    _process_events,
    worker_facts_of,
)
from ccnl_engine.payroll.application.amounts._compute import _compute_amounts
from ccnl_engine.payroll.application.amounts._domestic import _domestic_hourly_rate
from ccnl_engine.payroll.application.amounts._types import _AmountsInput
from ccnl_engine.payroll.application.handlers._overtime_rate import CCNLOvertimeBands
from ccnl_engine.payroll.application.handlers.benefits import fringe_threshold_of
from ccnl_engine.payroll.application.period._accrual_decisions import (
    accrual_decisions,
)
from ccnl_engine.payroll.application.period._base_decisions import (
    base_stage_decisions,
)
from ccnl_engine.payroll.application.period._caller_rules import (
    caller_supplied_decisions,
)
from ccnl_engine.payroll.application.period._checks import check_absences_within_pay
from ccnl_engine.payroll.application.period._ivs_ceiling import (
    IvsCeiling,
    ivs_ceiling_decision,
    run_ivs_ceiling,
)
from ccnl_engine.payroll.application.period._pension_decision import (
    pension_decision,
    pension_terms,
)
from ccnl_engine.payroll.application.period._run_decisions import contract_decisions
from ccnl_engine.payroll.application.period._seniority import (
    run_seniority,
    seniority_decision,
)
from ccnl_engine.payroll.application.year._extra_month_accrual import (
    settle_extra_months,
)
from ccnl_engine.payroll.domain.obligations import (
    TRATTAMENTO_RECOVERY,
    ULTERIORE_RECOVERY,
)
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.application.handlers._totals import _EventTotals
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.tax import TaxComputation
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules


@dataclass(frozen=True)
class RunEvents:
    """Variable events and extra-month settlements of the run."""

    totals: _EventTotals
    items: tuple[PayItem, ...]
    entries: tuple[LedgerEntry, ...]


@dataclass(frozen=True)
class RunAmounts:
    """Amounts of the run with their INPS and IRPEF computations."""

    amounts: _PeriodAmounts
    contribution_breakdown: ContributionBreakdown
    tax_computation: TaxComputation
    recovery_plan: RecoveryPlan | None
    ivs_ceiling: IvsCeiling | None


def _variable_events(ctx: RunContext) -> RunEvents:
    request, opening = ctx.request, ctx.opening
    var_pay = ctx.var_pay_rules
    totals, items, entries = _process_events(
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
            with_children=request.has_dependent_children,
        ),
        opening_fringe_ytd=opening.cash.fringe.value,
        opening_fringe_taxed=opening.cash.fringe.taxed,
        pdr_income_ceiling=ctx.var_pay_rules.pdr.income_ceiling,
        rinnovo_regime=ctx.var_pay_rules.rinnovo,
        work_time_regime=ctx.var_pay_rules.notte_festivi_turni,
        opening_work_time_cap=opening.cash.work_time_regime,
        worker_facts=worker_facts_of(request, withholding_agent=ctx.withholding_agent),
        overtime_bands=CCNLOvertimeBands.of(
            ctx.contract.ccnl, ctx.contract.tctx.competence.year
        ),
    )
    return RunEvents(totals, items, entries)


def run_events(ctx: RunContext) -> RunEvents:
    """Post the variable events and the extra-month settlements of the run.

    Unpaid absences that deduct more than the pay of the run are rejected
    before the settlements are merged.

    Returns:
        The event totals with the settled bases added, and the items and
        entries of events and settlements.
    """
    events = _variable_events(ctx)
    settlement = settle_extra_months(
        ctx.request.extra_month_settlements,
        ctx.chain,
        ctx.cp,
        ctx.contract.tctx.payment,
        ctx.run_id,
        ctx.resolver,
        ctx.policy_context,
    )
    check_absences_within_pay(events.entries, ctx.monthly_gross)
    return RunEvents(
        settlement.added_to(events.totals),
        events.items + settlement.items,
        events.entries + settlement.entries,
    )


def _amounts_input(
    ctx: RunContext,
    totals: _EventTotals,
    surtax_rules: SurtaxRules | None,
    family_rules: FamilyDeductionRules | None,
    *,
    ivs_ceiling_applies: bool,
) -> _AmountsInput:
    request, contract = ctx.request, ctx.contract
    fiscal_year = ctx.fiscal_year
    return _AmountsInput(
        monthly_gross=ctx.monthly_gross,
        event_inps_base=totals.inps_base,
        event_tfr_base=totals.tfr_base,
        event_irpef_base=totals.irpef_base,
        event_substitute_base=totals.substitute_base,
        opening=ctx.opening.cash,
        withholding_schedule=ctx.withholding_schedule,
        upcoming_gross=ctx.upcoming_gross,
        rules=contract.year_rules,
        contract_type=request.contract_type,
        category=ctx.worker_category,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=family_rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
        pdr_rules=ctx.var_pay_rules.pdr,
        weekly_hours=_int_value(request.weekly_hours),
        contributable_hours=(
            request.contributable_hours.value
            if request.contributable_hours is not None
            else None
        ),
        domestic_hourly_rate=_domestic_hourly_rate(
            contract.ccnl,
            contract.year_rules,
            ctx.monthly_gross,
            contract.tctx.competence,
        ),
        eligible_work_days=_eligible_work_days(ctx),
        recovery_plan=ctx.opening.cash.obligations.recovery_of(
            fiscal_year, TRATTAMENTO_RECOVERY
        ),
        ulteriore_plan=ctx.opening.cash.obligations.recovery_of(
            fiscal_year, ULTERIORE_RECOVERY
        ),
        installment_run=ctx.installment_run,
        withholding_agent=ctx.withholding_agent,
        pension=pension_terms(ctx),
        conguaglio=ctx.conguaglio,
        surtax_obligations=ctx.opening.cash.obligations.surtax,
        run_month=request.period_id.month,
        regular_run=ctx.run_kind is RunKind.REGULAR,
        foreign_taxes=request.prior_year.foreign_taxes,
        deferred_irpef=_deferred_irpef(ctx),
    )


def _eligible_work_days(ctx: RunContext) -> int:
    """Return the days of employment in the tax year of the run.

    Returns:
        The days of the employment period in the year, or the whole year
        when the period is not tracked.
    """
    period = ctx.request.employment_period
    return DAYS_IN_YEAR if period is None else period.days_in_year(ctx.fiscal_year)


def _deferred_irpef(ctx: RunContext) -> Decimal:
    """Return the IRPEF a conguaglio of the run's tax year deferred.

    Returns:
        Zero without a deferral of the tax year.
    """
    deferred = ctx.opening.cash.obligations.deferred_of(ctx.fiscal_year)
    return Decimal(0) if deferred is None else deferred.irpef


def run_amounts(ctx: RunContext, totals: _EventTotals) -> RunAmounts:
    """Compute contributions, taxable income, IRPEF and surtax of the run.

    The surtax and family deduction rules are loaded only when the employer
    is a withholding agent and the request declares a residence or a family
    composition.

    Returns:
        The amounts of the run and their computations.
    """
    request, fiscal_year = ctx.request, ctx.fiscal_year
    withholds = ctx.withholding_agent
    needs_surtax = withholds and (
        request.regione is not None or request.comune_belfiore is not None
    )
    surtax_rules = ctx.repo.load_surtax_rules(fiscal_year) if needs_surtax else None
    family_rules = (
        ctx.repo.load_family_deduction_rules(fiscal_year)
        if withholds and request.family_composition is not None
        else None
    )
    ivs = run_ivs_ceiling(ctx, totals.inps_base)
    computed = _compute_amounts(
        _amounts_input(
            ctx,
            totals,
            surtax_rules,
            family_rules,
            ivs_ceiling_applies=ivs is not None and ivs.applies,
        )
    )
    return RunAmounts(*computed, ivs_ceiling=ivs)


def run_decisions(
    ctx: RunContext, totals: _EventTotals, run: RunAmounts
) -> tuple[CalculationDecision, ...]:
    """Return the base stage, contract, event and tax decisions of the run.

    Returns:
        The base stage decisions, the extra-month ratei counted, the
        contract decisions, then those of the
        events and of the amounts, and last the caller-supplied values of
        the events.
    """
    request, contract = ctx.request, ctx.contract
    amounts = run.amounts
    year = contract.tctx.competence.year
    pension = pension_decision(contract.ccnl, amounts.pension, year)
    ivs = run.ivs_ceiling
    ivs_decision = () if ivs is None else (ivs_ceiling_decision(ctx, ivs),)
    return (
        base_stage_decisions(ctx, totals, run)
        + ivs_decision
        + accrual_decisions(ctx)
        + contract_decisions(
            contract.ccnl,
            contract.level,
            request.category,
            ctx.worker_category,
            seniority_decision(ctx, run_seniority(ctx)),
            contract.tctx.competence.year,
            ctx.apprenticeship,
        )
        + ((pension,) if pension is not None else ())
        + totals.decisions
        + amounts.decisions
        + caller_supplied_decisions(request.events, contract.ccnl)
    )
