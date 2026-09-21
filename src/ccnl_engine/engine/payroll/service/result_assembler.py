"""Assemble payroll sub-objects (Earnings, Contributions, Taxes) from stage payloads."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.payroll_result import (
    Contributions,
    Earnings,
    Taxes,
)
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from decimal import Decimal


def _net_monthly(fiscal: object, gross: object) -> Decimal:
    """Return net_annual divided by additional_months, rounded to EUR cents.

    Returns:
        Decimal net monthly.
    """
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay  # noqa: PLC0415
    from ccnl_engine.engine.payroll.service.gross import GrossPay  # noqa: PLC0415

    assert isinstance(fiscal, FiscalPay)
    assert isinstance(gross, GrossPay)
    return money(fiscal.net_annual / gross.additional_months)


def _build_earnings(gross: object, work: object) -> Earnings:
    """Build :class:`Earnings` from the gross and work-rules payloads.

    Returns:
        Earnings sub-object populated from *gross* and *work*.
    """
    from ccnl_engine.engine.payroll.service.gross import GrossPay  # noqa: PLC0415
    from ccnl_engine.engine.payroll.service.work_rules import (  # noqa: PLC0415
        WorkRulesPay,
    )

    g = gross
    w = work
    assert isinstance(g, GrossPay)
    assert isinstance(w, WorkRulesPay)
    return Earnings(
        seniority_count=g.count,
        base_monthly=g.chain.base,
        seniority_monthly=g.chain.seniority,
        allowances_monthly=g.chain.allowances_total,
        ad_personam_monthly=g.ad_personam,
        second_level_monthly=g.second_level_monthly_total,
        gross_monthly=g.gross_monthly,
        gross_annual=g.gross_annual,
        hourly_rate=w.hourly_rate,
        apprenticeship_pct=g.apprenticeship_pct,
        apprenticeship_under_level_code=g.under_level_code,
    )


def _build_contributions(fiscal: object) -> Contributions:
    """Build :class:`Contributions` from the fiscal payload.

    Returns:
        Contributions sub-object populated from *fiscal*.
    """
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay  # noqa: PLC0415

    f = fiscal
    assert isinstance(f, FiscalPay)
    return Contributions(
        inps_employee_annual=f.inps_employee_annual,
        inps_employer_annual=f.inps_employer_annual,
        inail_employer_annual=f.inail_employer_annual,
        inps_employer_exemption_annual=f.inps_employer_exemption_annual,
        maternity_inps_indemnity_annual=f.maternity_inps_indemnity_annual,
        workplace_injury_inail_indemnity_annual=f.workplace_injury_inail_indemnity_annual,
        termination_tfr_liquidation_annual=f.termination_tfr_liquidation_annual,
        employer_funds_annual=f.employer_funds_annual,
        tfr_annual=f.tfr_annual,
        bilateral_employee_annual=f.bilateral_employee_annual,
        bilateral_employer_annual=f.bilateral_employer_annual,
        health_fund_employee_annual=f.health_fund_employee_annual,
        health_fund_employer_annual=f.health_fund_employer_annual,
    )


def _build_taxes(fiscal: object) -> Taxes:
    """Build :class:`Taxes` from the fiscal payload.

    Returns:
        Taxes sub-object populated from *fiscal*.
    """
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay  # noqa: PLC0415

    f = fiscal
    assert isinstance(f, FiscalPay)
    return Taxes(
        taxable_income=f.taxable_income,
        irpef_gross=f.irpef_gross,
        work_income_deduction=f.work_income_deduction,
        ulteriore_detrazione_lavoro=f.ulteriore_detrazione_lavoro,
        somma_esente=f.somma_esente,
        irpef_net=f.irpef_net,
        employer_withholds_irpef=f.employer_withholds_irpef,
        addizionale_regionale_annual=f.addizionale_regionale,
        addizionale_comunale_annual=f.addizionale_comunale,
        trattamento_integrativo=f.trattamento_integrativo,
        fiscal_simplifications=f.fiscal_simplifications,
        family_deduction_spouse_annual=f.fam_spouse,
        family_deduction_children_annual=f.fam_children,
        family_deduction_other_annual=f.fam_other,
        family_deduction_annual=f.fam_total,
        unused_family_deduction_annual=f.fam_unused,
        art15_deduction_annual=f.art15_total,
        unused_art15_deduction_annual=f.art15_unused,
        sterilizzazione_clawback_annual=f.sterilizzazione_clawback,
        conguaglio_annual=f.conguaglio_annual,
        termination_residual_leave_payout_annual=f.termination_residual_leave_payout_annual,
        contract_renewal_arrears_annual=f.contract_renewal_arrears_annual,
        una_tantum_annual=f.una_tantum_annual,
        personal_withholdings_annual=f.personal_withholdings_annual,
        additional_irpef_base_annual=f.additional_irpef_base_annual,
        territorial_supplement_annual=f.territorial_supplement_annual,
        company_supplement_annual=f.company_supplement_annual,
    )
