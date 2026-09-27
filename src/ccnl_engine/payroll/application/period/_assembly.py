"""Assembly of a period result: totals, closing state, checks and report."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.application.period._capability_traces import (
    capability_report,
)
from ccnl_engine.payroll.application.period._checks import check_net_covered, run_facts
from ccnl_engine.payroll.application.period._closing_state import (
    RunOutcome,
    closing_state,
)
from ccnl_engine.payroll.application.period._rule_sources import (
    missing_source_issues,
    run_rule_sources,
    weakest_by_capability,
)
from ccnl_engine.payroll.application.reconcile import check_period
from ccnl_engine.payroll.application.withholding._cap import run_net
from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.service._contributions_rates import category_rate_issue

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._pipeline import (
        RunAmounts,
        RunEvents,
    )
    from ccnl_engine.payroll.application.period._posting import (
        RunCredits,
        RunPostings,
    )
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.period_state import PeriodState

_ZERO = Decimal(0)

#: Accounts added to the gross, net of unpaid absences, for the employer cost.
_EMPLOYER_COST_ACCOUNTS = (
    AccountKind.NON_CASH_BENEFITS,
    AccountKind.EMPLOYER_CONTRIBUTIONS,
    AccountKind.BILATERAL_FUND_EMPLOYER,
    AccountKind.TFR_ACCRUAL,
    AccountKind.PENSION_FUND_EMPLOYER,
    AccountKind.PENSION_FUND_TFR,
)


def _employer_cost(entries: tuple[LedgerEntry, ...]) -> Decimal:
    cost = _sum_ledger(entries, AccountKind.CASH_EARNINGS) - _sum_ledger(
        entries, AccountKind.EMPLOYEE_DEDUCTIONS
    )
    for account in _EMPLOYER_COST_ACCOUNTS:
        cost += _sum_ledger(entries, account)
    return cost


def _closing(
    ctx: RunContext,
    events: RunEvents,
    amounts: RunAmounts,
    recoveries: RunCredits,
    posted: RunPostings,
) -> PeriodState:
    return closing_state(
        ctx.opening,
        RunOutcome(
            tax_year=ctx.fiscal_year,
            withholding_slots=ctx.withholding_schedule.run_count.value,
            run_id=ctx.closed_run_id,
            run_kind=ctx.run_kind,
            entries=posted.entries,
            period_inps_base=ctx.monthly_gross + events.totals.inps_base,
            amounts=posted.amounts,
            events=events.totals,
            somma_esente=recoveries.somma,
            recovery_plan=amounts.recovery_plan,
            carried=recoveries.carried.remaining,
            shortfall=posted.capped.shortfall,
        ),
    )


def _benefits(events: RunEvents, entries: tuple[LedgerEntry, ...]) -> BenefitBreakdown:
    return BenefitBreakdown(
        value=_sum_ledger(entries, AccountKind.NON_CASH_BENEFITS),
        cash=_ZERO,
        irpef_base=events.totals.fringe_irpef,
        inps_base=events.totals.fringe_inps,
        employer_cost=_sum_ledger(entries, AccountKind.NON_CASH_BENEFITS),
    )


def _rule_issues(ctx: RunContext) -> tuple[CalculationIssue, ...]:
    issue = category_rate_issue(
        ctx.contract.year_rules, ctx.request.contract_type, ctx.worker_category
    )
    return () if issue is None else (issue,)


def _result(
    ctx: RunContext,
    events: RunEvents,
    amounts: RunAmounts,
    recoveries: RunCredits,
    posted: RunPostings,
    decisions: tuple[CalculationDecision, ...],
    bundle_version: str | None,
) -> PeriodResult:
    entries = posted.entries
    somma, carried, capped = recoveries.somma, recoveries.carried, posted.capped
    closing = _closing(ctx, events, amounts, recoveries, posted)
    all_decisions = decisions + somma.decisions + carried.decisions + capped.decisions
    executed = events.totals.executed_features
    sources = run_rule_sources(ctx, all_decisions, executed)
    return PeriodResult(
        period_id=ctx.request.period_id,
        payment_date=ctx.request.payment_date,
        period_gross=_sum_ledger(entries, AccountKind.CASH_EARNINGS),
        period_net=run_net(entries),
        period_employer_cost=_employer_cost(entries),
        unpaid_absence_deduction=_sum_ledger(entries, AccountKind.EMPLOYEE_DEDUCTIONS),
        closing_state=closing,
        pay_items=posted.pay_items + events.items + somma.items + carried.items,
        ledger_entries=entries,
        capability_report=capability_report(
            ctx.contract.catalog,
            all_decisions,
            executed,
            ctx.fiscal_year,
            weakest_by_capability(sources),
        ),
        contribution_breakdown=amounts.contribution_breakdown,
        tax_computation=amounts.tax_computation,
        benefit_breakdown=_benefits(events, entries),
        run=ctx.request.run,
        bundle_version=bundle_version,
        issues=events.totals.issues
        + posted.amounts.surtax.issues
        + somma.issues
        + capped.issues
        + _rule_issues(ctx)
        + missing_source_issues(sources),
        decisions=all_decisions,
    )


def assemble_result(
    ctx: RunContext,
    events: RunEvents,
    amounts: RunAmounts,
    recoveries: RunCredits,
    posted: RunPostings,
    decisions: tuple[CalculationDecision, ...],
    bundle_version: str | None,
) -> PeriodResult:
    """Build the period result of the run and check it.

    Returns:
        The result, once its net covers its deductions and every
        reconciliation invariant holds.
    """
    result = _result(
        ctx, events, amounts, recoveries, posted, decisions, bundle_version
    )
    check_net_covered(result)
    facts = run_facts(
        ctx.request,
        ctx.contract.year_rules,
        ivs_ceiling_applies=ctx.ivs_ceiling_applies,
        pdr_cap=ctx.var_pay_rules.pdr.max_amount,
        accrual=ctx.accrual,
        projected_taxable=posted.amounts.projected_taxable,
        withholding_agent=ctx.withholding_agent,
    )
    check_period(result, ctx.opening, facts)
    return result
