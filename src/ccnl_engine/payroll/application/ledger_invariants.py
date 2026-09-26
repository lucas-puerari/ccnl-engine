"""Ledger-balance reconciliation invariants.

These invariants verify that ledger entries are internally consistent and
that the computed scalar outputs (period_gross, period_net, period_employer_cost)
can be derived from the ledger totals.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import (
    InvariantCode,
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState

_ZERO = Decimal(0)


def check_pay_item_posted(
    result: PeriodCalculationResult,
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
    result: PeriodCalculationResult,
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
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """Check the net identity.

    CASH_EARNINGS + CREDITS + TFR_SETTLEMENT
    - EMPLOYEE_CONTRIBUTIONS - BILATERAL_FUND_EMPLOYEE
    - EMPLOYEE_DEDUCTIONS - SUBSTITUTE_TAX
    - ORDINARY_TAX - SURTAX - SEPARATE_TAX
    = period_net.

    Returns:
        A single violation when the derived net diverges from ``period_net``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    period_credits = _sum_account(result, AccountKind.CREDITS)
    tfr_settle = _sum_account(result, AccountKind.TFR_SETTLEMENT)
    contributions = _sum_account(result, AccountKind.EMPLOYEE_CONTRIBUTIONS)
    bilateral_emp = _sum_account(result, AccountKind.BILATERAL_FUND_EMPLOYEE)
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
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that IRPEF withheld YTD advances by the net IRPEF of the ledger.

    Returns:
        A violation when the closing-minus-opening IRPEF delta diverges from
        the net IRPEF ledger movement.
    """
    delta = result.closing_state.ytd.tax.irpef - opening.ytd.tax.irpef
    ordinary_tax = _sum_account(result, AccountKind.ORDINARY_TAX)
    irpef_refund = sum(
        e.amount
        for e in result.ledger_entries
        if e.account == AccountKind.CREDITS and e.pay_item_kind == "tax_refund_item"
    )
    net_withholding = ordinary_tax - irpef_refund
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
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """Check the employer cost identity.

    CASH_EARNINGS - EMPLOYEE_DEDUCTIONS + NON_CASH_BENEFITS
    + EMPLOYER_CONTRIBUTIONS + BILATERAL_FUND_EMPLOYER
    + TFR_ACCRUAL = period_employer_cost.

    Returns:
        A violation when the derived employer cost diverges from
        ``period_employer_cost``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    deductions = _sum_account(result, AccountKind.EMPLOYEE_DEDUCTIONS)
    ncb = _sum_account(result, AccountKind.NON_CASH_BENEFITS)
    employer = _sum_account(result, AccountKind.EMPLOYER_CONTRIBUTIONS)
    bilateral_er = _sum_account(result, AccountKind.BILATERAL_FUND_EMPLOYER)
    tfr = _sum_account(result, AccountKind.TFR_ACCRUAL)
    derived = cash - deductions + ncb + employer + bilateral_er + tfr
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
    result: PeriodCalculationResult,
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
    result: PeriodCalculationResult,
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
