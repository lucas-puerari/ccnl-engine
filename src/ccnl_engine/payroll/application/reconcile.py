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
    I10 — IRPEF delta: closing.tax.irpef - opening.tax.irpef
          = ORDINARY_TAX total - IRPEF_REFUND (tax_refund_item in CREDITS).
    I11 — YTD state transition: regular_periods_closed, tax_withholding_periods_closed,
          closed_run_ids, earnings.gross, and earnings.inps_employee advance correctly
          from opening.
    I12 — employer cost identity: CASH_EARNINGS - EMPLOYEE_DEDUCTIONS
          + NON_CASH_BENEFITS + EMPLOYER_CONTRIBUTIONS
          + BILATERAL_FUND_EMPLOYER + TFR_ACCRUAL = period_employer_cost.
    I13 — gross identity: CASH_EARNINGS total = period_gross.
    I14 — all ledger entry IDs in a period are unique.
    I15 — period_gross is non-negative.
    I16 — 0 <= closing.trattamento.recovered <= closing.trattamento.recognized.
    I17 — every EMPLOYEE_DEDUCTIONS ledger entry has a non-negative amount.
          Refunds and adjustments must use an explicit account, not a negative
          deduction.
    I18: closing.work_time_regime.used = opening used + eligible amounts of
         the capped regime decisions, and does not exceed the annual cap.

Legal invariants (L1 to L4, see ``legal_invariants``) reject negative
substitute tax, ordinary tax, employee contributions and employer
contributions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import ReconciliationViolation
from ccnl_engine.payroll.application.ledger_invariants import (
    check_i1,
    check_i2,
    check_i9,
    check_i10,
    check_i12,
    check_i13,
    check_i14,
    check_i15,
    check_i17,
)
from ccnl_engine.payroll.application.legal_invariants import check_legal
from ccnl_engine.payroll.application.state_invariants import (
    check_i11,
    check_i16,
    check_i18,
)

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
    violations.extend(check_i1(result))
    violations.extend(check_i2(result))
    violations.extend(check_i9(result))
    violations.extend(check_i10(result, opening))
    violations.extend(check_i11(result, opening))
    violations.extend(check_i12(result))
    violations.extend(check_i13(result))
    violations.extend(check_i14(result))
    violations.extend(check_i15(result))
    violations.extend(check_i16(result))
    violations.extend(check_i17(result))
    violations.extend(check_i18(result, opening))
    violations.extend(check_legal(result, opening))
    return ReconciliationResult(violations=tuple(violations))
