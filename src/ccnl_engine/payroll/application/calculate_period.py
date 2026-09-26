"""Period-first payroll calculation: single competence month.

Computation order: (1) variable events → aggregated totals, (2) gross from
CCNL salary table, (3) INPS contributions and TFR accrual, (4) IRPEF via
conguaglio YTD, (5) pay items and ledger entries, (6) advance YTD state.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_family_deduction_rules,
    load_variable_pay_rules,
)
from ccnl_engine.payroll.application._capability_traces import capability_report
from ccnl_engine.payroll.application._extra_month_accrual import (
    run_fraction,
    settle_extra_months,
)
from ccnl_engine.payroll.application._period_amounts import (
    _compute_amounts,
    _domestic_hourly_rate,
    _resolve_chain,
)
from ccnl_engine.payroll.application._period_utils import (
    _apply_extra_month_policy,
    _effective_resolver,
    _int_value,
    _sum_ledger,
)
from ccnl_engine.payroll.application._run_decisions import contract_decisions
from ccnl_engine.payroll.application._withholding_plan import (
    resolve_withholding_schedule,
    somma_esente_credit,
    upcoming_recurring_gross,
)
from ccnl_engine.payroll.application.allocate_events import _process_events
from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
    _project_ledger,
)
from ccnl_engine.payroll.application.reconcile import reconcile as _reconcile
from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employment_context import (
    EffectiveDateContext,
    TemporalContext,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    SommaEsenteAccount,
    TaxYtd,
    TrattamentoAccount,
)
from ccnl_engine.payroll.service.category import resolve_worker_category
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository

_ZERO = Decimal(0)


def _resolve_run_id(request: PeriodCalculationRequest) -> str:
    """Return the run identifier and raise if the run was already processed.

    Returns:
        The run identifier string for this period.

    Raises:
        ValueError: When the run was already closed in the opening state.
    """
    run_id = (
        request.run.run_id
        if request.run is not None
        else f"{request.period_id.year}_{request.period_id.month:02d}"
    )
    if run_id in request.opening_state.closed_run_ids:
        msg = f"Run '{run_id}' was already processed in this payroll year"
        raise ValueError(msg)
    return run_id


def calculate_period(
    request: PeriodCalculationRequest,
    *,
    repo: KnowledgeRepository | None = None,
    resolver: PolicyResolver | None = None,
    bundle_version: str | None = None,
) -> PeriodCalculationResult:
    """Compute payroll for one competence period using the period-first model.

    Args:
        request: Period calculation input: CCNL, level, period, YTD state and
            optional variable events.
        repo: Optional knowledge repository. Uses
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` when ``None``.
        resolver: Optional pre-loaded :class:`~ccnl_engine.payroll.domain.policy\
.PolicyResolver`.  When ``None``, the bundled Italian ruleset is loaded on every
            call.  Pass a cached instance (e.g. from :attr:`PayrollEngine._resolver`)
            to avoid repeated JSON parsing.
        bundle_version: Knowledge-bundle version string to embed in the result.
            ``None`` when called outside a :class:`PayrollEngine` context.

    Returns:
        A :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`
        with gross, net, employer cost, closing YTD state, pay items and ledger.

    Raises:
        DataIntegrityError: When the ledger reconciliation invariants fail after
            computation, indicating an internal accounting consistency error.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
    effective_resolver = _effective_resolver(resolver)
    ccnl = effective_repo.load_ccnl(request.ccnl_slug)
    tctx = TemporalContext.from_period(
        request.period_id.year, request.period_id.month, request.payment_date
    )
    level = ccnl.level_by_code(request.level_code)
    date_ctx = EffectiveDateContext.from_period(
        request.period_id.year, request.period_id.month, tctx.payment
    )
    year_rules = effective_repo.load_year_rules(
        tctx.fiscal_year, ccnl.meta.tax_sector, request.employer.headcount.value
    )
    catalog = effective_repo.load_capability_catalog(tctx.fiscal_year)
    withholding_schedule = resolve_withholding_schedule(
        request.withholding_schedule, ccnl, tctx.competence, tctx.fiscal_year
    )
    worker_category = resolve_worker_category(
        ccnl, level, request.category, seniority=request.seniority_months
    )
    chain = _resolve_chain(
        ccnl,
        level,
        request.contract_type,
        tctx.competence,
        seniority_months=_int_value(request.seniority_months),
        roles=request.roles,
        worker_category=worker_category,
        weekly_hours=_int_value(request.weekly_hours),
        full_time_weekly_hours=_int_value(request.full_time_weekly_hours),
    )
    run_kind = request.run.run_kind if request.run is not None else RunKind.REGULAR
    run_id = _resolve_run_id(request)
    slots_closed = request.opening_state.tax_withholding_periods_closed
    upcoming_gross = upcoming_recurring_gross(chain, withholding_schedule, slots_closed)
    chain = _apply_extra_month_policy(
        chain, run_kind, run_fraction(request, ccnl, tctx.competence)
    )
    monthly_gross = money(chain.base + chain.seniority + chain.allowances_total)

    var_pay_rules = load_variable_pay_rules(tctx.fiscal_year)
    fringe_threshold = (
        var_pay_rules.fringe_benefit.threshold_with_children
        if request.has_dependent_children
        else var_pay_rules.fringe_benefit.threshold_standard
    )

    ivs_ceiling_applies = request.ceiling_status in {
        ContributionCeilingStatus.POST_1995,
        ContributionCeilingStatus.OPTED_IN,
    }
    policy_context = PolicyContext(
        year=tctx.fiscal_year,
        as_of=tctx.competence,
        ccnl_slug=request.ccnl_slug,
        sector=ccnl.meta.tax_sector,
        gross_ytd=request.opening_state.earnings.gross,
    )
    cp = CompetencePeriod(year=request.period_id.year, month=request.period_id.month)
    event_totals, event_items, event_entries = _process_events(
        request.events,
        cp,
        tctx.payment,
        run_id,
        date_ctx,
        effective_resolver,
        policy_context,
        fringe_threshold=fringe_threshold,
        opening_fringe_ytd=request.opening_state.fringe.value,
        opening_fringe_taxed=request.opening_state.fringe.taxed,
        pdr_income_ceiling=var_pay_rules.pdr.income_ceiling,
        rinnovo_regime=var_pay_rules.rinnovo,
        work_time_regime=var_pay_rules.notte_festivi_turni,
        opening_work_time_cap=request.opening_state.work_time_regime,
    )
    settlement = settle_extra_months(
        request.extra_month_settlements,
        chain,
        cp,
        tctx.payment,
        run_id,
        effective_resolver,
        policy_context,
    )
    event_totals = settlement.added_to(event_totals)
    event_items += settlement.items
    event_entries += settlement.entries

    needs_surtax = request.regione is not None or request.comune_belfiore is not None
    surtax_rules = (
        effective_repo.load_surtax_rules(tctx.fiscal_year) if needs_surtax else None
    )
    fam_ded_rules = (
        load_family_deduction_rules(tctx.fiscal_year)
        if request.family_composition is not None
        else None
    )
    domestic_hr = _domestic_hourly_rate(
        ccnl, year_rules, monthly_gross, tctx.competence
    )
    computed = _compute_amounts(
        monthly_gross,
        event_totals.inps_base,
        event_totals.tfr_base,
        event_totals.irpef_base,
        event_totals.substitute_base,
        request.opening_state,
        withholding_schedule,
        upcoming_gross,
        year_rules,
        request.contract_type,
        worker_category,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=fam_ded_rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
        pdr_rules=var_pay_rules.pdr,
        weekly_hours=_int_value(request.weekly_hours),
        contributable_hours=(
            request.contributable_hours.value
            if request.contributable_hours is not None
            else None
        ),
        domestic_hourly_rate=domestic_hr,
        eligible_work_days=(
            request.employment_period.days_in_year(tctx.fiscal_year)
            if request.employment_period is not None
            else DAYS_IN_YEAR
        ),
    )
    amounts, contribution_breakdown, tax_computation, next_recovery_plan = computed
    decisions = (
        contract_decisions(
            ccnl,
            level,
            request.category,
            worker_category,
            request.seniority_months,
            chain.seniority,
            tctx.competence.year,
        )
        + event_totals.decisions
        + amounts.decisions
    )
    pay_items = _build_pay_items(
        amounts, chain, request.period_id, request.payment_date, run_tag=run_id
    )
    ledger_entries = _project_ledger(
        amounts,
        chain,
        request.period_id,
        request.payment_date,
        effective_resolver,
        policy_context,
        run_tag=run_id,
    )

    # Somma esente (L. 207/2024): this run's share of the projected annual amount
    period_somma_esente, se_items, se_entries = somma_esente_credit(
        tax_computation,
        withholding_schedule,
        effective_resolver,
        policy_context,
        cp,
        request.payment_date,
        run_id,
    )

    all_entries = ledger_entries + event_entries + se_entries

    period_gross = _sum_ledger(all_entries, AccountKind.CASH_EARNINGS)
    period_net = (
        period_gross
        + _sum_ledger(all_entries, AccountKind.TFR_SETTLEMENT)
        + _sum_ledger(all_entries, AccountKind.CREDITS)
        - _sum_ledger(all_entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        - _sum_ledger(all_entries, AccountKind.BILATERAL_FUND_EMPLOYEE)
        - _sum_ledger(all_entries, AccountKind.EMPLOYEE_DEDUCTIONS)
        - _sum_ledger(all_entries, AccountKind.SUBSTITUTE_TAX)
        - _sum_ledger(all_entries, AccountKind.ORDINARY_TAX)
        - _sum_ledger(all_entries, AccountKind.SURTAX)
        - _sum_ledger(all_entries, AccountKind.SEPARATE_TAX)
    )
    unpaid_absence_deduction = _sum_ledger(all_entries, AccountKind.EMPLOYEE_DEDUCTIONS)
    period_employer_cost = (
        period_gross
        - unpaid_absence_deduction
        + _sum_ledger(all_entries, AccountKind.NON_CASH_BENEFITS)
        + _sum_ledger(all_entries, AccountKind.EMPLOYER_CONTRIBUTIONS)
        + _sum_ledger(all_entries, AccountKind.BILATERAL_FUND_EMPLOYER)
        + _sum_ledger(all_entries, AccountKind.TFR_ACCRUAL)
    )

    period_inps_base = monthly_gross + event_totals.inps_base
    regular_delta = 1 if run_kind == "regular" else 0
    tax_delta = 1 if run_kind.consumes_withholding_slot else 0
    op = request.opening_state
    closing = PeriodState(
        tax_year=tctx.fiscal_year,
        regular_periods_closed=op.regular_periods_closed + regular_delta,
        tax_withholding_periods_closed=(op.tax_withholding_periods_closed + tax_delta),
        closed_run_ids=op.closed_run_ids | {run_id},
        earnings=EarningsYtd(
            gross=op.earnings.gross + period_gross,
            inps_base=op.earnings.inps_base + period_inps_base,
            taxable=op.earnings.taxable + amounts.period_taxable,
            inps_employee=(
                op.earnings.inps_employee
                + _sum_ledger(all_entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
            ),
        ),
        fringe=FringeYtd(
            value=op.fringe.value + event_totals.fringe_value,
            taxed=op.fringe.taxed + event_totals.fringe_irpef,
            pdr=op.fringe.pdr + amounts.pdr_eligible,
        ),
        tax=TaxYtd(
            irpef=op.tax.irpef + amounts.period_irpef,
            surtax=op.tax.surtax + amounts.period_surtax,
        ),
        trattamento=TrattamentoAccount(
            recognized=op.trattamento.recognized + max(_ZERO, amounts.period_tratt),
            recovered=op.trattamento.recovered + max(_ZERO, -amounts.period_tratt),
            plan=next_recovery_plan,
        ),
        somma_esente=SommaEsenteAccount(
            recognized=op.somma_esente.recognized + period_somma_esente,
        ),
        work_time_regime=RegimeCapAccount(
            used=op.work_time_regime.used + event_totals.work_time_cap_used
        ),
    )
    benefit_breakdown = BenefitBreakdown(
        value=_sum_ledger(all_entries, AccountKind.NON_CASH_BENEFITS),
        cash=_ZERO,
        irpef_base=event_totals.fringe_irpef,
        inps_base=event_totals.fringe_inps,
        employer_cost=_sum_ledger(all_entries, AccountKind.NON_CASH_BENEFITS),
    )
    result = PeriodCalculationResult(
        period_id=request.period_id,
        payment_date=request.payment_date,
        period_gross=period_gross,
        period_net=period_net,
        period_employer_cost=period_employer_cost,
        unpaid_absence_deduction=unpaid_absence_deduction,
        closing_state=closing,
        pay_items=pay_items + event_items + se_items,
        ledger_entries=all_entries,
        capability_report=capability_report(
            catalog, decisions, event_totals.executed_features, tctx.fiscal_year
        ),
        contribution_breakdown=contribution_breakdown,
        tax_computation=tax_computation,
        benefit_breakdown=benefit_breakdown,
        run=request.run,
        bundle_version=bundle_version,
        issues=event_totals.issues + amounts.surtax.issues,
        decisions=decisions,
    )
    rec = _reconcile(result, request.opening_state)
    if not rec.ok:
        msgs = "; ".join(f"[{v.invariant_id}] {v.message}" for v in rec.violations)
        msg = f"Period reconciliation failed: {msgs}"
        raise DataIntegrityError(msg)
    return result
