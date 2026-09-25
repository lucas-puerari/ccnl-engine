"""Period-first payroll calculation: single competence month.

The computation order is:
  1. Process variable work events into aggregated totals.
  2. Resolve gross from the CCNL salary table for the period date.
  3. Compute INPS contributions and TFR accrual on the augmented bases.
  4. Project annual taxable income and compute IRPEF via conguaglio YTD.
  5. Build pay items and ledger entries from the resolved amounts.
  6. Advance the YTD state.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.capability_catalog import CapabilityReport
from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.tax.service.loaders import (
    load_family_deduction_rules,
    load_variable_pay_rules,
)
from ccnl_engine.payroll.application._period_amounts import (
    _apply_extra_month_policy,
    _as_of,
    _compute_amounts,
    _domestic_hourly_rate,
    _resolve_chain,
)
from ccnl_engine.payroll.application._period_utils import (
    _make_entry,
    _require_resolution,
    _sum_ledger,
)
from ccnl_engine.payroll.application.allocate_events import _process_events
from ccnl_engine.payroll.application.post_ledger import (
    _build_pay_items,
    _project_ledger,
)
from ccnl_engine.payroll.application.reconcile import reconcile as _reconcile
from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import (
    CompetencePeriod,
    PayItem,
    TaxCreditItem,
)
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository

_ZERO = Decimal(0)

_ALWAYS_COMPUTED: frozenset[str] = frozenset({
    "base_salary",
    "seniority",
    "inps_employee",
    "inps_employer",
    "tfr",
    "irpef",
    "trattamento_integrativo",
    "ulteriore_detrazione_lavoro",
    "overtime",
    "night_work",
    "holiday_work",
    "absence",
    "leave",
    "sickness",
    "fringe_benefit",
    "welfare",
    "bonus_pdr",
    "contract_renewal_arrears",
    "bilateral_funds",
    "termination_tfr",
})


def _build_observed(request: PeriodCalculationRequest) -> dict[str, str]:
    """Return the capability observation map for this request.

    Axes whose resolution depends on caller-supplied data are reported as
    ``"not_computed"`` when the required input is absent, so the capability
    catalog can distinguish genuinely skipped features from missing coverage.

    Returns:
        Mapping of feature name to its observed computation status.
    """
    obs: dict[str, str] = dict.fromkeys(_ALWAYS_COMPUTED, "computed")
    obs["addizionale_regionale"] = (
        "computed" if request.regione is not None else "not_computed"
    )
    obs["addizionale_comunale"] = (
        "computed" if request.comune_belfiore is not None else "not_computed"
    )
    obs["family_deductions"] = (
        "computed" if request.family_composition is not None else "not_computed"
    )
    return obs


def _resolve_run_id(request: PeriodCalculationRequest, period_year: int) -> str:
    """Return the run identifier and raise if the run was already processed.

    Returns:
        The run identifier string for this period.

    Raises:
        ValueError: When the run was already closed in the opening state.
    """
    run_id = (
        request.run.run_id
        if request.run is not None
        else f"{period_year}_{request.period_id.month:02d}"
    )
    if run_id in request.opening_state.closed_run_ids:
        msg = f"Run '{run_id}' was already processed in this payroll year"
        raise ValueError(msg)
    return run_id


def _effective_resolver(resolver: PolicyResolver | None) -> PolicyResolver:
    return resolver if resolver is not None else PolicyResolver.load()


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
    as_of = _as_of(request.period_id)
    level = ccnl.level_by_code(request.level_code)
    date_ctx = EffectiveDateContext.from_period(
        request.period_id.year, request.period_id.month, request.payment_date
    )
    period_year = request.period_id.year
    year_rules = effective_repo.load_year_rules(
        period_year, ccnl.meta.tax_sector, request.num_employees
    )
    catalog = effective_repo.load_capability_catalog(period_year)
    capability_gaps = catalog.gaps(
        _build_observed(request), detect_absent=True, year=period_year
    )
    capability_report = CapabilityReport(catalog_year=period_year, gaps=capability_gaps)
    additional_months = int(ccnl.parameters.additional_months.value_at(as_of))
    chain = _resolve_chain(ccnl, level, request.contract_type, as_of)
    run_kind = request.run.run_kind if request.run is not None else "regular"
    run_id = _resolve_run_id(request, period_year)
    chain = _apply_extra_month_policy(
        chain, run_kind, request.opening_state.regular_periods_closed
    )
    monthly_gross = money(chain.base + chain.seniority + chain.allowances_total)

    var_pay_rules = load_variable_pay_rules(period_year)
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
        year=period_year,
        as_of=as_of,
        ccnl_slug=request.ccnl_slug,
        sector=ccnl.meta.tax_sector,
        gross_ytd=request.opening_state.gross_ytd,
        num_employees=request.num_employees,
    )
    cp = CompetencePeriod(year=request.period_id.year, month=request.period_id.month)
    event_totals, event_items, event_entries = _process_events(
        request.events,
        cp,
        request.payment_date,
        run_id,
        date_ctx,
        effective_resolver,
        policy_context,
        fringe_threshold=fringe_threshold,
        opening_fringe_ytd=request.opening_state.fringe_ytd,
        opening_fringe_taxed=request.opening_state.fringe_taxed_ytd,
    )

    needs_surtax = request.regione is not None or request.comune_belfiore is not None
    surtax_rules = (
        effective_repo.load_surtax_rules(period_year) if needs_surtax else None
    )
    fam_ded_rules = (
        load_family_deduction_rules(period_year)
        if request.family_composition is not None
        else None
    )
    domestic_hr = _domestic_hourly_rate(ccnl, year_rules, monthly_gross, as_of)
    amounts, contribution_breakdown, tax_computation = _compute_amounts(
        monthly_gross,
        event_totals.inps_base,
        event_totals.tfr_base,
        event_totals.irpef_base,
        event_totals.substitute_base,
        request.opening_state,
        additional_months,
        year_rules,
        request.contract_type,
        level.category,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=fam_ded_rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
        pdr_rules=var_pay_rules.pdr,
        weekly_hours=request.weekly_hours,
        contributable_hours=request.contributable_hours,
        domestic_hourly_rate=domestic_hr,
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

    # Somma esente (L. 207/2024): extract annual amount, prorate to period
    annual_somma_esente = next(
        (c.amount for c in tax_computation.components if c.name == "somma_esente"),
        _ZERO,
    )
    period_somma_esente = (
        money(annual_somma_esente / additional_months)
        if annual_somma_esente > _ZERO
        else _ZERO
    )
    se_items: tuple[PayItem, ...] = ()
    se_entries: tuple[LedgerEntry, ...] = ()
    if period_somma_esente > _ZERO:
        credit_pid = _require_resolution(
            effective_resolver, "tax_credit_item", policy_context
        ).policy_id
        se_item_id = f"somma_esente_{run_id}"
        se_items = (
            TaxCreditItem(
                item_id=se_item_id,
                competence_period=cp,
                payment_date=request.payment_date,
                quantity=Decimal(1),
                amount=period_somma_esente,
            ),
        )
        se_entries = (
            _make_entry(
                se_item_id,
                se_item_id,
                "tax_credit_item",
                cp,
                request.payment_date,
                AccountKind.CREDITS,
                period_somma_esente,
                policy_id=credit_pid,
            ),
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
    tax_delta = 0 if run_kind == "adjustment" else 1
    closing = PeriodState(
        regular_periods_closed=(
            request.opening_state.regular_periods_closed + regular_delta
        ),
        tax_withholding_periods_closed=(
            request.opening_state.tax_withholding_periods_closed + tax_delta
        ),
        closed_run_ids=request.opening_state.closed_run_ids | {run_id},
        irpef_withheld_ytd=(
            request.opening_state.irpef_withheld_ytd + amounts.period_irpef
        ),
        inps_employee_ytd=(
            request.opening_state.inps_employee_ytd
            + _sum_ledger(all_entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        ),
        gross_ytd=request.opening_state.gross_ytd + period_gross,
        inps_base_ytd=request.opening_state.inps_base_ytd + period_inps_base,
        taxable_ytd=request.opening_state.taxable_ytd + amounts.period_taxable,
        fringe_ytd=(request.opening_state.fringe_ytd + event_totals.fringe_value),
        fringe_taxed_ytd=(
            request.opening_state.fringe_taxed_ytd + event_totals.fringe_irpef
        ),
        pdr_ytd=request.opening_state.pdr_ytd + amounts.pdr_eligible,
        credit_recognized_ytd=(
            request.opening_state.credit_recognized_ytd
            + max(_ZERO, amounts.period_tratt)
        ),
        credit_recovered_ytd=(
            request.opening_state.credit_recovered_ytd
            + max(_ZERO, -amounts.period_tratt)
        ),
        surtax_ytd=(request.opening_state.surtax_ytd + amounts.period_surtax),
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
        capability_report=capability_report,
        contribution_breakdown=contribution_breakdown,
        tax_computation=tax_computation,
        benefit_breakdown=benefit_breakdown,
        run=request.run,
        bundle_version=bundle_version,
    )
    rec = _reconcile(result, request.opening_state)
    if not rec.ok:
        msgs = "; ".join(f"[{v.invariant_id}] {v.message}" for v in rec.violations)
        msg = f"Period reconciliation failed: {msgs}"
        raise DataIntegrityError(msg)
    return result
