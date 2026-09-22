"""Post arrears, termination, TFR, and variable pay to the ledger."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.engine.payroll.service.ledger_builder._earnings import _last_day

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay

_ZERO = Decimal(0)


def post_arrears_termination_tfr(
    fiscal: FiscalPay, as_of: date, ledger: Ledger
) -> None:
    """Post contract-renewal arrears, termination payouts and TFR accrual.

    - ``contract_renewal_arrears_annual`` → CASH_EARNINGS
    - ``termination_residual_leave_payout_annual`` → CASH_EARNINGS
    - ``termination_tfr_liquidation_annual`` → TFR_SETTLEMENT
    - ``tfr_annual`` → TFR_ACCRUAL

    Zero-amount entries are silently skipped.

    Args:
        fiscal: The resolved fiscal-pay components.
        as_of: The competence date used to derive the year/month for entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"
    payment = _last_day(as_of)

    if fiscal.contract_renewal_arrears_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"contract_renewal_arrears_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"contract_renewal_arrears_{yymm}",
                pay_item_kind="contract_renewal_arrears",
                account=AccountKind.CASH_EARNINGS,
                amount=fiscal.contract_renewal_arrears_annual,
                source_item_id=f"contract_renewal_arrears_{yymm}",
                policy_decision_id="it/earning/variable",
            )
        )

    if fiscal.termination_residual_leave_payout_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"termination_leave_payout_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"termination_leave_payout_{yymm}",
                pay_item_kind="termination_leave_payout",
                account=AccountKind.CASH_EARNINGS,
                amount=fiscal.termination_residual_leave_payout_annual,
                source_item_id=f"termination_leave_payout_{yymm}",
            )
        )

    if fiscal.termination_tfr_liquidation_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"tfr_liquidation_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"tfr_liquidation_{yymm}",
                pay_item_kind="tfr_liquidation",
                account=AccountKind.TFR_SETTLEMENT,
                amount=fiscal.termination_tfr_liquidation_annual,
                source_item_id=f"tfr_liquidation_{yymm}",
            )
        )

    if fiscal.tfr_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"tfr_accrual_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"tfr_accrual_{yymm}",
                pay_item_kind="tfr_accrual",
                account=AccountKind.TFR_ACCRUAL,
                amount=fiscal.tfr_annual,
                source_item_id=f"tfr_accrual_{yymm}",
                policy_decision_id="it/tfr/accrual",
            )
        )


def post_variable_pay(work: WorkRulesPay, as_of: date, ledger: Ledger) -> None:
    """Post overtime, absences, bonuses and fringe benefits as ledger entries.

    Supplements (overtime, night, holiday) and bonuses post to CASH_EARNINGS.
    Absence deductions post to EMPLOYEE_DEDUCTIONS as positive amounts.
    Taxable fringe benefits and welfare post to NON_CASH_BENEFITS.
    Zero-amount entries are silently skipped.

    Args:
        work: The resolved work-rules pay components.
        as_of: The competence date used to derive the year/month for the entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"
    payment = _last_day(as_of)

    supplement_pairs = (
        (work.overtime_supp, "overtime_supplement"),
        (work.night_supp, "night_supplement"),
        (work.holiday_supp, "holiday_supplement"),
    )
    for amount, kind in supplement_pairs:
        if amount != _ZERO:
            ledger.append(
                LedgerEntry(
                    entry_id=f"{kind}_{yymm}",
                    competence_period=period,
                    payment_date=payment,
                    pay_item_id=f"{kind}_{yymm}",
                    pay_item_kind=kind,
                    account=AccountKind.CASH_EARNINGS,
                    amount=amount,
                    source_item_id=f"{kind}_{yymm}",
                    policy_decision_id="it/earning/supplement",
                )
            )

    if work.absence_deduction_monthly != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"absence_deduction_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"absence_deduction_{yymm}",
                pay_item_kind="absence_deduction",
                account=AccountKind.EMPLOYEE_DEDUCTIONS,
                amount=work.absence_deduction_monthly,
                source_item_id=f"absence_deduction_{yymm}",
                policy_decision_id="it/deduction/absence",
            )
        )

    if work.bonus_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"bonus_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"bonus_{yymm}",
                pay_item_kind="bonus",
                account=AccountKind.CASH_EARNINGS,
                amount=work.bonus_annual,
                source_item_id=f"bonus_{yymm}",
                policy_decision_id="it/earning/variable",
            )
        )

    if work.fringe_benefit_taxable_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"fringe_benefit_taxable_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"fringe_benefit_taxable_{yymm}",
                pay_item_kind="fringe_benefit_taxable",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=work.fringe_benefit_taxable_annual,
                source_item_id=f"fringe_benefit_taxable_{yymm}",
                policy_decision_id="it/benefit/fringe",
            )
        )

    if work.welfare_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"welfare_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"welfare_{yymm}",
                pay_item_kind="welfare",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=work.welfare_annual,
                source_item_id=f"welfare_{yymm}",
                policy_decision_id="it/benefit/welfare",
            )
        )
