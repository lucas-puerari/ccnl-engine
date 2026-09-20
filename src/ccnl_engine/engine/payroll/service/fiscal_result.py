"""FiscalPay result dataclass: annual contributions, tax, deductions and net pay."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification


@dataclass(frozen=True)
class FiscalPay:
    """Annual contributions, tax, deductions and net pay."""

    consumed_ruleset_ids: tuple[RulesetIdentity | None, ...]
    consumed_verifications: dict[str, str]
    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    inps_employee_additional_annual: Decimal
    inail_employer_annual: Decimal
    inps_employer_exemption_annual: Decimal
    maternity_inps_indemnity_annual: Decimal
    workplace_injury_inail_indemnity_annual: Decimal
    termination_tfr_liquidation_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
    bilateral_employee_annual: Decimal
    bilateral_employer_annual: Decimal
    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    fam_spouse: Decimal
    fam_children: Decimal
    fam_other: Decimal
    fam_total: Decimal
    fam_unused: Decimal
    art15_total: Decimal
    art15_unused: Decimal
    sterilizzazione_clawback: Decimal
    ulteriore_detrazione_lavoro: Decimal
    somma_esente: Decimal
    irpef_net: Decimal
    conguaglio_annual: Decimal
    termination_residual_leave_payout_annual: Decimal
    contract_renewal_arrears_annual: Decimal
    una_tantum_annual: Decimal
    personal_withholdings_annual: Decimal
    additional_irpef_base_annual: Decimal
    health_fund_employee_annual: Decimal
    health_fund_employer_annual: Decimal
    territorial_supplement_annual: Decimal
    company_supplement_annual: Decimal
    trattamento_integrativo: Decimal
    addizionale_regionale: Decimal
    addizionale_comunale: Decimal
    net_annual: Decimal
    net_monthly: Decimal
    employer_cost_annual: Decimal
    employer_withholds_irpef: bool
    fiscal_simplifications: frozenset[FiscalSimplification]
