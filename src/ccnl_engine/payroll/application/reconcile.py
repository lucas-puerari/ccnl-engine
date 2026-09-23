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
          - ORDINARY_TAX - SURTAX - SEPARATE_TAX
          = period_net.
    I10 — IRPEF delta: closing.irpef_withheld_ytd - opening.irpef_withheld_ytd
          = ORDINARY_TAX total.
    I11 — YTD state transition: months_closed, gross_ytd, and inps_employee_ytd
          advance correctly from opening.
    I12 — employer cost identity: CASH_EARNINGS + NON_CASH_BENEFITS
          + EMPLOYER_CONTRIBUTIONS + BILATERAL_FUND_EMPLOYER
          + TFR_ACCRUAL = period_employer_cost.
    I13 — gross identity: CASH_EARNINGS total = period_gross.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind

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
    taxes = _sum_account(result, AccountKind.ORDINARY_TAX)
    surtax = _sum_account(result, AccountKind.SURTAX)
    sep_tax = _sum_account(result, AccountKind.SEPARATE_TAX)
    derived = (
        cash
        + period_credits
        + tfr_settle
        - contributions
        - bilateral_emp
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
    """I10: IRPEF delta equals ORDINARY_TAX ledger total.

    Returns:
        A violation when the closing-minus-opening IRPEF delta diverges from
        the posted ORDINARY_TAX amount.
    """
    delta = result.closing_state.irpef_withheld_ytd - opening.irpef_withheld_ytd
    ordinary_tax = _sum_account(result, AccountKind.ORDINARY_TAX)
    if delta != ordinary_tax:
        return [
            ReconciliationViolation(
                invariant_id="I10",
                message="IRPEF delta != ORDINARY_TAX: conguaglio source unverifiable",
                expected=ordinary_tax,
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
    return ReconciliationResult(violations=tuple(violations))
