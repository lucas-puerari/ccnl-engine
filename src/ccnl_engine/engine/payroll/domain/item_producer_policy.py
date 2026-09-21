"""Italian payroll treatment policies for pay-item production.

Defines the canonical Italian payroll treatment policies (tax, contribution,
TFR, cost axes) and the POLICY_REGISTRY lookup table used by the item
builders to resolve a PolicyDecision for each pay-item kind.
"""

from __future__ import annotations

from datetime import date

from ccnl_engine.engine.payroll.domain.pay_items import (
    ContributionTreatment,
    CostTreatment,
    PayItemPolicy,
    PolicyDecision,
    TaxTreatment,
    TfrTreatment,
)

_EPOCH = date(2000, 1, 1)

_ART51 = "Art. 51 TUIR"
_ART2120 = "Art. 2120 c.c."
_DPR22_5 = "DPR 917/1986 art. 22"
_ART12_13 = "Art. 12-13 TUIR"


def _decision(
    policy_id: str,
    tax: TaxTreatment,
    contribution: ContributionTreatment,
    tfr: TfrTreatment,
    cost: CostTreatment,
    legal_basis: str,
) -> PolicyDecision:
    return PolicyDecision(
        policy_id=policy_id,
        policy_version="2026.1",
        effective_from=_EPOCH,
        effective_until=None,
        tax_treatment=tax,
        contribution_treatment=contribution,
        tfr_treatment=tfr,
        cost_treatment=cost,
        legal_basis=legal_basis,
    )


def _policy(
    policy_id: str,
    kinds: tuple[str, ...],
    tax: TaxTreatment,
    contribution: ContributionTreatment,
    tfr: TfrTreatment,
    cost: CostTreatment,
    legal_basis: str,
) -> PayItemPolicy:
    dec = _decision(policy_id, tax, contribution, tfr, cost, legal_basis)
    return PayItemPolicy(
        policy_id=policy_id,
        policy_version="2026.1",
        applies_to_kinds=kinds,
        effective_from=_EPOCH,
        effective_until=None,
        default_decision=dec,
    )


# Standard Italian payroll treatment policies (Art. 51 TUIR and related norms).
ORDINARY_EARNING_POLICY = _policy(
    "it/earning/ordinary",
    (
        "base_salary_earning",
        "seniority_earning",
        "fixed_allowance_earning",
        "one_off_earning",
    ),
    TaxTreatment.ORDINARY,
    ContributionTreatment.INCLUDED,
    TfrTreatment.INCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

SUPPLEMENT_POLICY = _policy(
    "it/earning/supplement",
    ("overtime_earning", "night_holiday_shift_earning"),
    TaxTreatment.ORDINARY,
    ContributionTreatment.INCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

ABSENCE_DEDUCTION_POLICY = _policy(
    "it/deduction/absence",
    ("absence_deduction",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.INCLUDED,
    TfrTreatment.INCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

VARIABLE_PAY_POLICY = _policy(
    "it/earning/variable",
    ("bonus_earning", "contract_renewal_arrears"),
    TaxTreatment.ORDINARY,
    ContributionTreatment.INCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

FRINGE_BENEFIT_POLICY = _policy(
    "it/benefit/fringe",
    ("fringe_benefit_item",),
    TaxTreatment.NON_CASH_TAXABLE,
    ContributionTreatment.INCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYER_COST,
    "Art. 51 c.3 TUIR",
)

WELFARE_POLICY = _policy(
    "it/benefit/welfare",
    ("welfare_item",),
    TaxTreatment.EXEMPT,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYER_COST,
    "Art. 51 c.2 TUIR",
)

TFR_ACCRUAL_POLICY = _policy(
    "it/tfr/accrual",
    ("tfr_accrual_item",),
    TaxTreatment.SEPARATE,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.SPECIAL,
    CostTreatment.ACCRUAL_ONLY,
    _ART2120,
)

TFR_SETTLEMENT_POLICY = _policy(
    "it/tfr/settlement",
    ("tfr_settlement_item",),
    TaxTreatment.SEPARATE,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.SPECIAL,
    CostTreatment.EMPLOYEE_CASH,
    _ART2120,
)

EMPLOYEE_CONTRIBUTION_POLICY = _policy(
    "it/contribution/employee",
    ("employee_withholding_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _DPR22_5,
)

EMPLOYER_CONTRIBUTION_POLICY = _policy(
    "it/contribution/employer",
    ("employer_contribution_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYER_COST,
    _DPR22_5,
)

EXTRA_MONTH_EARNING_POLICY = _policy(
    "it/earning/extra_month",
    ("extra_month_earning",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.INCLUDED,
    TfrTreatment.INCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

SICKNESS_POLICY = _policy(
    "it/indemnity/sickness",
    ("sickness_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

MATERNITY_POLICY = _policy(
    "it/indemnity/maternity",
    ("maternity_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

WORK_INJURY_POLICY = _policy(
    "it/indemnity/work_injury",
    ("work_injury_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART51,
)

TAX_CREDIT_POLICY = _policy(
    "it/tax/credit",
    ("tax_credit_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART12_13,
)

TAX_REFUND_POLICY = _policy(
    "it/tax/refund",
    ("tax_refund_item",),
    TaxTreatment.ORDINARY,
    ContributionTreatment.EXCLUDED,
    TfrTreatment.EXCLUDED,
    CostTreatment.EMPLOYEE_CASH,
    _ART12_13,
)

# Flat registry: kind -> policy for quick lookup.
POLICY_REGISTRY: dict[str, PayItemPolicy] = {
    k: p
    for p in (
        ORDINARY_EARNING_POLICY,
        SUPPLEMENT_POLICY,
        ABSENCE_DEDUCTION_POLICY,
        VARIABLE_PAY_POLICY,
        FRINGE_BENEFIT_POLICY,
        WELFARE_POLICY,
        TFR_ACCRUAL_POLICY,
        TFR_SETTLEMENT_POLICY,
        EMPLOYEE_CONTRIBUTION_POLICY,
        EMPLOYER_CONTRIBUTION_POLICY,
        EXTRA_MONTH_EARNING_POLICY,
        SICKNESS_POLICY,
        MATERNITY_POLICY,
        WORK_INJURY_POLICY,
        TAX_CREDIT_POLICY,
        TAX_REFUND_POLICY,
    )
    for k in p.applies_to_kinds
}


def _resolve(kind: str, as_of: date) -> PolicyDecision | None:
    policy = POLICY_REGISTRY.get(kind)
    if policy is None:
        return None
    return policy.resolve(kind, as_of)
