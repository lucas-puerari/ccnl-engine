"""Unit tests for ReconciliationService."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.ledger import AccountKind, Ledger, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.engine.payroll.domain.reconciliation import (
    ReconciliationError,
    ReconciliationViolation,
)
from ccnl_engine.engine.payroll.service.reconciliation import ReconciliationService

_PERIOD = CompetencePeriod(year=2026, month=6)
_V = Decimal("100.00")
_ZERO = Decimal(0)


def _entry(
    entry_id: str = "e1",
    pay_item_kind: str = "base_salary_earning",
    account: AccountKind = AccountKind.GROSS_EARNINGS,
    amount: Decimal = _V,
) -> LedgerEntry:
    """Build a minimal LedgerEntry for testing.

    Returns:
        A :class:`LedgerEntry` with the given fields.
    """
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=_PERIOD,
        pay_item_id=entry_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=amount,
    )


def _ledger(*entries: LedgerEntry) -> Ledger:
    """Build a Ledger from entries.

    Returns:
        A :class:`Ledger` containing the given entries.
    """
    ledger = Ledger()
    for e in entries:
        ledger.append(e)
    return ledger


def _check(ledger: Ledger) -> None:
    """Run ReconciliationService.check on ledger."""
    ReconciliationService().check(ledger)


class TestI3NonEmptyKind:
    """I3: every entry must carry a non-empty pay_item_kind."""

    def test_non_empty_kind_passes(self) -> None:
        """Valid entry with non-empty kind passes I3."""
        _check(_ledger(_entry(pay_item_kind="base_salary_earning")))

    def test_empty_kind_raises(self) -> None:
        """Entry with empty pay_item_kind raises ReconciliationError with I3."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(_ledger(_entry(pay_item_kind="")))
        assert any(v.code == "I3" for v in exc_info.value.violations)


class TestI4NoZeroAmount:
    """I4: no entry may have a zero amount."""

    def test_non_zero_amount_passes(self) -> None:
        """Entry with non-zero amount passes I4."""
        _check(_ledger(_entry(amount=_V)))

    def test_zero_amount_raises(self) -> None:
        """Entry with zero amount raises ReconciliationError with I4."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(_ledger(_entry(amount=_ZERO)))
        assert any(v.code == "I4" for v in exc_info.value.violations)


class TestI5GrossEarningsSign:
    """I5: GROSS_EARNINGS must be positive except absence_deduction (negative)."""

    def test_positive_gross_earnings_passes(self) -> None:
        """Positive GROSS_EARNINGS entry passes I5."""
        _check(_ledger(_entry(account=AccountKind.GROSS_EARNINGS, amount=_V)))

    def test_negative_absence_deduction_passes(self) -> None:
        """Negative absence_deduction GROSS_EARNINGS entry passes I5."""
        _check(
            _ledger(
                _entry(pay_item_kind="base_salary_earning", amount=_V),
                _entry(
                    entry_id="e2",
                    pay_item_kind="absence_deduction",
                    account=AccountKind.GROSS_EARNINGS,
                    amount=Decimal("-50.00"),
                ),
            )
        )

    def test_negative_non_absence_gross_raises(self) -> None:
        """Negative non-absence GROSS_EARNINGS entry raises I5."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(
                        pay_item_kind="base_salary_earning",
                        account=AccountKind.GROSS_EARNINGS,
                        amount=Decimal("-10.00"),
                    )
                )
            )
        assert any(v.code == "I5" for v in exc_info.value.violations)

    def test_positive_absence_deduction_raises(self) -> None:
        """Positive absence_deduction entry raises I5 (deductions must be negative)."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(pay_item_kind="base_salary_earning", amount=_V),
                    _entry(
                        entry_id="e2",
                        pay_item_kind="absence_deduction",
                        account=AccountKind.GROSS_EARNINGS,
                        amount=_V,
                    ),
                )
            )
        assert any(v.code == "I5" for v in exc_info.value.violations)


class TestI6ContributionsPositive:
    """I6: EMPLOYEE_CONTRIBUTIONS and EMPLOYER_CONTRIBUTIONS must be positive."""

    def test_positive_employee_contribution_passes(self) -> None:
        """Positive EMPLOYEE_CONTRIBUTIONS entry passes I6."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="c1",
                    pay_item_kind="inps_employee_contribution",
                    account=AccountKind.EMPLOYEE_CONTRIBUTIONS,
                    amount=_V,
                ),
            )
        )

    def test_positive_employer_contribution_passes(self) -> None:
        """Positive EMPLOYER_CONTRIBUTIONS entry passes I6."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="c1",
                    pay_item_kind="inps_employer_contribution",
                    account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                    amount=_V,
                ),
            )
        )

    def test_zero_employee_contribution_raises(self) -> None:
        """Zero EMPLOYEE_CONTRIBUTIONS entry should have been skipped — raises I4+I6."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(),
                    _entry(
                        entry_id="c1",
                        pay_item_kind="inps_employee_contribution",
                        account=AccountKind.EMPLOYEE_CONTRIBUTIONS,
                        amount=_ZERO,
                    ),
                )
            )
        codes = {v.code for v in exc_info.value.violations}
        assert "I6" in codes


class TestI7GrossSumPositive:
    """I7: net sum of all GROSS_EARNINGS entries must be positive."""

    def test_positive_gross_sum_passes(self) -> None:
        """Ledger with net-positive GROSS_EARNINGS passes I7."""
        _check(
            _ledger(
                _entry(amount=Decimal("500.00")),
                _entry(
                    entry_id="e2",
                    pay_item_kind="absence_deduction",
                    account=AccountKind.GROSS_EARNINGS,
                    amount=Decimal("-100.00"),
                ),
            )
        )

    def test_gross_sum_zero_passes(self) -> None:
        """Zero net GROSS_EARNINGS is valid (full-month absence capped)."""
        _check(
            _ledger(
                _entry(amount=_V),
                _entry(
                    entry_id="e2",
                    pay_item_kind="absence_deduction",
                    account=AccountKind.GROSS_EARNINGS,
                    amount=-_V,
                ),
            )
        )

    def test_negative_gross_sum_raises(self) -> None:
        """Negative net GROSS_EARNINGS raises I7."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(amount=_V),
                    _entry(
                        entry_id="e2",
                        pay_item_kind="absence_deduction",
                        account=AccountKind.GROSS_EARNINGS,
                        amount=Decimal("-200.00"),
                    ),
                )
            )
        assert any(v.code == "I7" for v in exc_info.value.violations)


class TestI8NoDuplicateEntryIds:
    """I8: each entry_id is unique within the ledger."""

    def test_unique_ids_pass(self) -> None:
        """Ledger with unique entry IDs passes I8."""
        _check(_ledger(_entry("e1"), _entry("e2")))

    def test_duplicate_id_raises(self) -> None:
        """Duplicate entry_id raises ReconciliationError with I8."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(_ledger(_entry("e1"), _entry("e1")))
        assert any(v.code == "I8" for v in exc_info.value.violations)


class TestI9NetPayNonNegative:
    """I9: NET_PAY entries must be non-negative."""

    def test_positive_net_pay_passes(self) -> None:
        """Positive NET_PAY entry passes I9."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="w1",
                    pay_item_kind="welfare",
                    account=AccountKind.NET_PAY,
                    amount=_V,
                ),
            )
        )

    def test_negative_net_pay_raises(self) -> None:
        """Negative NET_PAY entry raises I9."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(),
                    _entry(
                        entry_id="w1",
                        pay_item_kind="welfare",
                        account=AccountKind.NET_PAY,
                        amount=Decimal("-50.00"),
                    ),
                )
            )
        assert any(v.code == "I9" for v in exc_info.value.violations)


class TestI14TfrNonNegative:
    """I14: TFR_ACCRUAL entries must be non-negative."""

    def test_positive_tfr_passes(self) -> None:
        """Positive TFR_ACCRUAL entry passes I14."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="tfr1",
                    pay_item_kind="tfr_accrual",
                    account=AccountKind.TFR_ACCRUAL,
                    amount=_V,
                ),
            )
        )

    def test_negative_tfr_raises(self) -> None:
        """Negative TFR_ACCRUAL entry raises I14."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(),
                    _entry(
                        entry_id="tfr1",
                        pay_item_kind="tfr_accrual",
                        account=AccountKind.TFR_ACCRUAL,
                        amount=Decimal("-10.00"),
                    ),
                )
            )
        assert any(v.code == "I14" for v in exc_info.value.violations)


class TestReconciliationError:
    """ReconciliationError carries the violation list."""

    def test_error_message_contains_codes(self) -> None:
        """Error string includes the violation codes."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(_ledger(_entry(pay_item_kind="")))
        assert "I3" in str(exc_info.value)

    def test_violations_attribute(self) -> None:
        """ReconciliationError.violations contains ReconciliationViolation objects."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(_ledger(_entry(amount=_ZERO)))
        assert all(
            isinstance(v, ReconciliationViolation) for v in exc_info.value.violations
        )


class TestMultipleViolations:
    """Multiple invariant violations are collected before raising."""

    def test_multiple_violations_collected(self) -> None:
        """Zero amount and empty kind both reported in one error."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(_ledger(_entry(pay_item_kind="", amount=_ZERO)))
        codes = {v.code for v in exc_info.value.violations}
        assert "I3" in codes
        assert "I4" in codes


class TestStubInvariants:
    """Stub invariants (not yet verifiable) return empty violation lists."""

    def test_i1_stub_returns_empty(self) -> None:
        """_check_i1_payitem_coverage returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i1_payitem_coverage(_ledger(_entry())) == []

    def test_i2_stub_returns_empty(self) -> None:
        """_check_i2_no_double_treatment returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i2_no_double_treatment(_ledger(_entry())) == []

    def test_i10_stub_returns_empty(self) -> None:
        """_check_i10_conguaglio_source returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i10_conguaglio_source(_ledger(_entry())) == []

    def test_i11_stub_returns_empty(self) -> None:
        """_check_i11_ytd_state returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i11_ytd_state(_ledger(_entry())) == []

    def test_i12_stub_returns_empty(self) -> None:
        """_check_i12_annual_from_periods returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i12_annual_from_periods(_ledger(_entry())) == []

    def test_i13_stub_returns_empty(self) -> None:
        """_check_i13_single_rounding_point returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i13_single_rounding_point(_ledger(_entry())) == []


class TestCleanLedger:
    """A well-formed ledger with all standard entries passes all checks."""

    def test_full_standard_payroll_passes(self) -> None:
        """Standard payroll ledger with earnings, contributions and TFR passes."""
        ledger = _ledger(
            _entry("base", "base_salary_earning", AccountKind.GROSS_EARNINGS, _V),
            _entry(
                "inps_emp",
                "inps_employee_contribution",
                AccountKind.EMPLOYEE_CONTRIBUTIONS,
                Decimal("9.19"),
            ),
            _entry(
                "inps_er",
                "inps_employer_contribution",
                AccountKind.EMPLOYER_CONTRIBUTIONS,
                Decimal("23.81"),
            ),
            _entry(
                "irpef",
                "irpef",
                AccountKind.IRPEF,
                Decimal("23.00"),
            ),
            _entry(
                "tfr",
                "tfr_accrual",
                AccountKind.TFR_ACCRUAL,
                Decimal("8.33"),
            ),
        )
        _check(ledger)
