"""Fiscal, contribution, and tax-credit pay-item builders."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.item_producer_policy import _resolve
from ccnl_engine.engine.payroll.domain.pay_items import (
    CompetencePeriod,
    ContractRenewalArrears,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    MaternityItem,
    TaxCreditItem,
    TaxRefundItem,
    TfrAccrualItem,
    TfrSettlementItem,
    WorkInjuryItem,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.engine.payroll.service.fiscal_result import FiscalPay

_ZERO = Decimal(0)


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
    if fiscal.termination_tfr_liquidation_annual != _ZERO:
        items.append(
            TfrSettlementItem(
                item_id=f"tfr_settlement_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.termination_tfr_liquidation_annual,
                policy_decision=_resolve("tfr_settlement_item", as_of),
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
    if fiscal.maternity_inps_indemnity_annual != _ZERO:
        items.append(
            MaternityItem(
                item_id=f"maternity_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.maternity_inps_indemnity_annual,
                policy_decision=_resolve("maternity_item", as_of),
            )
        )
    if fiscal.workplace_injury_inail_indemnity_annual != _ZERO:
        items.append(
            WorkInjuryItem(
                item_id=f"work_injury_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.workplace_injury_inail_indemnity_annual,
                policy_decision=_resolve("work_injury_item", as_of),
            )
        )
    items.extend(_build_tax_credit_items(fiscal, period, payment, yymm, as_of))
    return items


def _build_tax_credit_items(
    fiscal: FiscalPay,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce TaxCreditItem and TaxRefundItem from deduction and conguaglio fields.

    Returns:
        List of tax credit and refund items for the period.
    """
    items: list[PayItem] = []
    if fiscal.work_income_deduction != _ZERO:
        items.append(
            TaxCreditItem(
                item_id=f"work_deduction_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.work_income_deduction,
                policy_decision=_resolve("tax_credit_item", as_of),
            )
        )
    if fiscal.fam_total != _ZERO:
        items.append(
            TaxCreditItem(
                item_id=f"family_deduction_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.fam_total,
                policy_decision=_resolve("tax_credit_item", as_of),
            )
        )
    if fiscal.conguaglio_annual > _ZERO:
        items.append(
            TaxRefundItem(
                item_id=f"conguaglio_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=fiscal.conguaglio_annual,
                policy_decision=_resolve("tax_refund_item", as_of),
            )
        )
    return items
