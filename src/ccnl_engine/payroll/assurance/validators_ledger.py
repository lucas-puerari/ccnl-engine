"""Ledger-balance reconciliation invariants.

These invariants verify that ledger entries are internally consistent and
that the computed scalar outputs (period_gross, period_net, period_employer_cost)
can be derived from the ledger totals.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.types import (
    InvariantCode,
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.ledger.models_remittance import POST_CONGUAGLIO_WITHHOLDING

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult
    from ccnl_engine.payroll.state.models import PeriodState

_ZERO = Decimal(0)


def check_pay_item_posted(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that every PayItem has at least one matching LedgerEntry.

    Returns:
        Violations for any PayItem whose ``item_id`` has no ledger entry.
    """
    item_ids = {item.item_id for item in result.pay_items}
    posted_ids = {e.pay_item_id for e in result.ledger_entries}
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.PAY_ITEM_POSTED,
            message=f"PayItem '{item_id}' has no ledger entry",
        )
        for item_id in sorted(item_ids - posted_ids)
    ]


def check_earning_contribution_exclusive(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that no item posts to both CASH_EARNINGS and EMPLOYEE_CONTRIBUTIONS.

    Returns:
        Violations for any item_id appearing in both conflicting accounts.
    """
    gross_ids = {
        e.pay_item_id
        for e in result.ledger_entries
        if e.account == AccountKind.CASH_EARNINGS
    }
    deduction_ids = {
        e.pay_item_id
        for e in result.ledger_entries
        if e.account == AccountKind.EMPLOYEE_CONTRIBUTIONS
    }
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.EARNING_CONTRIBUTION_EXCLUSIVE,
            message=(
                f"Item '{item_id}' posts to both CASH_EARNINGS "
                "and EMPLOYEE_CONTRIBUTIONS"
            ),
        )
        for item_id in sorted(gross_ids & deduction_ids)
    ]


def check_net_identity(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check the net identity.

    CASH_EARNINGS + CREDITS + TAX_REFUNDS + SURTAX_REFUNDS
    + CREDIT_RECOVERY_SHORTFALL + TFR_SETTLEMENT
    - CREDIT_RECOVERIES - EMPLOYEE_CONTRIBUTIONS
    - BILATERAL_FUND_EMPLOYEE - PENSION_FUND_EMPLOYEE
    - EMPLOYEE_DEDUCTIONS - SUBSTITUTE_TAX
    - ORDINARY_TAX - SURTAX - SEPARATE_TAX
    = period_net.

    Returns:
        A single violation when the derived net diverges from ``period_net``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    period_credits = (
        _sum_account(result, AccountKind.CREDITS)
        + _sum_account(result, AccountKind.TAX_REFUNDS)
        + _sum_account(result, AccountKind.SURTAX_REFUNDS)
        + _sum_account(result, AccountKind.CREDIT_RECOVERY_SHORTFALL)
        - _sum_account(result, AccountKind.CREDIT_RECOVERIES)
    )
    tfr_settle = _sum_account(result, AccountKind.TFR_SETTLEMENT)
    contributions = _sum_account(result, AccountKind.EMPLOYEE_CONTRIBUTIONS)
    bilateral_emp = _sum_account(result, AccountKind.BILATERAL_FUND_EMPLOYEE)
    pension_emp = _sum_account(result, AccountKind.PENSION_FUND_EMPLOYEE)
    emp_deductions = _sum_account(result, AccountKind.EMPLOYEE_DEDUCTIONS)
    sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
    taxes = _sum_account(result, AccountKind.ORDINARY_TAX)
    surtax = _sum_account(result, AccountKind.SURTAX)
    sep_tax = _sum_account(result, AccountKind.SEPARATE_TAX)
    derived = (
        cash
        + period_credits
        + tfr_settle
        - contributions
        - bilateral_emp
        - pension_emp
        - emp_deductions
        - sub_tax
        - taxes
        - surtax
        - sep_tax
    )
    if derived != result.period_net:
        return [
            ReconciliationViolation(
                invariant_id=InvariantCode.NET_IDENTITY,
                message="Net identity violated: ledger-derived net != period_net",
                expected=result.period_net,
                actual=derived,
            )
        ]
    return []


def check_irpef_withheld_continuity(
    result: PeriodResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that IRPEF withheld YTD advances by the net IRPEF of the ledger.

    The IRPEF of an earlier conguaglio deferred on written request (coded
    1066) is withheld on the run but belongs to the earlier year, so it is
    left out.

    Returns:
        A violation when the closing-minus-opening IRPEF delta diverges from
        ``ORDINARY_TAX`` less ``TAX_REFUNDS``.
    """
    delta = result.closing_state.cash.tax.irpef - opening.cash.tax.irpef
    deferred = sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
            and e.remittance_code == POST_CONGUAGLIO_WITHHOLDING
        ),
        _ZERO,
    )
    net_withholding = (
        _sum_account(result, AccountKind.ORDINARY_TAX)
        - deferred
        - _sum_account(result, AccountKind.TAX_REFUNDS)
    )
    if delta != net_withholding:
        return [
            ReconciliationViolation(
                invariant_id=InvariantCode.IRPEF_WITHHELD_CONTINUITY,
                message="IRPEF delta != net ORDINARY_TAX",
                expected=net_withholding,
                actual=delta,
            )
        ]
    return []


def check_employer_cost_identity(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check the employer cost identity.

    CASH_EARNINGS - EMPLOYEE_DEDUCTIONS + NON_CASH_BENEFITS
    + EMPLOYER_CONTRIBUTIONS + BILATERAL_FUND_EMPLOYER
    + TFR_ACCRUAL + PENSION_FUND_EMPLOYER + PENSION_FUND_TFR
    + TFR_TREASURY_FUND = period_employer_cost.

    Returns:
        A violation when the derived employer cost diverges from
        ``period_employer_cost``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    deductions = _sum_account(result, AccountKind.EMPLOYEE_DEDUCTIONS)
    ncb = _sum_account(result, AccountKind.NON_CASH_BENEFITS)
    employer = _sum_account(result, AccountKind.EMPLOYER_CONTRIBUTIONS)
    bilateral_er = _sum_account(result, AccountKind.BILATERAL_FUND_EMPLOYER)
    tfr = _sum_account(result, AccountKind.TFR_ACCRUAL) + _sum_account(
        result, AccountKind.TFR_TREASURY_FUND
    )
    pension = _sum_account(result, AccountKind.PENSION_FUND_EMPLOYER) + _sum_account(
        result, AccountKind.PENSION_FUND_TFR
    )
    derived = cash - deductions + ncb + employer + bilateral_er + tfr + pension
    if derived != result.period_employer_cost:
        return [
            ReconciliationViolation(
                invariant_id=InvariantCode.EMPLOYER_COST_IDENTITY,
                message="Employer cost identity violated",
                expected=result.period_employer_cost,
                actual=derived,
            )
        ]
    return []


def check_gross_identity(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that period_gross equals the CASH_EARNINGS ledger total.

    Returns:
        A violation when the CASH_EARNINGS total diverges from ``period_gross``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    if cash != result.period_gross:
        return [
            ReconciliationViolation(
                invariant_id=InvariantCode.GROSS_IDENTITY,
                message="period_gross != CASH_EARNINGS ledger total",
                expected=result.period_gross,
                actual=cash,
            )
        ]
    return []


def check_ledger_entry_unique(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that all ledger entry IDs within a period are unique.

    Returns:
        One violation per duplicate entry ID detected.
    """
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in result.ledger_entries:
        if entry.entry_id in seen:
            duplicates.append(entry.entry_id)
        else:
            seen.add(entry.entry_id)
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.LEDGER_ENTRY_UNIQUE,
            message=f"Duplicate ledger entry ID: {eid!r}",
        )
        for eid in duplicates
    ]
