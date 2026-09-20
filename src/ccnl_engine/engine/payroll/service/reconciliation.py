"""ReconciliationService: verify accounting invariants on a Ledger.

Each invariant maps to a static method named _check_I<N>_*.  Methods return
a list of :class:`ReconciliationViolation`; an empty list means the invariant
holds.  :meth:`check` collects all violations and raises
:class:`ReconciliationError` when any are found.

Invariants I1-I2 and I10-I13 require information not yet present in the
ledger (PayItem provenance, YTD state, period aggregation).  They are kept
as explicit stubs so future contributors can fill them in incrementally.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.reconciliation import (
    ReconciliationError,
    ReconciliationViolation,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.ledger import Ledger

_ZERO = Decimal(0)
_ABSENCE_KIND = "absence_deduction"


class ReconciliationService:
    """Check that a Ledger satisfies the accounting invariants."""

    def check(self, ledger: Ledger) -> None:
        """Run all invariants and raise on violation.

        Args:
            ledger: The ledger produced by a payroll computation.

        Raises:
            ReconciliationError: When at least one invariant is violated.
        """
        violations: list[ReconciliationViolation] = []
        violations.extend(self._check_i3_non_empty_kind(ledger))
        violations.extend(self._check_i4_no_zero_amount(ledger))
        violations.extend(self._check_i5_gross_earnings_sign(ledger))
        violations.extend(self._check_i6_contributions_positive(ledger))
        violations.extend(self._check_i7_gross_sum_non_negative(ledger))
        violations.extend(self._check_i8_no_duplicate_entry_ids(ledger))
        violations.extend(self._check_i9_net_pay_non_negative(ledger))
        violations.extend(self._check_i14_tfr_non_negative(ledger))
        if violations:
            raise ReconciliationError(violations)

    # ------------------------------------------------------------------
    # Checkable invariants
    # ------------------------------------------------------------------

    @staticmethod
    def _check_i3_non_empty_kind(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I3: every movement carries a non-empty pay_item_kind.

        Returns:
            List of violations; empty when the invariant holds.
        """
        return [
            ReconciliationViolation(
                code="I3",
                message=f"entry {e.entry_id!r} has empty pay_item_kind",
            )
            for e in ledger
            if not e.pay_item_kind
        ]

    @staticmethod
    def _check_i4_no_zero_amount(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I4: no entry has a zero amount (skipped upstream).

        Returns:
            List of violations; empty when the invariant holds.
        """
        return [
            ReconciliationViolation(
                code="I4",
                message=(f"entry {e.entry_id!r} ({e.pay_item_kind}) has zero amount"),
            )
            for e in ledger
            if e.amount == _ZERO
        ]

    @staticmethod
    def _check_i5_gross_earnings_sign(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I5: GROSS_EARNINGS positive; absence_deduction negative.

        Returns:
            List of violations; empty when the invariant holds.
        """
        violations = []
        for e in ledger:
            if e.account != AccountKind.GROSS_EARNINGS:
                continue
            if e.pay_item_kind == _ABSENCE_KIND:
                if e.amount > _ZERO:
                    violations.append(
                        ReconciliationViolation(
                            code="I5",
                            message=(
                                f"absence_deduction entry {e.entry_id!r} "
                                f"has positive amount {e.amount}"
                            ),
                        )
                    )
            elif e.amount < _ZERO:
                violations.append(
                    ReconciliationViolation(
                        code="I5",
                        message=(
                            f"GROSS_EARNINGS entry {e.entry_id!r} "
                            f"({e.pay_item_kind}) has negative amount"
                            f" {e.amount}"
                        ),
                    )
                )
        return violations

    @staticmethod
    def _check_i6_contributions_positive(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I6: EMPLOYEE_CONTRIBUTIONS and EMPLOYER_CONTRIBUTIONS are positive.

        Returns:
            List of violations; empty when the invariant holds.
        """
        contrib_accounts = {
            AccountKind.EMPLOYEE_CONTRIBUTIONS,
            AccountKind.EMPLOYER_CONTRIBUTIONS,
        }
        return [
            ReconciliationViolation(
                code="I6",
                message=(
                    f"contribution entry {e.entry_id!r} ({e.pay_item_kind}) "
                    f"has non-positive amount {e.amount}"
                ),
            )
            for e in ledger
            if e.account in contrib_accounts and e.amount <= _ZERO
        ]

    @staticmethod
    def _check_i7_gross_sum_non_negative(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I7: net sum of GROSS_EARNINGS entries must be non-negative.

        Returns:
            List of violations; empty when the invariant holds.
        """
        gross_sum = sum(
            (e.amount for e in ledger if e.account == AccountKind.GROSS_EARNINGS),
            _ZERO,
        )
        if gross_sum < _ZERO:
            return [
                ReconciliationViolation(
                    code="I7",
                    message=(
                        f"net GROSS_EARNINGS sum is {gross_sum}; must be non-negative"
                    ),
                )
            ]
        return []

    @staticmethod
    def _check_i8_no_duplicate_entry_ids(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I8: each entry_id is unique within the ledger.

        Returns:
            List of violations; empty when the invariant holds.
        """
        seen: set[str] = set()
        duplicates: set[str] = set()
        for e in ledger:
            if e.entry_id in seen:
                duplicates.add(e.entry_id)
            seen.add(e.entry_id)
        return [
            ReconciliationViolation(
                code="I8",
                message=f"duplicate entry_id {eid!r}",
            )
            for eid in sorted(duplicates)
        ]

    @staticmethod
    def _check_i9_net_pay_non_negative(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I9: NET_PAY entries are non-negative.

        Returns:
            List of violations; empty when the invariant holds.
        """
        return [
            ReconciliationViolation(
                code="I9",
                message=(
                    f"NET_PAY entry {e.entry_id!r} ({e.pay_item_kind}) "
                    f"has negative amount {e.amount}"
                ),
            )
            for e in ledger
            if e.account == AccountKind.NET_PAY and e.amount < _ZERO
        ]

    @staticmethod
    def _check_i14_tfr_non_negative(
        ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I14: TFR_ACCRUAL entries are non-negative.

        Returns:
            List of violations; empty when the invariant holds.
        """
        return [
            ReconciliationViolation(
                code="I14",
                message=(
                    f"TFR_ACCRUAL entry {e.entry_id!r} ({e.pay_item_kind}) "
                    f"has negative amount {e.amount}"
                ),
            )
            for e in ledger
            if e.account == AccountKind.TFR_ACCRUAL and e.amount < _ZERO
        ]

    # ------------------------------------------------------------------
    # Stubs for invariants requiring future infrastructure
    # ------------------------------------------------------------------

    @staticmethod
    def _check_i1_payitem_coverage(
        _ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I1: every PayItem produces a movement or blocking limitation.

        Not yet verifiable: PayItem provenance is not tracked in the ledger.

        Returns:
            Empty list; stub.
        """
        return []

    @staticmethod
    def _check_i2_no_double_treatment(
        _ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I2: no item is consumed twice by the same treatment.

        Not yet verifiable: treatment identity is not tracked in LedgerEntry.

        Returns:
            Empty list; stub.
        """
        return []

    @staticmethod
    def _check_i10_conguaglio_source(
        _ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I10: prior withholdings affect conguaglio, not annual tax debt.

        Not yet verifiable: prior-period withholdings are not in the ledger.

        Returns:
            Empty list; stub.
        """
        return []

    @staticmethod
    def _check_i11_ytd_state(
        _ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I11: closing YTD state equals opening state plus period movements.

        Not yet verifiable: PayrollState is not implemented.

        Returns:
            Empty list; stub.
        """
        return []

    @staticmethod
    def _check_i12_annual_from_periods(
        _ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I12: annual summary equals aggregation of period ledgers.

        Not yet verifiable: period-level ledgers are not implemented.

        Returns:
            Empty list; stub.
        """
        return []

    @staticmethod
    def _check_i13_single_rounding_point(
        _ledger: Ledger,
    ) -> list[ReconciliationViolation]:
        """I13: rounding occurs once at the point set by policy.

        Not yet verifiable: rounding policy is not tracked in the ledger.

        Returns:
            Empty list; stub.
        """
        return []
