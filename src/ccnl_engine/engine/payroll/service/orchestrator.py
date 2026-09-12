"""Coordinate gross, fiscal and optional computations into a payroll result."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.payroll.service.audit import (
    _collect_provenance,
    build_calculation,
)
from ccnl_engine.engine.payroll.service.fiscal import compute_fiscal
from ccnl_engine.engine.payroll.service.gross import compute_gross
from ccnl_engine.engine.payroll.service.scope import (
    _compute_confidence,
    _compute_result_status,
    build_scope,
)
from ccnl_engine.engine.payroll.service.work_rules import compute_work_rules
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.engine.tax.service.loaders import (
    load_year_rules,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.calculation import (
        Calculation,
    )
    from ccnl_engine.engine.payroll.domain.scenario import Employment, PayrollScenario


def _resolve_tax_year(employment: Employment) -> int:
    """Return the tax year for rule loading.

    Uses the explicit override when set, otherwise falls back to the
    calendar year of the employment date.

    Returns:
        The integer year to use for ``load_year_rules`` and
        ``load_surtax_rules``.
    """
    if employment.tax_year is not None:
        return employment.tax_year
    return employment.calculation_date.year


def compute(scenario: PayrollScenario) -> Calculation:
    """Compute gross-to-net salary and employer cost for a payroll scenario.

    Loads the CCNL, tax/INPS rules, and (when jurisdiction is set) surtax
    rules from the bundled knowledge base, then runs the full payroll
    computation chain.

    Args:
        scenario: The full payroll scenario — worker data and employment
            relationship — as a :class:`~ccnl_engine.engine.payroll.domain\
.scenario.PayrollScenario`.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        whose ``result`` is the :class:`PayrollResult` with all gross, net,
        and cost figures, together with the engine version, the ruleset
        identities used and a serialisable snapshot of the inputs.

    """
    # Load rulesets from the knowledge base
    ccnl = load_ccnl(scenario.employment.ccnl)
    as_of = scenario.employment.calculation_date
    year = _resolve_tax_year(scenario.employment)
    rules = load_year_rules(
        year, ccnl.meta.tax_sector, scenario.employment.employer.num_employees
    )
    j = scenario.employee.jurisdiction
    needs_surtax = j is not None and (
        j.regione is not None or j.comune_belfiore is not None
    )
    surtax = load_surtax_rules(year) if needs_surtax else None

    gross = compute_gross(scenario, ccnl)
    fiscal = compute_fiscal(scenario, ccnl, rules, surtax, gross, year)
    work = compute_work_rules(scenario, ccnl, gross, year)
    calculation_scope = build_scope(scenario, fiscal, work)
    # R11: pass ccnl and under_level_code so _collect_provenance can resolve
    # the effective pay level for under-classification apprentices instead of
    # always using the destination level.
    provenance = _collect_provenance(
        gross.level,
        as_of,
        gross.chain,
        ccnl.parameters.seniority_increments,
        ccnl=ccnl,
        under_level_code=gross.under_level_code,
    )
    result_status = _compute_result_status(calculation_scope)
    result_warnings = work.warnings

    result = PayrollResult(
        ccnl_id=ccnl.meta.ccnl_id,
        level_code=scenario.employee.level_code,
        employment_type=scenario.employment.contract.type,
        part_time_pct=scenario.employee.part_time_pct,
        as_of=as_of,
        year=as_of.year,
        seniority_count=gross.count,
        base_monthly=gross.chain.base,
        seniority_monthly=gross.chain.seniority,
        allowances_monthly=gross.chain.allowances_total,
        ad_personam_monthly=gross.ad_personam,
        second_level_monthly=gross.second_level_monthly_total,
        gross_monthly=gross.gross_monthly,
        gross_annual=gross.gross_annual,
        hourly_rate=work.hourly_rate,
        apprenticeship_pct=gross.apprenticeship_pct,
        apprenticeship_under_level_code=gross.under_level_code,
        inps_employee_annual=fiscal.inps_employee_annual,
        inps_employer_annual=fiscal.inps_employer_annual,
        employer_funds_annual=fiscal.employer_funds_annual,
        tfr_annual=fiscal.tfr_annual,
        taxable_income=fiscal.taxable_income,
        irpef_gross=fiscal.irpef_gross,
        work_income_deduction=fiscal.work_income_deduction,
        irpef_net=fiscal.irpef_net,
        employer_withholds_irpef=fiscal.employer_withholds_irpef,
        addizionale_regionale_annual=fiscal.addizionale_regionale,
        addizionale_comunale_annual=fiscal.addizionale_comunale,
        trattamento_integrativo=fiscal.trattamento_integrativo,
        fiscal_simplifications=fiscal.fiscal_simplifications,
        net_annual=fiscal.net_annual,
        net_monthly=fiscal.net_monthly,
        employer_cost_annual=fiscal.employer_cost_annual,
        provenance=provenance,
        status=result_status,
        confidence=_compute_confidence(result_status, result_warnings, provenance),
        calculation_scope=calculation_scope,
        warnings=result_warnings,
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
        family_deduction_spouse_annual=fiscal.fam_spouse,
        family_deduction_children_annual=fiscal.fam_children,
        family_deduction_other_annual=fiscal.fam_other,
        family_deduction_annual=fiscal.fam_total,
        unused_family_deduction_annual=fiscal.fam_unused,
        art15_deduction_annual=fiscal.art15_total,
        unused_art15_deduction_annual=fiscal.art15_unused,
    )
    return build_calculation(scenario, ccnl, rules, surtax, gross, work, result)
