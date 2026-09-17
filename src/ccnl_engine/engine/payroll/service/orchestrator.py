"""Coordinate gross, fiscal and optional computations into a payroll result."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, assert_never

from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.domain.employee import (
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.payroll.service.assembly import (
    _collect_provenance,
    build_calculation,
)
from ccnl_engine.engine.payroll.service.fiscal import compute_fiscal
from ccnl_engine.engine.payroll.service.gross import compute_gross
from ccnl_engine.engine.payroll.service.scope import (
    build_scope,
    compute_confidence,
    compute_result_status,
)
from ccnl_engine.engine.payroll.service.work_rules import compute_work_rules
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.engine.tax.service.loaders import (
    load_year_rules,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.calculation import (
        Calculation,
    )
    from ccnl_engine.engine.payroll.domain.scenario import Employment, PayrollScenario


_IVS_CEILING_THRESHOLD = date(1996, 1, 1)


def _ivs_date_msg(hire_date: date) -> str | None:
    """Warning when an explicit hire date is on or after the IVS threshold.

    Returns:
        Warning string, or ``None`` when hire date is before the threshold.
    """
    if hire_date < _IVS_CEILING_THRESHOLD:
        return None
    return (
        f"hire date {hire_date} is on or after "
        f"{_IVS_CEILING_THRESHOLD}: contributions are overstated; "
        "consider setting ivs_ceiling_applies=True"
    )


def _ivs_months_msg(months: int, as_of: date) -> str | None:
    """Warning when implied hire date (from months of service) is post-threshold.

    Returns:
        Warning string, or ``None`` when the implied hire predates the threshold.
    """
    months_since_threshold = (as_of.year - _IVS_CEILING_THRESHOLD.year) * 12 + (
        as_of.month - _IVS_CEILING_THRESHOLD.month
    )
    if months > months_since_threshold:
        return None  # implied hire date is before the threshold
    return (
        f"seniority of {months} months implies hire on or after "
        f"{_IVS_CEILING_THRESHOLD}: contributions are overstated; "
        "consider setting ivs_ceiling_applies=True"
    )


def _ivs_ceiling_warning(
    scenario: PayrollScenario,
    as_of: date,
    contribution_base: Decimal,
    ivs_ceiling: Decimal | None,
) -> str | None:
    """Return a warning when a post-1996 hire has ivs_ceiling_applies=False.

    Workers hired on or after 1996-01-01 are subject to the INPS IVS
    contribution ceiling.  When the ceiling is skipped, the engine uses a
    higher contribution base, so computed contributions are overstated.

    When ``ivs_ceiling`` is known and the contribution base does not exceed
    it, the ceiling would have no effect, so no warning is emitted.

    Covers all three seniority input types:

    - ``SeniorityByDate``: compare the explicit hire date to the threshold.
    - ``SeniorityByMonths``: derive an implied hire date from *as_of* and
      the stored months count; warn when the implied date is on or after
      the threshold.
    - ``SeniorityByCount``: hire date is unknowable; always warn so the
      caller can make an explicit choice.

    Returns:
        A warning string, or ``None`` when no warning is warranted.
    """
    if scenario.employee.ivs_ceiling_applies:
        return None
    if ivs_ceiling is not None and contribution_base <= ivs_ceiling:
        return None
    seniority = scenario.employee.seniority
    if seniority is None:
        # When seniority is absent we cannot determine whether the ceiling
        # applies.  Warn only when we know the ceiling exists and the base
        # already exceeds it (the prior guard handled base ≤ ceiling), so
        # the economic impact of the wrong decision is concrete.
        return (
            (
                "seniority is None: IVS ceiling applicability cannot be "
                "determined; if the worker was hired on or after "
                f"{_IVS_CEILING_THRESHOLD}, contributions are overstated. "
                "Set ivs_ceiling_applies=True to apply the IVS ceiling."
            )
            if ivs_ceiling is not None
            else None
        )
    if isinstance(seniority, SeniorityByDate):
        return _ivs_date_msg(seniority.value)
    if isinstance(seniority, SeniorityByMonths):
        return _ivs_months_msg(seniority.value, as_of)
    if isinstance(seniority, SeniorityByCount):
        return (
            "SeniorityByCount used without ivs_ceiling_applies: "
            f"if hired on or after {_IVS_CEILING_THRESHOLD}, "
            "contributions are overstated; "
            "consider setting ivs_ceiling_applies=True"
        )
    assert_never(seniority)  # pragma: no cover


def _resolve_tax_year(employment: Employment) -> int:
    """Return the tax year for rule loading.

    Uses the explicit override when set, otherwise falls back to the
    calendar year of the employment date.

    Returns:
        Integer year for ``load_year_rules`` and ``load_surtax_rules``.
    """
    if employment.tax_year is not None:
        return employment.tax_year
    return employment.calculation_date.year


def compute(scenario: PayrollScenario) -> Calculation:
    """Compute gross-to-net salary and employer cost for a payroll scenario.

    Loads the CCNL, tax/INPS rules, and (when jurisdiction is set) surtax
    rules from the bundled knowledge base, then runs the full payroll
    computation chain.

    Returns:
        :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with all gross, net and cost figures plus a serialisable input snapshot.
    """
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
    provenance = _collect_provenance(
        gross.level,
        as_of,
        gross.chain,
        ccnl.parameters.seniority_increments,
        ccnl=ccnl,
        under_level_code=gross.under_level_code,
    )
    result_status = compute_result_status(calculation_scope)
    # Gather all RulesetIdentity records for rulesets actually consumed so
    # that compute_confidence can downgrade from "high" when any of them
    # has verification_status != "verified".  None entries mean "consumed
    # but identity absent" and are treated as unverified by compute_confidence.
    # Main rulesets (ccnl, tax rules) are always consumed; INPS rules are only
    # consumed for the standard percentage model, not the domestic forfait model.
    # Optional-feature rulesets are only added when the feature was used.
    main_rulesets: tuple[RulesetIdentity | None, ...] = (ccnl.ruleset, rules.ruleset)
    if rules.domestic_contributions is None:
        # Standard percentage model: INPS rules were consumed.
        main_rulesets = (*main_rulesets, rules.inps_ruleset)
    consumed_rulesets = (
        main_rulesets + tuple(work.consumed_ruleset_ids) + fiscal.consumed_ruleset_ids
    )
    ivs_ceiling = rules.inps.ceiling if rules.inps is not None else None
    # Domestic contracts use per-hour forfait rates; the IVS ceiling model
    # does not participate in that calculation, so no warning is warranted.
    ivs_warn = (
        None
        if rules.domestic_contributions is not None
        else _ivs_ceiling_warning(scenario, as_of, gross.contribution_base, ivs_ceiling)
    )
    result_warnings = (
        (*work.warnings, ivs_warn) if ivs_warn is not None else work.warnings
    )

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
        bilateral_employee_annual=fiscal.bilateral_employee_annual,
        bilateral_employer_annual=fiscal.bilateral_employer_annual,
        taxable_income=fiscal.taxable_income,
        irpef_gross=fiscal.irpef_gross,
        work_income_deduction=fiscal.work_income_deduction,
        ulteriore_detrazione_lavoro=fiscal.ulteriore_detrazione_lavoro,
        somma_esente=fiscal.somma_esente,
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
        confidence=compute_confidence(
            result_status, result_warnings, provenance, consumed_rulesets
        ),
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
        sterilizzazione_clawback_annual=fiscal.sterilizzazione_clawback,
    )
    return build_calculation(scenario, ccnl, rules, surtax, gross, work, result)
