"""Core payroll computation pipeline: compute() and scenario conversion helpers."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    Coverage,
    EmployerCost,
    PeriodPayroll,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    AnnualizedAssumption,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.assembly import (
    _collect_provenance,
    build_calculation,
)
from ccnl_engine.engine.payroll.service.coverage_evaluator import _ivs_ceiling_warning
from ccnl_engine.engine.payroll.service.fiscal import compute_fiscal
from ccnl_engine.engine.payroll.service.gross import compute_gross
from ccnl_engine.engine.payroll.service.ledger_builder import (
    post_arrears_termination_tfr,
    post_contributions_and_taxes,
    post_earnings,
    post_fiscal_summary,
    post_variable_pay,
)
from ccnl_engine.engine.payroll.service.reconciliation import ReconciliationService
from ccnl_engine.engine.payroll.service.result_assembler import (
    _build_contributions,
    _build_earnings,
    _build_taxes,
    _net_monthly,
)
from ccnl_engine.engine.payroll.service.scope import (
    build_scope,
    ccnl_notes_to_limitations,
    compute_confidence,
    compute_result_status,
)
from ccnl_engine.engine.payroll.service.work_rules import compute_work_rules

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.knowledge_repository import KnowledgeRepository
    from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.payroll.domain.employment import Employment
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules


_ZERO = Decimal(0)


def _resolve_tax_year(employment: Employment) -> int:
    """Return the tax year for rule loading.

    Uses the explicit override when set, otherwise falls back to the
    calendar year of the employment date.

    Returns:
        Integer year for ``load_year_rules`` and ``load_surtax_rules``.
    """
    if employment.tax_year is not None:
        return employment.tax_year
    return employment.as_of.year


def _scenario_period(scenario: _InternalScenario) -> PeriodPayrollInput | None:
    """Build a PeriodPayrollInput from scenario period events.

    Returns:
        A :class:`PeriodPayrollInput` from *scenario*, or ``None`` when no
        period events are set.
    """
    fields = (
        scenario.time_supplements,
        scenario.absence_days,
        scenario.leave_input,
        scenario.sick_input,
        scenario.fringe_benefit_input,
        scenario.welfare_input,
        scenario.bonus_input,
    )
    if all(f is None for f in fields):
        return None
    return PeriodPayrollInput(
        time_supplements=scenario.time_supplements,
        absence_days=scenario.absence_days,
        leave_input=scenario.leave_input,
        sick_input=scenario.sick_input,
        fringe_benefit_input=scenario.fringe_benefit_input,
        welfare_input=scenario.welfare_input,
        bonus_input=scenario.bonus_input,
    )


def _annual_to_scenario(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput | None = None,
) -> _InternalScenario:
    """Build an internal scenario from an AnnualEstimateInput.

    Merges the structural fields from *scenario* with the period-specific
    events from *period* (when supplied).

    Returns:
        A :class:`_InternalScenario` ready for :func:`compute`.
    """
    if period is not None:
        return _InternalScenario(
            employee=scenario.employee,
            employment=scenario.employment,
            family=scenario.family,
            art15_deductions=scenario.art15_deductions,
            bilateral_funds=scenario.bilateral_funds,
            tax_basis=(
                period.tax_period
                if period.tax_period is not None
                else AnnualizedAssumption()
            ),
            time_supplements=period.time_supplements,
            absence_days=period.absence_days,
            leave_input=period.leave_input,
            sick_input=period.sick_input,
            fringe_benefit_input=period.fringe_benefit_input,
            welfare_input=period.welfare_input,
            bonus_input=period.bonus_input,
            prior_period_irpef_withheld=period.prior_period_irpef_withheld,
            maternity_inps_indemnity_annual=period.maternity_inps_indemnity_annual,
            workplace_injury_inail_indemnity_annual=(
                period.workplace_injury_inail_indemnity_annual
            ),
            termination_residual_leave_payout_annual=(
                period.termination_residual_leave_payout_annual
            ),
            termination_tfr_liquidation_annual=(
                period.termination_tfr_liquidation_annual
            ),
            contract_renewal_arrears_annual=period.contract_renewal_arrears_annual,
            una_tantum_annual=period.una_tantum_annual,
            personal_withholdings_annual=period.personal_withholdings_annual,
            additional_irpef_base_annual=period.additional_irpef_base_annual,
            health_fund_employee_annual=period.health_fund_employee_annual,
            health_fund_employer_annual=period.health_fund_employer_annual,
            territorial_supplement_annual=period.territorial_supplement_annual,
            company_supplement_annual=period.company_supplement_annual,
        )
    return _InternalScenario(
        employee=scenario.employee,
        employment=scenario.employment,
        family=scenario.family,
        art15_deductions=scenario.art15_deductions,
        bilateral_funds=scenario.bilateral_funds,
    )


def _load_from_repo(
    scenario: _InternalScenario,
    year: int,
    repo: KnowledgeRepository | None,
) -> tuple[CCNL, YearRules, SurtaxRules | None]:
    effective = repo if repo is not None else BundledKnowledgeRepository()
    ccnl = effective.load_ccnl(scenario.employment.ccnl)
    rules = effective.load_year_rules(
        year, ccnl.meta.tax_sector, scenario.employment.employer.num_employees
    )
    j = scenario.employee.jurisdiction
    needs_surtax = j is not None and (
        j.regione is not None or j.comune_belfiore is not None
    )
    surtax = effective.load_surtax_rules(year) if needs_surtax else None
    return ccnl, rules, surtax


def compute(
    scenario: _InternalScenario,
    bundle: PayrollBundle | None = None,
    *,
    _period: PeriodPayrollInput | None = None,
    repo: KnowledgeRepository | None = None,
) -> Calculation:
    """Compute gross-to-net salary and employer cost for an internal scenario.

    Loads the CCNL, tax/INPS rules, and (when jurisdiction is set) surtax
    rules from the bundled knowledge base, then runs the full payroll
    computation chain.

    When *bundle* is provided the three ruleset objects it carries are used
    directly, skipping rule loading.  This guarantees reproducibility across
    multiple calls (e.g. monthly payroll for a full year) and avoids repeated
    I/O even when the individual loaders are not yet cached.

    Args:
        scenario: The internal payroll scenario built by :func:`_annual_to_scenario`.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``, rulesets
            are loaded (and cached) on demand.
        repo: Optional knowledge repository.  When ``None``,
            :class:`~ccnl_engine.engine.io.service.bundled_knowledge_repository\
.BundledKnowledgeRepository` is used.  Pass a custom implementation to
            inject test stubs or alternative data sources.

    Returns:
        :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with all gross, net and cost figures plus a serialisable input snapshot.
    """
    if _period is None:
        _period = _scenario_period(scenario)
    as_of = scenario.employment.as_of
    year = _resolve_tax_year(scenario.employment)
    if bundle is not None:
        ccnl = bundle.ccnl
        rules = bundle.rules
        surtax = bundle.surtax
    else:
        ccnl, rules, surtax = _load_from_repo(scenario, year, repo)

    gross = compute_gross(scenario, ccnl)
    ledger = Ledger()
    post_earnings(gross, as_of, ledger)
    work = compute_work_rules(scenario, ccnl, gross, year)
    fiscal = compute_fiscal(scenario, ccnl, rules, surtax, gross, year, work)
    post_contributions_and_taxes(fiscal, as_of, ledger)
    post_variable_pay(work, as_of, ledger)
    post_arrears_termination_tfr(fiscal, as_of, ledger)
    post_fiscal_summary(fiscal, as_of, ledger)
    ReconciliationService().check(ledger)
    calculation_scope = build_scope(scenario, fiscal, work, ccnl.coverage)
    provenance = _collect_provenance(
        gross.level,
        as_of,
        gross.chain,
        ccnl.parameters.seniority_increments,
        ccnl=ccnl,
        under_level_code=gross.under_level_code,
    )
    result_status = compute_result_status(calculation_scope)
    # Main rulesets (ccnl, tax rules) are always consumed; INPS rules are only
    # consumed for the standard percentage model, not the domestic forfait model.
    main_rulesets: tuple[RulesetIdentity | None, ...] = (ccnl.ruleset, rules.ruleset)
    if rules.domestic_contributions is None:
        main_rulesets = (*main_rulesets, rules.inps_ruleset)
    consumed_rulesets = (
        main_rulesets + tuple(work.consumed_ruleset_ids) + fiscal.consumed_ruleset_ids
    )
    ivs_ceiling = rules.inps.ceiling if rules.inps is not None else None
    ivs_warn = (
        None
        if rules.domestic_contributions is not None
        else _ivs_ceiling_warning(scenario, as_of, gross.contribution_base, ivs_ceiling)
    )
    result_warnings = (
        (*work.warnings, ivs_warn) if ivs_warn is not None else work.warnings
    )

    coverage = Coverage(
        status=result_status,
        confidence=compute_confidence(
            result_status, result_warnings, provenance, consumed_rulesets
        ),
        calculation_scope=calculation_scope,
        warnings=result_warnings,
        consumed_rulesets=consumed_rulesets,
        limitations=ccnl_notes_to_limitations(ccnl.coverage),
    )
    base: dict[str, object] = {
        "ccnl_id": ccnl.meta.ccnl_id,
        "level_code": scenario.employee.level_code,
        "employment_type": scenario.employment.contract.type,
        "part_time_ratio": scenario.employee.part_time_ratio,
        "as_of": as_of,
        "year": as_of.year,
        "contract_effective_date": (
            p.valid_from
            if (p := gross.level.base_salary.period_at(as_of)) is not None
            else as_of  # pragma: no cover
        ),
        "tax_rule_year": year,
        "earnings": _build_earnings(gross, work),
        "contributions": _build_contributions(fiscal),
        "taxes": _build_taxes(fiscal),
        "employer_cost": EmployerCost(
            employer_cost_annual=ledger.total(AccountKind.EMPLOYER_COST)
        ),
        "coverage": coverage,
        "provenance": provenance,
        "net_annual": ledger.total(AccountKind.NET_PAY),
        "net_monthly": _net_monthly(ledger, gross),
    }
    if _period is not None:
        result: AnnualEstimate = PeriodPayroll(
            **base,  # type: ignore[arg-type]
            pay_period=_period,
            base_monthly_full_time=work.base_monthly_full_time,
            overtime_supplement_monthly=work.overtime_supp,
            night_supplement_monthly=work.night_supp,
            holiday_supplement_monthly=work.holiday_supp,
            time_supplements_monthly=work.time_supplements_monthly,
            time_supplements_annual_projection=work.time_supplements_annual_projection,
            absence_deduction_monthly=work.absence_deduction_monthly,
            effective_gross_monthly=work.effective_gross_monthly,
            leave_accrued_days_monthly=work.leave_accrued_days_monthly,
            leave_taken_days_monthly=work.leave_taken_days_monthly,
            leave_balance_days=work.leave_balance_days,
            sick_days_monthly=work.sick_days_monthly,
            sick_carenza_days_monthly=work.sick_carenza_days_monthly,
            sick_inps_indemnity_monthly=work.sick_inps_indemnity_monthly,
            sick_company_integration_monthly=work.sick_company_integration_monthly,
            fringe_benefit_annual=work.fringe_benefit_annual,
            fringe_benefit_threshold_annual=work.fringe_benefit_threshold_annual,
            fringe_benefit_taxable_annual=work.fringe_benefit_taxable_annual,
            welfare_annual=work.welfare_annual,
            bonus_annual=work.bonus_annual,
            bonus_pdr_flat_tax_annual=work.bonus_pdr_flat_tax_annual,
            bonus_ordinary_taxable_annual=work.bonus_ordinary_taxable_annual,
        )
    else:
        result = AnnualEstimate(**base)  # type: ignore[arg-type]
    return build_calculation(
        scenario, ccnl, rules, surtax, gross, work, result, fiscal, ledger
    )
