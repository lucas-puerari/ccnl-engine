"""Steps of one run: events, amounts and decisions.

The credits, the withholding cap and the base posting follow in
:mod:`~ccnl_engine.payroll.application.period._posting`.  Each step reads
the :class:`~ccnl_engine.payroll.application.period._context.RunContext`
and the outputs of the steps before it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _int_value
from ccnl_engine.payroll.application.allocate_events import (
    _process_events,
    worker_facts_of,
)
from ccnl_engine.payroll.application.amounts._compute import _compute_amounts
from ccnl_engine.payroll.application.amounts._domestic import _domestic_hourly_rate
from ccnl_engine.payroll.application.amounts._types import _AmountsInput
from ccnl_engine.payroll.application.period._checks import check_absences_within_pay
from ccnl_engine.payroll.application.period._run_decisions import contract_decisions
from ccnl_engine.payroll.application.withholding._cap import ends_in_year
from ccnl_engine.payroll.application.year._extra_month_accrual import (
    settle_extra_months,
)
from ccnl_engine.payroll.domain.obligations import TRATTAMENTO_RECOVERY
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


def _variable_events(ctx: RunContext) -> RunEvents:
    request, opening = ctx.request, ctx.opening
    fringe_rules = ctx.var_pay_rules.fringe_benefit
    totals, items, entries = _process_events(
        request.events,
        ctx.cp,
        ctx.contract.tctx.payment,
        ctx.run_id,
        ctx.contract.date_ctx,
        ctx.resolver,
        ctx.policy_context,
        fringe_threshold=(
            fringe_rules.threshold_with_children
            if request.has_dependent_children
            else fringe_rules.threshold_standard
        ),
        opening_fringe_ytd=opening.ytd.fringe.value,
        opening_fringe_taxed=opening.ytd.fringe.taxed,
        pdr_income_ceiling=ctx.var_pay_rules.pdr.income_ceiling,
        rinnovo_regime=ctx.var_pay_rules.rinnovo,
        work_time_regime=ctx.var_pay_rules.notte_festivi_turni,
        opening_work_time_cap=opening.ytd.work_time_regime,
        worker_facts=worker_facts_of(request),
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
) -> _AmountsInput:
    request, contract = ctx.request, ctx.contract
    fiscal_year = ctx.fiscal_year
    return _AmountsInput(
        monthly_gross=ctx.monthly_gross,
        event_inps_base=totals.inps_base,
        event_tfr_base=totals.tfr_base,
        event_irpef_base=totals.irpef_base,
        event_substitute_base=totals.substitute_base,
        opening=ctx.opening.ytd,
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
        ivs_ceiling_applies=ctx.ivs_ceiling_applies,
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
        eligible_work_days=(
            request.employment_period.days_in_year(fiscal_year)
            if request.employment_period is not None
            else DAYS_IN_YEAR
        ),
        recovery_plan=ctx.opening.obligations.recovery_of(
            fiscal_year, TRATTAMENTO_RECOVERY
        ),
        later_payslips=not ends_in_year(request.employment_period, fiscal_year),
    )


def run_amounts(ctx: RunContext, totals: _EventTotals) -> RunAmounts:
    """Compute contributions, taxable income, IRPEF and surtax of the run.

    The surtax and family deduction rules are loaded only when the request
    declares a residence or a family composition.

    Returns:
        The amounts of the run and their computations.
    """
    request, fiscal_year = ctx.request, ctx.fiscal_year
    needs_surtax = request.regione is not None or request.comune_belfiore is not None
    surtax_rules = ctx.repo.load_surtax_rules(fiscal_year) if needs_surtax else None
    family_rules = (
        ctx.repo.load_family_deduction_rules(fiscal_year)
        if request.family_composition is not None
        else None
    )
    computed = _compute_amounts(_amounts_input(ctx, totals, surtax_rules, family_rules))
    return RunAmounts(*computed)


def run_decisions(
    ctx: RunContext, totals: _EventTotals, amounts: _PeriodAmounts
) -> tuple[CalculationDecision, ...]:
    """Return the contract, event and tax decisions of the run.

    Returns:
        The contract decisions, then those of the events and of the amounts.
    """
    request, contract = ctx.request, ctx.contract
    return (
        contract_decisions(
            contract.ccnl,
            contract.level,
            request.category,
            ctx.worker_category,
            request.seniority_months,
            ctx.chain.seniority,
            contract.tctx.competence.year,
        )
        + totals.decisions
        + amounts.decisions
    )
