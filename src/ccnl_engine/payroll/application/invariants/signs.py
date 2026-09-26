"""Sign invariants: amounts that a payslip never carries as negative.

These checks are distinct from the accounting identities of
``ledger_invariants``: an identity can hold while a component has the wrong
sign.

Implemented invariants:
    gross_non_negative: ``period_gross >= 0``.
    employee_deduction_non_negative: every EMPLOYEE_DEDUCTIONS entry is
        ``>= 0``; refunds and adjustments use an explicit account.
    substitute_tax_non_negative: every SUBSTITUTE_TAX entry is ``>= 0``;
        refunds are posted to CREDITS, never as negative substitute tax.
    ordinary_tax_non_negative: every ORDINARY_TAX entry is ``>= 0``; an
        IRPEF refund uses the CREDITS account (``tax_refund_item`` policy).
    employee_contribution_non_negative and
    employer_contribution_non_negative: every EMPLOYEE_CONTRIBUTIONS and
        EMPLOYER_CONTRIBUTIONS entry is ``>= 0``; a correction of past
        contributions is a distinct movement, not a negative contribution.
    net_pay_non_negative: ``period_net >= 0``.  A run whose unpaid absences
        leave less pay than the withholdings due is rejected as invalid
        input before reconciliation, so a negative net reaching this check
        is an engine error.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.invariants._types import (
    InvariantCode,
    ReconciliationViolation,
)
from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__: list[str] = []

_ZERO = Decimal(0)

#: Accounts whose every entry must be non-negative, with the invariant code.
_NON_NEGATIVE_ACCOUNTS: tuple[tuple[AccountKind, InvariantCode], ...] = (
    (AccountKind.EMPLOYEE_DEDUCTIONS, InvariantCode.EMPLOYEE_DEDUCTION_NON_NEGATIVE),
    (AccountKind.SUBSTITUTE_TAX, InvariantCode.SUBSTITUTE_TAX_NON_NEGATIVE),
    (AccountKind.ORDINARY_TAX, InvariantCode.ORDINARY_TAX_NON_NEGATIVE),
    (
        AccountKind.EMPLOYEE_CONTRIBUTIONS,
        InvariantCode.EMPLOYEE_CONTRIBUTION_NON_NEGATIVE,
    ),
    (
        AccountKind.EMPLOYER_CONTRIBUTIONS,
        InvariantCode.EMPLOYER_CONTRIBUTION_NON_NEGATIVE,
    ),
)


def check_account_non_negative(
    result: PeriodResult,
    account: AccountKind,
    code: InvariantCode,
) -> list[ReconciliationViolation]:
    """Check that every entry of ``account`` has a non-negative amount.

    Returns:
        One violation, coded ``code``, per entry posting a negative amount.
    """
    return [
        ReconciliationViolation(
            invariant_id=code,
            message=(
                f"LedgerEntry '{e.pay_item_id}' posts a negative amount "
                f"{e.amount} to {account.value}"
            ),
            expected=_ZERO,
            actual=e.amount,
        )
        for e in result.ledger_entries
        if e.account == account and e.amount < _ZERO
    ]


def _check_non_negative_total(
    value: Decimal, code: InvariantCode, name: str
) -> list[ReconciliationViolation]:
    """Return a violation when the result total ``value`` is negative.

    Returns:
        A single violation coded ``code`` when ``value < 0``.
    """
    if value >= _ZERO:
        return []
    return [
        ReconciliationViolation(
            invariant_id=code,
            message=f"{name} is negative",
            expected=_ZERO,
            actual=value,
        )
    ]


def check_signs(result: PeriodResult) -> list[ReconciliationViolation]:
    """Run every sign invariant against ``result``.

    Returns:
        List of :class:`ReconciliationViolation` instances, empty when all pass.
    """
    violations = _check_non_negative_total(
        result.period_gross, InvariantCode.GROSS_NON_NEGATIVE, "period_gross"
    )
    for account, code in _NON_NEGATIVE_ACCOUNTS:
        violations.extend(check_account_non_negative(result, account, code))
    violations.extend(
        _check_non_negative_total(
            result.period_net, InvariantCode.NET_PAY_NON_NEGATIVE, "period_net"
        )
    )
    return violations
