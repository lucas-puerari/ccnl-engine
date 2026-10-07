"""Assembly of a period result: totals, closing state, checks and report."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.application.period._accrual_decisions import run_accruals
from ccnl_engine.payroll.application.period._additional_ivs import (
    additional_ivs_issue,
)
from ccnl_engine.payroll.application.period._capability_registry import (
    capability_report,
    case_facts,
)
from ccnl_engine.payroll.application.period._checks import check_net_covered, run_facts
from ccnl_engine.payroll.application.period._closing_state import (
    RunOutcome,
    closing_state,
)
from ccnl_engine.payroll.application.period._limitations import run_limitations
from ccnl_engine.payroll.application.period._minimum_base import minimum_base_issue
from ccnl_engine.payroll.application.period._other_employers import (
    other_employers_issue,
)
from ccnl_engine.payroll.application.period._rule_sources import (
    missing_source_issues,
    run_rule_sources,
    weakest_by_capability,
)
from ccnl_engine.payroll.application.period._rulesets import run_rulesets
from ccnl_engine.payroll.application.period._seniority import run_seniority
from ccnl_engine.payroll.application.period._tfr_revaluation import (
    tfr_revaluation_issues,
)
from ccnl_engine.payroll.application.reconcile import check_period
from ccnl_engine.payroll.application.withholding._cap import run_net
from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.service._contributions_rates import category_rate_issue
from ccnl_engine.payroll.service.additional_ivs import (
    MONTHLY_COMPONENT,
    SETTLEMENT_COMPONENT,
)

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
#: Components of the additional 1% IVS the competence year accumulates.
_ADDITIONAL_IVS = frozenset({MONTHLY_COMPONENT, SETTLEMENT_COMPONENT})

#: Accounts added to the gross, net of unpaid absences, for the employer cost.
_EMPLOYER_COST_ACCOUNTS = (
    AccountKind.NON_CASH_BENEFITS,
    AccountKind.EMPLOYER_CONTRIBUTIONS,
    AccountKind.BILATERAL_FUND_EMPLOYER,
    AccountKind.TFR_ACCRUAL,
    AccountKind.PENSION_FUND_EMPLOYER,
    AccountKind.PENSION_FUND_TFR,
    AccountKind.TFR_TREASURY_FUND,
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
            conguaglio=ctx.takes_last_slot,
            payment=ctx.payment,
            entries=posted.entries,
            period_inps_base=amounts.inps_base(
                ctx.monthly_gross + events.totals.inps_base
            ),
            amounts=posted.amounts,
            events=events.totals,
            somma_esente=recoveries.somma,
            recovery_plan=amounts.recovery_plan,
            carried=recoveries.carried.remaining,
            shortfall=posted.capped.shortfall,
            deferred=posted.deferred.remaining,
            additional_ivs=sum(
                (
                    c.amount
                    for c in amounts.contribution_breakdown.components
                    if c.name in _ADDITIONAL_IVS
                ),
                _ZERO,
            ),
            history_known=_chainable(ctx),
            employment_spells=ctx.employment_spells,
        ),
    )


def _chainable(ctx: RunContext) -> bool:
    """Return whether a later run can open with the closing state of the run.

    It cannot when the run opened without the history of the employment,
    or when it is the conguaglio of a withholding agent and the request
    omits the residence: the surtax of the tax year is then undetermined,
    so the conguaglio withholds no saldo, opens no installment and no
    municipal acconto for the next year (D.Lgs. 446/1997 art. 50 c. 4,
    D.Lgs. 360/1998 art. 1 cc. 4-5) and drops the acconto the year carried,
    which the saldo would absorb.

    Returns:
        ``False`` when the closing state misses part of the history.
    """
    request = ctx.request
    residence_unknown = request.regione is None or request.comune_belfiore is None
    surtax_undetermined = ctx.conguaglio and ctx.withholding_agent and residence_unknown
    return ctx.opening_issue is None and not surtax_undetermined


def _benefits(events: RunEvents, entries: tuple[LedgerEntry, ...]) -> BenefitBreakdown:
    return BenefitBreakdown(
        value=_sum_ledger(entries, AccountKind.NON_CASH_BENEFITS),
        cash=_ZERO,
        irpef_base=events.totals.fringe_irpef,
        inps_base=events.totals.fringe_inps,
        employer_cost=_sum_ledger(entries, AccountKind.NON_CASH_BENEFITS),
    )


def _input_issues(
    ctx: RunContext, events: RunEvents, amounts: RunAmounts
) -> tuple[CalculationIssue, ...]:
    """Return the issues of the facts and rules the run read.

    Returns:
        The issues of the category rates, the seniority, the proration, the
        minimum INPS base, the IVS massimale, the additional 1% IVS, the
        opening state, the INPS base of other employments and the TFR
        revaluation, in that order,
        each only when raised.
    """
    ivs = amounts.ivs_ceiling
    base = amounts.inps_base(ctx.monthly_gross + events.totals.inps_base)
    issues = (
        category_rate_issue(
            ctx.contract.year_rules, ctx.request.contract_type, ctx.worker_category
        ),
        run_seniority(ctx).issue(),
        ctx.proration.issue(),
        minimum_base_issue(amounts.minimum_base),
        None if ivs is None else ivs.issue(),
        additional_ivs_issue(ctx),
        ctx.opening_issue,
        other_employers_issue(ctx, base),
    )
    raised = tuple(issue for issue in issues if issue is not None)
    return raised + tfr_revaluation_issues(ctx)


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
    all_decisions = (
        decisions
        + somma.decisions
        + carried.decisions
        + capped.decisions
        + posted.deferred.decisions
    )
    executed = events.totals.executed_features
    sources = run_rule_sources(ctx, all_decisions, executed)
    report = capability_report(
        ctx.contract.catalog,
        all_decisions,
        executed,
        case_facts(ctx),
        ctx.fiscal_year,
        weakest_by_capability(sources),
    )
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
        capability_report=report,
        contribution_breakdown=amounts.contribution_breakdown,
        tax_computation=amounts.tax_computation,
        benefit_breakdown=_benefits(events, entries),
        run=ctx.request.run,
        bundle_version=bundle_version,
        issues=events.totals.issues
        + posted.amounts.surtax.issues
        + posted.amounts.issues
        + somma.issues
        + capped.issues
        + posted.deferred.issues
        + _input_issues(ctx, events, amounts)
        + missing_source_issues(sources),
        decisions=all_decisions,
        rulesets=run_rulesets(ctx, sources),
        limitations=run_limitations(ctx, report, events.totals.limitations),
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
        ivs_ceiling_applies=(
            amounts.ivs_ceiling is not None and amounts.ivs_ceiling.applies
        ),
        pdr_cap=ctx.var_pay_rules.pdr.max_amount,
        accruals=run_accruals(ctx),
        projected_taxable=posted.amounts.projected_taxable,
        withholding_agent=ctx.withholding_agent,
    )
    check_period(result, ctx.opening, facts)
    return result
