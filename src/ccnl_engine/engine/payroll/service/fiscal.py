"""Annual contributions, tax and deduction coordination."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.scenario import TaxPeriod
from ccnl_engine.engine.payroll.service import contributions as _contrib
from ccnl_engine.engine.payroll.service import irpef as _irpef
from ccnl_engine.engine.payroll.service.fiscal_contributions import (
    _compute_bilateral_funds,
    _employer_funds,
    _inps_contributions,
)
from ccnl_engine.engine.payroll.service.fiscal_deductions import (
    _compute_ti,
    _run_wr_art15_deductions,
    _run_wr_family_deductions,
)
from ccnl_engine.engine.payroll.service.fiscal_helpers import (
    _conguaglio,
    _injury_indemnity,
    _inps_exemption,
    _maternity_indemnity,
    _termination_amount,
    _update_simplification_flags,
)
from ccnl_engine.engine.payroll.service.fiscal_result import FiscalPay
from ccnl_engine.engine.payroll.service.fiscal_rulesets import _fiscal_consumed
from ccnl_engine.engine.payroll.service.fiscal_surtax import _compute_addizionali
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
    )
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

_ZERO = Decimal(0)

__all__ = ["FiscalPay", "compute_fiscal"]


def compute_fiscal(
    scenario: PayrollScenario,
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    gross: GrossPay,
    year: int,
    work: WorkRulesPay,
) -> FiscalPay:
    """Apply the annual fiscal chain to resolved gross pay.

    Returns:
        Contributions, deductions, net pay and fiscal simplifications.
    """
    j = scenario.employee.jurisdiction
    ivs_ceiling_applies = scenario.employee.ivs_ceiling_applies

    inps_employee_annual, inps_employer_annual, inps_employee_additional_annual = (
        _inps_contributions(
            rules,
            scenario.employment.contract,
            gross.gross_monthly,
            gross.contribution_base,
            gross.worker_category,
            weekly_hours=scenario.employee.weekly_hours,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )
    )
    employer_funds_annual = _employer_funds(
        ccnl,
        gross.worker_category,
        gross.contribution_base,
        scenario.employment.as_of,
    )
    tfr_annual = _contrib.tfr(gross.tfr_base, rules)
    bilateral_employee_annual, bilateral_employer_annual = _compute_bilateral_funds(
        scenario.bilateral_funds,
        gross.tfr_base,
        gross.gross_annual,
    )
    inail_rate = scenario.employment.employer.inail_rate
    inail_employer_annual = (
        money(gross.gross_annual * inail_rate) if inail_rate is not None else _ZERO
    )
    inps_employer_exemption_annual = _inps_exemption(
        inps_employer_annual,
        scenario.employment.employer.inps_employer_exemption_annual,
    )
    maternity_inps_indemnity_annual = _maternity_indemnity(
        scenario.maternity_inps_indemnity_annual
    )
    workplace_injury_inail_indemnity_annual = _injury_indemnity(
        scenario.workplace_injury_inail_indemnity_annual
    )
    termination_residual_leave_payout_annual = _termination_amount(
        scenario.termination_residual_leave_payout_annual
    )
    termination_tfr_liquidation_annual = _termination_amount(
        scenario.termination_tfr_liquidation_annual
    )
    contract_renewal_arrears_annual = _termination_amount(
        scenario.contract_renewal_arrears_annual
    )
    una_tantum_annual = _termination_amount(scenario.una_tantum_annual)
    personal_withholdings_annual = _termination_amount(
        scenario.personal_withholdings_annual
    )
    additional_irpef_base_annual = _termination_amount(
        scenario.additional_irpef_base_annual
    )
    health_fund_employee_annual = _termination_amount(
        scenario.health_fund_employee_annual
    )
    health_fund_employer_annual = _termination_amount(
        scenario.health_fund_employer_annual
    )
    territorial_supplement_annual = _termination_amount(
        scenario.territorial_supplement_annual
    )
    company_supplement_annual = _termination_amount(scenario.company_supplement_annual)

    taxable_income = money(
        gross.gross_annual
        - inps_employee_annual
        + work.fringe_benefit_taxable_annual
        + work.bonus_ordinary_taxable_annual
        + additional_irpef_base_annual
    )
    irpef_gross = _irpef.irpef_gross(taxable_income, rules)
    eligible_work_days = (
        scenario.tax_basis.eligible_work_days
        if isinstance(scenario.tax_basis, TaxPeriod)
        else 365
    )
    work_income_deduction = _irpef.work_income_deduction(
        taxable_income, eligible_work_days, rules.work_deduction
    )
    employer_withholds_irpef = not ccnl.meta.withholding_exempt

    # Family deductions (Art. 12 TUIR): computed when scenario.family is set.
    # These are the only work-rules feature that mutates irpef_net / net_annual.
    # Trattamento integrativo eligibility (Art. 1 D.L. 3/2020) depends on the
    # sum of Art. 13 + Art. 12 + qualifying Art. 15 deductions, per the statute.
    (
        fam_spouse,
        fam_children,
        fam_other,
        fam_total,
        fam_unused,
        fam_ruleset,
    ) = _run_wr_family_deductions(
        scenario=scenario,
        reddito_complessivo=taxable_income,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        year=year,
        employer_withholds_irpef=employer_withholds_irpef,
    )

    # Ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024):
    # flat EUR 1 000 for taxable income in (20 000, 32 000].
    # Must be computed before Art. 15 so it can be deducted from available
    # IRPEF when computing art15_unused.
    ud_rules = rules.ulteriore_detrazione
    if ud_rules is not None:
        ulteriore_detrazione_lavoro = _irpef.ulteriore_detrazione_lavoro(
            taxable_income, ud_rules, eligible_work_days
        )
    else:
        ulteriore_detrazione_lavoro = _ZERO

    # Art. 15 TUIR deductions (interessi passivi mutuo prima casa, etc.).
    art15_total, art15_unused, art15_ruleset = _run_wr_art15_deductions(
        scenario=scenario,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        fam_total=fam_total,
        ulteriore_detrazione_lavoro=ulteriore_detrazione_lavoro,
        year=year,
        employer_withholds_irpef=employer_withholds_irpef,
    )

    # Sterilizzazione detrazioni (Art. 1 c. 3-4 L. 199/2025): for reddito
    # complessivo > EUR 200 000, reduce oneri detraibili al 19% (Art. 15 c. 1
    # lett. a, b, d, e TUIR; not spese sanitarie lett. c) by EUR 440.
    effective_art15 = _irpef.apply_sterilizzazione_detrazioni(
        art15_total,
        taxable_income,
        rules.sterilizzazione_detrazioni,
    )
    sterilizzazione_clawback = money(art15_total - effective_art15)
    if sterilizzazione_clawback > _ZERO and employer_withholds_irpef:
        art15_capacity = money(
            max(
                _ZERO,
                irpef_gross
                - work_income_deduction
                - fam_total
                - ulteriore_detrazione_lavoro,
            )
        )
        art15_unused = money(max(_ZERO, effective_art15 - art15_capacity))

    # irpef_fiscal: the tax actually owed after all deductions, regardless of
    # whether the employer is a sostituto d'imposta.  Used to gate addizionali
    # (only due when IRPEF is owed) and to derive irpef_net.
    # When the employer is not a sostituto d'imposta, irpef_net is zeroed;
    # irpef_gross and work_income_deduction remain as informational figures.
    irpef_fiscal = money(
        max(
            _ZERO,
            irpef_gross
            - work_income_deduction
            - fam_total
            + sterilizzazione_clawback
            - art15_total
            - ulteriore_detrazione_lavoro,
        )
    )
    irpef_net = irpef_fiscal if employer_withholds_irpef else _ZERO
    conguaglio_annual = _conguaglio(irpef_net, scenario.prior_period_irpef_withheld)

    # Trattamento integrativo (Art. 1 D.L. 3/2020): computed when the tax
    # data file carries the required parameters.
    # relevant_deductions: Art. 12 + Art. 13 + qualifying Art. 15 (statute).
    # Only pre-2022 mortgage interest qualifies; later mortgages reduce
    # IRPEF but are excluded from the TI relevant-deductions sum.
    art15_pre_1993 = (
        art15_total
        if (
            scenario.art15_deductions is not None
            and scenario.art15_deductions.mortgage_pre_2022
        )
        else _ZERO
    )
    relevant_deductions = work_income_deduction + fam_total + art15_pre_1993
    trattamento_integrativo, fiscal_simplifications = _compute_ti(
        taxable_income,
        irpef_gross,
        work_income_deduction,
        relevant_deductions,
        rules,
        eligible_work_days,
    )

    # Somma esente (L. 207/2024): flat-rate net bonus for reddito complessivo
    # up to 20 000 EUR.  Added directly to net pay (not an IRPEF base change).
    se_rules = rules.somma_esente
    somma_esente_amount = (
        money(_irpef.somma_esente(taxable_income, se_rules))
        if se_rules is not None
        else _ZERO
    )

    fam = scenario.family
    has_any_dependent = fam is not None and fam.has_any_dependent
    fiscal_simplifications = _update_simplification_flags(
        fiscal_simplifications,
        has_any_dependent=has_any_dependent,
        art15_total=art15_total,
        ud_rules_present=ud_rules is not None,
        se_rules_present=se_rules is not None,
        has_bilateral_funds=bool(scenario.bilateral_funds),
    )

    # Addizionale regionale e comunale (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998).
    regione = j.regione if j is not None else None
    comune_belfiore = j.comune_belfiore if j is not None else None
    (
        addizionale_regionale,
        addizionale_comunale,
        fiscal_simplifications,
        surtax_reg_consumed,
        surtax_com_consumed,
    ) = _compute_addizionali(
        taxable_income,
        surtax,
        fiscal_simplifications,
        regione=regione,
        comune_belfiore=comune_belfiore,
        irpef_due=irpef_fiscal,
    )

    if employer_withholds_irpef:
        net_annual = money(
            gross.gross_annual
            - inps_employee_annual
            - irpef_net
            - addizionale_regionale
            - addizionale_comunale
            + trattamento_integrativo
            + somma_esente_amount
            - bilateral_employee_annual
            - work.bonus_pdr_flat_tax_annual
            + termination_residual_leave_payout_annual
            + contract_renewal_arrears_annual
            + una_tantum_annual
            - personal_withholdings_annual
            - health_fund_employee_annual
            + territorial_supplement_annual
            + company_supplement_annual
        )
    else:
        net_annual = money(
            gross.gross_annual
            - inps_employee_annual
            - bilateral_employee_annual
            + termination_residual_leave_payout_annual
            + contract_renewal_arrears_annual
            + una_tantum_annual
            - personal_withholdings_annual
            - health_fund_employee_annual
            + territorial_supplement_annual
            + company_supplement_annual
        )
    net_monthly = money(net_annual / gross.additional_months)
    employer_cost_annual = money(
        gross.gross_annual
        + inps_employer_annual
        - inps_employer_exemption_annual
        - maternity_inps_indemnity_annual
        - workplace_injury_inail_indemnity_annual
        + termination_residual_leave_payout_annual
        + contract_renewal_arrears_annual
        + una_tantum_annual
        + inail_employer_annual
        + employer_funds_annual
        + bilateral_employer_annual
        + health_fund_employer_annual
        + territorial_supplement_annual
        + company_supplement_annual
        + tfr_annual
    )

    consumed_ruleset_ids, consumed_ver = _fiscal_consumed(
        scenario,
        surtax,
        fam_ruleset,
        art15_ruleset,
        has_any_dependent=has_any_dependent,
        surtax_reg_consumed=surtax_reg_consumed,
        surtax_com_consumed=surtax_com_consumed,
    )

    return FiscalPay(
        consumed_ruleset_ids=consumed_ruleset_ids,
        consumed_verifications=consumed_ver,
        inps_employee_annual=inps_employee_annual,
        inps_employer_annual=inps_employer_annual,
        inps_employee_additional_annual=inps_employee_additional_annual,
        inail_employer_annual=inail_employer_annual,
        inps_employer_exemption_annual=inps_employer_exemption_annual,
        maternity_inps_indemnity_annual=maternity_inps_indemnity_annual,
        workplace_injury_inail_indemnity_annual=workplace_injury_inail_indemnity_annual,
        termination_tfr_liquidation_annual=termination_tfr_liquidation_annual,
        employer_funds_annual=employer_funds_annual,
        tfr_annual=tfr_annual,
        bilateral_employee_annual=bilateral_employee_annual,
        bilateral_employer_annual=bilateral_employer_annual,
        taxable_income=taxable_income,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        fam_spouse=fam_spouse,
        fam_children=fam_children,
        fam_other=fam_other,
        fam_total=fam_total,
        fam_unused=fam_unused,
        art15_total=art15_total,
        art15_unused=art15_unused,
        sterilizzazione_clawback=sterilizzazione_clawback,
        ulteriore_detrazione_lavoro=ulteriore_detrazione_lavoro,
        somma_esente=somma_esente_amount,
        irpef_net=irpef_net,
        conguaglio_annual=conguaglio_annual,
        termination_residual_leave_payout_annual=termination_residual_leave_payout_annual,
        contract_renewal_arrears_annual=contract_renewal_arrears_annual,
        una_tantum_annual=una_tantum_annual,
        personal_withholdings_annual=personal_withholdings_annual,
        additional_irpef_base_annual=additional_irpef_base_annual,
        health_fund_employee_annual=health_fund_employee_annual,
        health_fund_employer_annual=health_fund_employer_annual,
        territorial_supplement_annual=territorial_supplement_annual,
        company_supplement_annual=company_supplement_annual,
        trattamento_integrativo=trattamento_integrativo,
        addizionale_regionale=addizionale_regionale,
        addizionale_comunale=addizionale_comunale,
        net_annual=net_annual,
        net_monthly=net_monthly,
        employer_cost_annual=employer_cost_annual,
        employer_withholds_irpef=employer_withholds_irpef,
        fiscal_simplifications=fiscal_simplifications,
    )
