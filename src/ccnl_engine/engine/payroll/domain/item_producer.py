"""Build typed PayItem objects with PolicyDecision from payroll computation results.

Each non-zero computation output is wrapped as a typed PayItem carrying the
standard Italian payroll treatment (tax, contribution, TFR, cost axes).  The
resulting tuple can be stored on Calculation.pay_items and used to project raw
totals without re-running the computation.
"""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BaseSalaryEarning,
    BonusEarning,
    CompetencePeriod,
    ContractRenewalArrears,
    ContributionTreatment,
    CostTreatment,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    ExtraMonthEarning,
    FixedAllowanceEarning,
    FringeBenefitItem,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItemPolicy,
    PolicyDecision,
    SeniorityEarning,
    TaxTreatment,
    TfrAccrualItem,
    TfrTreatment,
    WelfareItem,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.engine.payroll.service.fiscal_result import FiscalPay
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay

_ZERO = Decimal(0)
_EPOCH = date(2000, 1, 1)

_ART51 = "Art. 51 TUIR"
_ART2120 = "Art. 2120 c.c."
_DPR22_5 = "DPR 917/1986 art. 22"


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
        EMPLOYEE_CONTRIBUTION_POLICY,
        EMPLOYER_CONTRIBUTION_POLICY,
        EXTRA_MONTH_EARNING_POLICY,
    )
    for k in p.applies_to_kinds
}


def _last_day(as_of: date) -> date:
    last = calendar.monthrange(as_of.year, as_of.month)[1]
    return date(as_of.year, as_of.month, last)


def _period(as_of: date) -> CompetencePeriod:
    return CompetencePeriod(year=as_of.year, month=as_of.month)


def _resolve(kind: str, as_of: date) -> PolicyDecision | None:
    policy = POLICY_REGISTRY.get(kind)
    if policy is None:
        return None
    return policy.resolve(kind, as_of)


def _build_gross_items(
    gross: GrossPay,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce items from contractual gross-pay chain components.

    Returns:
        List of typed PayItem objects for base salary, seniority, and allowances.
    """
    items: list[PayItem] = []
    if gross.chain.base != _ZERO:
        items.append(
            BaseSalaryEarning(
                item_id=f"base_salary_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=gross.chain.base,
                policy_decision=_resolve("base_salary_earning", as_of),
            )
        )
    if gross.chain.seniority != _ZERO:
        items.append(
            SeniorityEarning(
                item_id=f"seniority_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(gross.count),
                amount=gross.chain.seniority,
                seniority_count=gross.count,
                policy_decision=_resolve("seniority_earning", as_of),
            )
        )
    for allowance, amount in gross.chain.allowances:
        if amount == _ZERO:
            continue
        items.append(
            FixedAllowanceEarning(
                item_id=f"allowance_{allowance.code}_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=amount,
                allowance_code=allowance.code,
                policy_decision=_resolve("fixed_allowance_earning", as_of),
            )
        )
    return items


def _build_work_items(
    work: WorkRulesPay,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce items from work-rules supplements and variable pay.

    Returns:
        List of typed PayItem objects for supplements, absence, and variable pay.
    """
    items: list[PayItem] = []
    if work.overtime_supp != _ZERO:
        items.append(
            OvertimeEarning(
                item_id=f"overtime_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.overtime_supp,
                hours=work.overtime_hours,
                policy_decision=_resolve("overtime_earning", as_of),
            )
        )
    if work.night_supp != _ZERO:
        items.append(
            NightHolidayShiftEarning(
                item_id=f"night_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.night_supp,
                hours=work.night_hours,
                policy_decision=_resolve("night_holiday_shift_earning", as_of),
            )
        )
    if work.holiday_supp != _ZERO:
        items.append(
            NightHolidayShiftEarning(
                item_id=f"holiday_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.holiday_supp,
                hours=work.holiday_hours,
                policy_decision=_resolve("night_holiday_shift_earning", as_of),
            )
        )
    if work.absence_deduction_monthly != _ZERO:
        items.append(
            AbsenceDeduction(
                item_id=f"absence_deduction_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=-work.absence_deduction_monthly,
                absence_days=Decimal(1),
                policy_decision=_resolve("absence_deduction", as_of),
            )
        )
    if work.bonus_annual != _ZERO:
        items.append(
            BonusEarning(
                item_id=f"bonus_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.bonus_annual,
                policy_decision=_resolve("bonus_earning", as_of),
            )
        )
    if work.fringe_benefit_annual != _ZERO:
        items.append(
            FringeBenefitItem(
                item_id=f"fringe_benefit_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.fringe_benefit_annual,
                threshold_annual=work.fringe_benefit_threshold_annual,
                taxable_amount=work.fringe_benefit_taxable_annual,
                policy_decision=_resolve("fringe_benefit_item", as_of),
            )
        )
    if work.welfare_annual != _ZERO:
        items.append(
            WelfareItem(
                item_id=f"welfare_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.welfare_annual,
                policy_decision=_resolve("welfare_item", as_of),
            )
        )
    return items


def _build_fiscal_items(
    fiscal: FiscalPay,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce items from fiscal contributions and TFR accrual.

    Returns:
        List of typed PayItem objects for contributions, TFR, and arrears.
    """
    items: list[PayItem] = []
    if fiscal.contract_renewal_arrears_annual != _ZERO:
        items.append(
            ContractRenewalArrears(
                item_id=f"contract_renewal_arrears_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.contract_renewal_arrears_annual,
                policy_decision=_resolve("contract_renewal_arrears", as_of),
            )
        )
    if fiscal.tfr_annual != _ZERO:
        items.append(
            TfrAccrualItem(
                item_id=f"tfr_accrual_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.tfr_annual,
                policy_decision=_resolve("tfr_accrual_item", as_of),
            )
        )
    if fiscal.inps_employee_annual != _ZERO:
        items.append(
            EmployeeWithholdingItem(
                item_id=f"inps_employee_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=-fiscal.inps_employee_annual,
                policy_decision=_resolve("employee_withholding_item", as_of),
            )
        )
    if fiscal.inps_employer_annual != _ZERO:
        items.append(
            EmployerContributionItem(
                item_id=f"inps_employer_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.inps_employer_annual,
                policy_decision=_resolve("employer_contribution_item", as_of),
            )
        )
    if fiscal.inail_employer_annual != _ZERO:
        items.append(
            EmployerContributionItem(
                item_id=f"inail_employer_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.inail_employer_annual,
                policy_decision=_resolve("employer_contribution_item", as_of),
            )
        )
    return items


def _build_extra_month_items(
    gross: GrossPay,
    extra_monthly_payments: int,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce ExtraMonthEarning items for tredicesima and quattordicesima.

    Returns:
        List of ExtraMonthEarning items (0, 1, or 2 entries).
    """
    items: list[PayItem] = []
    amount = gross.gross_monthly
    if amount == _ZERO:
        return items
    for i in range(extra_monthly_payments):
        month_number = 13 + i
        items.append(
            ExtraMonthEarning(
                item_id=f"extra_month_{month_number}_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=amount,
                month_number=month_number,
                policy_decision=_resolve("extra_month_earning", as_of),
            )
        )
    return items


def build_pay_items(
    gross: GrossPay,
    work: WorkRulesPay,
    fiscal: FiscalPay,
    as_of: date,
    extra_monthly_payments: int = 0,
) -> tuple[PayItem, ...]:
    """Produce typed PayItem objects from a completed payroll computation.

    One item is produced per non-zero computation output.  Each item carries a
    :class:`~ccnl_engine.engine.payroll.domain.pay_items.PolicyDecision` that
    encodes the Italian payroll treatment on the four axes (tax, contribution,
    TFR, cost).  Amounts mirror those recorded by the ledger builder so that
    totals are derivable by summing items grouped by account.

    Args:
        gross: Resolved contractual pay components.
        work: Work-rules pay components (supplements, absence, variable pay).
        fiscal: Annual contributions, taxes and net pay.
        as_of: Competence date (first day of the payroll month).
        extra_monthly_payments: Number of extra monthly payments (0, 1, or 2).

    Returns:
        Tuple of typed PayItem objects, one per non-zero component.
    """
    period = _period(as_of)
    payment = _last_day(as_of)
    yymm = f"{period.year}_{period.month:02d}"
    items: list[PayItem] = []
    items.extend(_build_gross_items(gross, period, payment, yymm, as_of))
    items.extend(
        _build_extra_month_items(
            gross, extra_monthly_payments, period, payment, yymm, as_of
        )
    )
    items.extend(_build_work_items(work, period, payment, yymm, as_of))
    items.extend(_build_fiscal_items(fiscal, period, payment, yymm, as_of))
    return tuple(items)
