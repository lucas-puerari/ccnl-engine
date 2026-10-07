"""Steps of one run: events, amounts and decisions.

Each step reads the run context and the outputs of the steps before it;
the credits and the postings follow in :mod:`.period._posting`. The steps
only orchestrate: the inputs they gather come from :mod:`._pipeline_inputs`
and the formulas live in the collaborators they call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.amounts._compute import _compute_amounts
from ccnl_engine.payroll.application.period._accrual_decisions import accrual_decisions
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
from ccnl_engine.payroll.application.period._pension_decision import pension_decision
from ccnl_engine.payroll.application.period._pipeline_inputs import (
    amounts_input,
    variable_events,
)
from ccnl_engine.payroll.application.period._run_decisions import contract_decisions
from ccnl_engine.payroll.application.period._seniority import (
    run_seniority,
    seniority_decision,
)
from ccnl_engine.payroll.application.period._tfr_revaluation import (
    tfr_revaluation_decisions,
)
from ccnl_engine.payroll.application.year._extra_month_settlement import (
    settle_extra_months,
)

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


def run_events(ctx: RunContext) -> RunEvents:
    """Post the variable events and the extra-month settlements of the run.

    Unpaid absences that deduct more than the pay of the run are rejected
    before the settlements are merged.

    Returns:
        The event totals with the settled bases added, and the items and
        entries of events and settlements.
    """
    events = RunEvents(*variable_events(ctx))
    settlement = settle_extra_months(
        ctx.settlements,
        ctx.regular_chain,
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
        amounts_input(
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
        contract decisions, the pension fund and the TFR revaluation, then
        those of the
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
        + tfr_revaluation_decisions(ctx)
        + totals.decisions
        + amounts.decisions
        + caller_supplied_decisions(request.events, contract.ccnl)
    )
