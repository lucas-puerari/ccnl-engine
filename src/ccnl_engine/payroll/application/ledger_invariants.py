"""Ledger-balance reconciliation invariants (I1, I2, I9, I10, I12-I15, I17).

These invariants verify that ledger entries are internally consistent and
that the computed scalar outputs (period_gross, period_net, period_employer_cost)
can be derived from the ledger totals.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import (
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState

_ZERO = Decimal(0)


def check_i1(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I1: every PayItem has at least one matching LedgerEntry.

    Returns:
        Violations for any PayItem whose ``item_id`` has no ledger entry.
    """
    item_ids = {item.item_id for item in result.pay_items}
    posted_ids = {e.pay_item_id for e in result.ledger_entries}
    return [
        ReconciliationViolation(
            invariant_id="I1",
            message=f"PayItem '{item_id}' has no ledger entry",
        )
        for item_id in sorted(item_ids - posted_ids)
    ]


def check_i2(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I2: no pay_item_id posts to both CASH_EARNINGS and EMPLOYEE_CONTRIBUTIONS.

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
            invariant_id="I2",
            message=(
                f"Item '{item_id}' posts to both CASH_EARNINGS "
                "and EMPLOYEE_CONTRIBUTIONS"
            ),
        )
        for item_id in sorted(gross_ids & deduction_ids)
    ]


def check_i9(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I9: net identity.

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
                invariant_id="I9",
                message="Net identity violated: ledger-derived net != period_net",
                expected=result.period_net,
                actual=derived,
            )
        ]
    return []


def check_i10(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I10: IRPEF delta equals net IRPEF movement in the ledger.

    Returns:
        A violation when the closing-minus-opening IRPEF delta diverges from
        the net IRPEF ledger movement.
    """
    delta = result.closing_state.irpef_withheld_ytd - opening.irpef_withheld_ytd
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
                invariant_id="I10",
                message="IRPEF delta != net ORDINARY_TAX",
                expected=net_withholding,
                actual=delta,
            )
        ]
    return []


def check_i12(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I12: employer cost identity.

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
                invariant_id="I12",
                message="Employer cost identity violated",
                expected=result.period_employer_cost,
                actual=derived,
            )
        ]
    return []


def check_i13(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I13: period_gross equals the CASH_EARNINGS ledger total.

    Returns:
        A violation when the CASH_EARNINGS total diverges from ``period_gross``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    if cash != result.period_gross:
        return [
            ReconciliationViolation(
                invariant_id="I13",
                message="period_gross != CASH_EARNINGS ledger total",
                expected=result.period_gross,
                actual=cash,
            )
        ]
    return []


def check_i14(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I14: all ledger entry IDs within a period are unique.

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
            invariant_id="I14",
            message=f"Duplicate ledger entry ID: {eid!r}",
        )
        for eid in duplicates
    ]


def check_i15(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I15: period_gross is non-negative.

    Returns:
        A violation when ``period_gross < 0``.
    """
    if result.period_gross < _ZERO:
        return [
            ReconciliationViolation(
                invariant_id="I15",
                message="period_gross is negative",
                expected=_ZERO,
                actual=result.period_gross,
            )
        ]
    return []


def check_i17(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I17: every EMPLOYEE_DEDUCTIONS entry has a non-negative amount.

    Returns:
        One violation per offending ledger entry.
    """
    return [
        ReconciliationViolation(
            invariant_id="I17",
            message=(
                f"EMPLOYEE_DEDUCTIONS entry {e.entry_id!r} "
                f"has negative amount {e.amount}"
            ),
            expected=_ZERO,
            actual=e.amount,
        )
        for e in result.ledger_entries
        if e.account == AccountKind.EMPLOYEE_DEDUCTIONS and e.amount < _ZERO
    ]
