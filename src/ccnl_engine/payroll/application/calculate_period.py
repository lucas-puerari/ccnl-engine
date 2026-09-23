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

_POLICY_RESOLVER: PolicyResolver | None = None

_OBSERVED: dict[str, str] = {
    "base_salary": "computed",
    "seniority": "computed",
    "inps_employee": "computed",
    "inps_employer": "computed",
    "tfr": "computed",
    "irpef": "computed",
    "trattamento_integrativo": "computed",
    "ulteriore_detrazione_lavoro": "computed",
    "addizionale_regionale": "computed",
    "addizionale_comunale": "computed",
    "family_deductions": "computed",
    "overtime": "computed",
    "night_work": "computed",
    "holiday_work": "computed",
    "absence": "computed",
    "leave": "computed",
    "sickness": "computed",
    "fringe_benefit": "computed",
    "welfare": "computed",
    "bonus_pdr": "computed",
    "contract_renewal_arrears": "computed",
    "bilateral_funds": "computed",
    "termination_tfr": "computed",
}


def _get_resolver() -> PolicyResolver:
    global _POLICY_RESOLVER  # noqa: PLW0603
    if _POLICY_RESOLVER is None:
        _POLICY_RESOLVER = PolicyResolver.load()
    return _POLICY_RESOLVER


def calculate_period(
    request: PeriodCalculationRequest,
    *,
    repo: KnowledgeRepository | None = None,
) -> PeriodCalculationResult:
    """Compute payroll for one competence period using the period-first model.

    Args:
        request: Period calculation input: CCNL, level, period, YTD state and
            optional variable events.
        repo: Optional knowledge repository. Uses
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` when ``None``.

    Returns:
        A :class:`~ccnl_engine.payroll.domain.period.PeriodCalculationResult`
        with gross, net, employer cost, closing YTD state, pay items and ledger.

    Raises:
        DataIntegrityError: When the ledger reconciliation invariants fail after
            computation, indicating an internal accounting consistency error.
    """
    effective_repo = repo if repo is not None else BundledKnowledgeRepository()
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
    capability_gaps = catalog.gaps(_OBSERVED, detect_absent=True, year=period_year)
    capability_report = CapabilityReport(catalog_year=period_year, gaps=capability_gaps)
    additional_months = int(ccnl.parameters.additional_months.value_at(as_of))
    chain = _resolve_chain(ccnl, level, request.contract_type, as_of)
    run_kind = request.run.run_kind if request.run is not None else "regular"
    chain = _apply_extra_month_policy(
        chain, run_kind, request.opening_state.months_closed
    )
    monthly_gross = money(chain.base + chain.seniority + chain.allowances_total)

    var_pay_rules = load_variable_pay_rules(period_year)
    if request.has_dependent_children:
        fringe_threshold = var_pay_rules.fringe_benefit.threshold_with_children
    else:
        fringe_threshold = var_pay_rules.fringe_benefit.threshold_standard

    resolver = _get_resolver()
    policy_context = PolicyContext(year=period_year, as_of=as_of)
    cp = CompetencePeriod(year=request.period_id.year, month=request.period_id.month)
    tag = (
        request.run.run_id
        if request.run is not None
        else f"{period_year}_{request.period_id.month:02d}"
    )
    event_totals, event_items, event_entries = _process_events(
        request.events,
        cp,
        request.payment_date,
        tag,
        date_ctx,
        resolver,
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
        ivs_ceiling_applies=request.ivs_ceiling_applies,
        pdr_rules=var_pay_rules.pdr,
        weekly_hours=request.weekly_hours,
        contributable_hours=request.contributable_hours,
        domestic_hourly_rate=domestic_hr,
    )
    pay_items = _build_pay_items(
        amounts, chain, request.period_id, request.payment_date, run_tag=tag
    )
    ledger_entries = _project_ledger(
        amounts,
        chain,
        request.period_id,
        request.payment_date,
        resolver,
        policy_context,
        run_tag=tag,
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
            resolver, "tax_credit_item", policy_context
        ).policy_id
        se_item_id = f"somma_esente_{tag}"
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
    period_employer_cost = (
        period_gross
        + _sum_ledger(all_entries, AccountKind.NON_CASH_BENEFITS)
        + _sum_ledger(all_entries, AccountKind.EMPLOYER_CONTRIBUTIONS)
        + _sum_ledger(all_entries, AccountKind.BILATERAL_FUND_EMPLOYER)
        + _sum_ledger(all_entries, AccountKind.TFR_ACCRUAL)
    )

    period_inps_base = monthly_gross + event_totals.inps_base
    closing = PeriodState(
        months_closed=request.opening_state.months_closed + 1,
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
        pdr_ytd=request.opening_state.pdr_ytd + event_totals.substitute_base,
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
        closing_state=closing,
        pay_items=pay_items + event_items + se_items,
        ledger_entries=all_entries,
        capability_report=capability_report,
        contribution_breakdown=contribution_breakdown,
        tax_computation=tax_computation,
        benefit_breakdown=benefit_breakdown,
        run=request.run,
    )
    rec = _reconcile(result, request.opening_state)
    if not rec.ok:
        msgs = "; ".join(f"[{v.invariant_id}] {v.message}" for v in rec.violations)
        msg = f"Period reconciliation failed: {msgs}"
        raise DataIntegrityError(msg)
    return result
