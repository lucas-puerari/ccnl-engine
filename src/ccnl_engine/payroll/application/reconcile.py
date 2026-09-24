"""Reconciliation invariants for PeriodCalculationResult.

Each invariant is a pure function that accepts a result (and, where needed,
the opening :class:`~ccnl_engine.payroll.domain.period.PeriodState`) and
returns a list of :class:`ReconciliationViolation` instances.

:func:`reconcile` runs all invariants and returns a :class:`ReconciliationResult`.

Invariants:
    I1  — every PayItem has at least one matching LedgerEntry.
    I2  — no pay_item_id posts to both CASH_EARNINGS and EMPLOYEE_CONTRIBUTIONS.
    I9  — net identity: CASH_EARNINGS + CREDITS + TFR_SETTLEMENT
          - EMPLOYEE_CONTRIBUTIONS - BILATERAL_FUND_EMPLOYEE
          - EMPLOYEE_DEDUCTIONS - SUBSTITUTE_TAX
          - ORDINARY_TAX - SURTAX - SEPARATE_TAX
          = period_net.
    I10 — IRPEF delta: closing.irpef_withheld_ytd - opening.irpef_withheld_ytd
          = ORDINARY_TAX total - IRPEF_REFUND (tax_refund_item in CREDITS).
    I11 — YTD state transition: months_closed, gross_ytd, and inps_employee_ytd
          advance correctly from opening.
    I12 — employer cost identity: CASH_EARNINGS + NON_CASH_BENEFITS
          + EMPLOYER_CONTRIBUTIONS + BILATERAL_FUND_EMPLOYER
          + TFR_ACCRUAL = period_employer_cost.
    I13 — gross identity: CASH_EARNINGS total = period_gross.
    I14 — all ledger entry IDs in a period are unique.
    I15 — period_gross is non-negative.
    I16 — 0 <= closing.credit_recovered_ytd <= closing.credit_recognized_ytd.
    I17 — every EMPLOYEE_DEDUCTIONS ledger entry has a non-negative amount.
          Refunds and adjustments must use an explicit account, not a negative
          deduction.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.ledger import AccountKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import (
        PeriodCalculationResult,
        PeriodState,
    )

__all__ = [
    "ReconciliationResult",
    "ReconciliationViolation",
    "reconcile",
]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class ReconciliationViolation:
    """One failed invariant check.

    Attributes:
        invariant_id: Short label identifying which invariant failed (e.g. ``"I9"``).
        message: Human-readable description of the failure.
        expected: The value the invariant expected, when applicable.
        actual: The value that was observed, when applicable.
    """

    invariant_id: str
    message: str
    expected: Decimal | None = None
    actual: Decimal | None = None


@dataclass(frozen=True)
class ReconciliationResult:
    """Outcome of running all reconciliation invariants on one result.

    Attributes:
        violations: Tuple of :class:`ReconciliationViolation` instances,
            empty when every invariant passes.
    """

    violations: tuple[ReconciliationViolation, ...]

    @property
    def ok(self) -> bool:
        """``True`` when no invariant was violated.

        Returns:
            ``True`` if :attr:`violations` is empty.
        """
        return len(self.violations) == 0


def _sum_account(
    result: PeriodCalculationResult,
    account: AccountKind,
) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total amount for ``account`` in ``result.ledger_entries``, or zero
        when no entries for that account are present.
    """
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        _ZERO,
    )


def _check_i1(
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


def _check_i2(
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


def _check_i9(
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


def _check_i10(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I10: IRPEF delta equals net IRPEF movement in the ledger.

    Net IRPEF = ORDINARY_TAX (positive withholding) minus IRPEF refunds
    (tax_refund_item entries in CREDITS, posted when ordinary_tax < 0).

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


def _check_i11(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I11: closing state correctly advances from opening.

    Returns:
        Violations for any YTD field that does not advance as expected.
    """
    violations: list[ReconciliationViolation] = []
    if result.closing_state.months_closed != opening.months_closed + 1:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="months_closed not incremented by 1",
                expected=Decimal(opening.months_closed + 1),
                actual=Decimal(result.closing_state.months_closed),
            )
        )
    expected_gross = opening.gross_ytd + _sum_account(result, AccountKind.CASH_EARNINGS)
    if result.closing_state.gross_ytd != expected_gross:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="gross_ytd not correctly accumulated from ledger",
                expected=expected_gross,
                actual=result.closing_state.gross_ytd,
            )
        )
    expected_inps = opening.inps_employee_ytd + _sum_account(
        result, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    if result.closing_state.inps_employee_ytd != expected_inps:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="inps_employee_ytd not correctly accumulated from ledger",
                expected=expected_inps,
                actual=result.closing_state.inps_employee_ytd,
            )
        )
    return violations


def _check_i12(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I12: employer cost identity.

    CASH_EARNINGS + NON_CASH_BENEFITS + EMPLOYER_CONTRIBUTIONS
    + BILATERAL_FUND_EMPLOYER + TFR_ACCRUAL = period_employer_cost.

    Returns:
        A violation when the derived employer cost diverges from
        ``period_employer_cost``.
    """
    cash = _sum_account(result, AccountKind.CASH_EARNINGS)
    ncb = _sum_account(result, AccountKind.NON_CASH_BENEFITS)
    employer = _sum_account(result, AccountKind.EMPLOYER_CONTRIBUTIONS)
    bilateral_er = _sum_account(result, AccountKind.BILATERAL_FUND_EMPLOYER)
    tfr = _sum_account(result, AccountKind.TFR_ACCRUAL)
    derived = cash + ncb + employer + bilateral_er + tfr
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


def _check_i13(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I13: period_gross equals the CASH_EARNINGS ledger total.

    Returns:
        A violation when the CASH_EARNINGS total diverges from
        ``period_gross``.
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


def _check_i14(
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


def _check_i15(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I15: period_gross is non-negative.

    A negative gross indicates that event deductions exceed the period salary,
    which is never valid in isolation (net-zero or refund runs must use
    explicit adjustment events).

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


def _check_i16(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I16: credit_recovered_ytd is between zero and credit_recognized_ytd.

    The cumulative trattamento integrativo recovered from the worker can never
    exceed the cumulative amount that was recognized. Violating this invariant
    means the worker has been charged back more than they ever received.

    Returns:
        A violation when the constraint is breached.
    """
    recovered = result.closing_state.credit_recovered_ytd
    recognized = result.closing_state.credit_recognized_ytd
    if recovered < _ZERO or recovered > recognized:
        return [
            ReconciliationViolation(
                invariant_id="I16",
                message=(
                    "credit_recovered_ytd outside [0, credit_recognized_ytd]: "
                    f"recovered={recovered}, recognized={recognized}"
                ),
                expected=recognized,
                actual=recovered,
            )
        ]
    return []


def _check_i17(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I17: every EMPLOYEE_DEDUCTIONS entry has a non-negative amount.

    Refunds and reversals must use an explicit account (e.g. CREDITS).
    A negative deduction would be *added* to the net instead of subtracted,
    silently inflating the worker's pay.

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


def reconcile(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> ReconciliationResult:
    """Run all reconciliation invariants on *result* and return findings.

    Args:
        result: The completed period calculation result to verify.
        opening: The YTD state that was passed into the calculation,
            used by invariants I10 and I11.

    Returns:
        A :class:`ReconciliationResult` whose :attr:`~ReconciliationResult.ok`
        property is ``True`` when every invariant passes.
    """
    violations: list[ReconciliationViolation] = []
    violations.extend(_check_i1(result))
    violations.extend(_check_i2(result))
    violations.extend(_check_i9(result))
    violations.extend(_check_i10(result, opening))
    violations.extend(_check_i11(result, opening))
    violations.extend(_check_i12(result))
    violations.extend(_check_i13(result))
    violations.extend(_check_i14(result))
    violations.extend(_check_i15(result))
    violations.extend(_check_i16(result))
    violations.extend(_check_i17(result))
    return ReconciliationResult(violations=tuple(violations))
