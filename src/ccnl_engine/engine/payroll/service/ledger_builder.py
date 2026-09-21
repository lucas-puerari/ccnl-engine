"""Post contractual pay components to the Ledger as LedgerEntry records."""

from __future__ import annotations

import calendar
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay

_ZERO = Decimal(0)


def _last_day(as_of: date) -> date:
    """Return the last calendar day of the month containing *as_of*.

    Returns:
        A :class:`~datetime.date` for the final day of that month.
    """
    import datetime  # noqa: PLC0415

    last = calendar.monthrange(as_of.year, as_of.month)[1]
    return datetime.date(as_of.year, as_of.month, last)


def post_earnings(gross: GrossPay, as_of: date, ledger: Ledger) -> None:
    """Post base salary, seniority and fixed allowances as CASH_EARNINGS entries.

    Entries with a zero amount are silently skipped.  All entries are posted to
    :attr:`~ccnl_engine.engine.payroll.domain.ledger.AccountKind.CASH_EARNINGS`.

    Args:
        gross: The resolved gross-pay components.
        as_of: The competence date used to derive the year/month for the entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"
    payment = _last_day(as_of)

    if gross.chain.base != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"base_salary_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"base_salary_{yymm}",
                pay_item_kind="base_salary_earning",
                account=AccountKind.CASH_EARNINGS,
                amount=gross.chain.base,
                source_item_id=f"base_salary_{yymm}",
                policy_decision_id="it/earning/ordinary",
            )
        )

    if gross.chain.seniority != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"seniority_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"seniority_{yymm}",
                pay_item_kind="seniority_earning",
                account=AccountKind.CASH_EARNINGS,
                amount=gross.chain.seniority,
                source_item_id=f"seniority_{yymm}",
                policy_decision_id="it/earning/ordinary",
                note=f"count={gross.count}",
            )
        )

    for allowance, amount in gross.chain.allowances:
        if amount == _ZERO:
            continue
        ledger.append(
            LedgerEntry(
                entry_id=f"allowance_{allowance.code}_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"allowance_{allowance.code}_{yymm}",
                pay_item_kind="fixed_allowance_earning",
                account=AccountKind.CASH_EARNINGS,
                amount=amount,
                source_item_id=f"allowance_{allowance.code}_{yymm}",
                policy_decision_id="it/earning/ordinary",
                note=allowance.code,
            )
        )


def post_contributions_and_taxes(
    fiscal: FiscalPay, as_of: date, ledger: Ledger
) -> None:
    """Post INPS contributions and IRPEF as ledger entries.

    Posts employee INPS to EMPLOYEE_CONTRIBUTIONS, employer INPS and INAIL to
    EMPLOYER_CONTRIBUTIONS, and net IRPEF to ORDINARY_TAX.  Zero-amount entries
    are silently skipped.

    Args:
        fiscal: The resolved fiscal-pay components.
        as_of: The competence date used to derive the year/month for the entries.
        ledger: The ledger to append to.
    """
    period = CompetencePeriod(year=as_of.year, month=as_of.month)
    yymm = f"{period.year}_{period.month:02d}"
    payment = _last_day(as_of)

    if fiscal.inps_employee_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"inps_employee_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"inps_employee_{yymm}",
                pay_item_kind="inps_employee_contribution",
                account=AccountKind.EMPLOYEE_CONTRIBUTIONS,
                amount=fiscal.inps_employee_annual,
                source_item_id=f"inps_employee_{yymm}",
                policy_decision_id="it/contribution/employee",
            )
        )

    if fiscal.inps_employer_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"inps_employer_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"inps_employer_{yymm}",
                pay_item_kind="inps_employer_contribution",
                account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                amount=fiscal.inps_employer_annual,
                source_item_id=f"inps_employer_{yymm}",
                policy_decision_id="it/contribution/employer",
            )
        )

    if fiscal.inail_employer_annual != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"inail_employer_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"inail_employer_{yymm}",
                pay_item_kind="inail_employer_contribution",
                account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                amount=fiscal.inail_employer_annual,
                source_item_id=f"inail_employer_{yymm}",
                policy_decision_id="it/contribution/employer",
            )
        )

    if fiscal.irpef_net != _ZERO:
        ledger.append(
            LedgerEntry(
                entry_id=f"irpef_{yymm}",
                competence_period=period,
                payment_date=payment,
                pay_item_id=f"irpef_{yymm}",
                pay_item_kind="irpef",
                account=AccountKind.ORDINARY_TAX,
                amount=fiscal.irpef_net,
                source_item_id=f"irpef_{yymm}",
            )
        )


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
