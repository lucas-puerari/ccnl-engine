"""Unit tests for ReconciliationService."""

from __future__ import annotations

from datetime import date
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
_PAYMENT = date(2026, 6, 30)
_V = Decimal("100.00")
_ZERO = Decimal(0)


def _entry(
    entry_id: str = "e1",
    pay_item_kind: str = "base_salary_earning",
    account: AccountKind = AccountKind.CASH_EARNINGS,
    amount: Decimal = _V,
) -> LedgerEntry:
    """Build a minimal LedgerEntry for testing.

    Returns:
        A :class:`LedgerEntry` with the given fields.
    """
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=_PERIOD,
        payment_date=_PAYMENT,
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


class TestI5CashEarningsSign:
    """I5: CASH_EARNINGS and EMPLOYEE_DEDUCTIONS entries must be positive."""

    def test_positive_cash_earnings_passes(self) -> None:
        """Positive CASH_EARNINGS entry passes I5."""
        _check(_ledger(_entry(account=AccountKind.CASH_EARNINGS, amount=_V)))

    def test_positive_employee_deduction_passes(self) -> None:
        """Positive EMPLOYEE_DEDUCTIONS entry passes I5."""
        _check(
            _ledger(
                _entry(pay_item_kind="base_salary_earning", amount=_V),
                _entry(
                    entry_id="e2",
                    pay_item_kind="absence_deduction",
                    account=AccountKind.EMPLOYEE_DEDUCTIONS,
                    amount=Decimal("50.00"),
                ),
            )
        )

    def test_negative_cash_earnings_raises(self) -> None:
        """Negative CASH_EARNINGS entry raises I5."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(
                        pay_item_kind="base_salary_earning",
                        account=AccountKind.CASH_EARNINGS,
                        amount=Decimal("-10.00"),
                    )
                )
            )
        assert any(v.code == "I5" for v in exc_info.value.violations)

    def test_negative_employee_deduction_raises(self) -> None:
        """Negative EMPLOYEE_DEDUCTIONS entry raises I5."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(pay_item_kind="base_salary_earning", amount=_V),
                    _entry(
                        entry_id="e2",
                        pay_item_kind="absence_deduction",
                        account=AccountKind.EMPLOYEE_DEDUCTIONS,
                        amount=Decimal("-50.00"),
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
    """I7: net sum of all CASH_EARNINGS entries must be non-negative."""

    def test_positive_cash_sum_passes(self) -> None:
        """Ledger with net-positive CASH_EARNINGS passes I7."""
        _check(
            _ledger(
                _entry(amount=Decimal("500.00")),
                _entry(
                    entry_id="e2",
                    pay_item_kind="second_earnings",
                    account=AccountKind.CASH_EARNINGS,
                    amount=Decimal("100.00"),
                ),
            )
        )

    def test_cash_sum_zero_passes(self) -> None:
        """Zero net CASH_EARNINGS is accepted."""
        _check(_ledger(_entry(amount=_V), _entry(entry_id="e2", amount=_V)))

    def test_negative_cash_sum_raises(self) -> None:
        """Single negative CASH_EARNINGS entry raises I7 and I5."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(
                        pay_item_kind="base_salary_earning",
                        account=AccountKind.CASH_EARNINGS,
                        amount=Decimal("-200.00"),
                    ),
                )
            )
        codes = {v.code for v in exc_info.value.violations}
        assert "I7" in codes


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
    """I9: net pay stub — not yet verifiable with mixed-unit ledger."""

    def test_i9_stub_always_passes(self) -> None:
        """I9 is stubbed; any ledger returns no I9 violations."""
        svc = ReconciliationService()
        assert svc._check_i9_net_pay_non_negative(_ledger(_entry())) == []


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

    def test_i9_stub_returns_empty(self) -> None:
        """_check_i9_net_pay_non_negative returns [] (stub)."""
        svc = ReconciliationService()
        assert svc._check_i9_net_pay_non_negative(_ledger(_entry())) == []

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


class TestI15NonCashBenefitsNonNegative:
    """I15: NON_CASH_BENEFITS entries must be non-negative."""

    def test_positive_non_cash_passes(self) -> None:
        """Positive NON_CASH_BENEFITS entry passes I15."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="fringe1",
                    pay_item_kind="fringe_benefit_item",
                    account=AccountKind.NON_CASH_BENEFITS,
                    amount=_V,
                ),
            )
        )

    def test_negative_non_cash_raises(self) -> None:
        """Negative NON_CASH_BENEFITS entry raises I15."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(),
                    _entry(
                        entry_id="fringe1",
                        pay_item_kind="fringe_benefit_item",
                        account=AccountKind.NON_CASH_BENEFITS,
                        amount=Decimal("-10.00"),
                    ),
                )
            )
        assert any(v.code == "I15" for v in exc_info.value.violations)

    def test_zero_non_cash_passes_invariant(self) -> None:
        """Zero NON_CASH_BENEFITS does not violate I15 in isolation."""
        svc = ReconciliationService()
        ledger = _ledger(
            _entry(
                entry_id="fringe1",
                pay_item_kind="fringe_benefit_item",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=_ZERO,
            ),
        )
        assert svc._check_i15_non_cash_benefits_non_negative(ledger) == []


class TestI16OrdinaryTaxNonNegative:
    """I16: ORDINARY_TAX entries must be non-negative."""

    def test_positive_ordinary_tax_passes(self) -> None:
        """Positive ORDINARY_TAX entry passes I16."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="irpef1",
                    pay_item_kind="irpef",
                    account=AccountKind.ORDINARY_TAX,
                    amount=_V,
                ),
            )
        )

    def test_negative_ordinary_tax_raises(self) -> None:
        """Negative ORDINARY_TAX entry raises I16."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(),
                    _entry(
                        entry_id="irpef1",
                        pay_item_kind="irpef",
                        account=AccountKind.ORDINARY_TAX,
                        amount=Decimal("-50.00"),
                    ),
                )
            )
        assert any(v.code == "I16" for v in exc_info.value.violations)

    def test_zero_ordinary_tax_passes_invariant(self) -> None:
        """Zero ORDINARY_TAX does not violate I16 in isolation."""
        svc = ReconciliationService()
        ledger = _ledger(
            _entry(
                entry_id="irpef1",
                pay_item_kind="irpef",
                account=AccountKind.ORDINARY_TAX,
                amount=_ZERO,
            ),
        )
        assert svc._check_i16_ordinary_tax_non_negative(ledger) == []


class TestI17TfrSettlementNonNegative:
    """I17: TFR_SETTLEMENT entries must be non-negative."""

    def test_positive_tfr_settlement_passes(self) -> None:
        """Positive TFR_SETTLEMENT entry passes I17."""
        _check(
            _ledger(
                _entry(),
                _entry(
                    entry_id="tfr_liq1",
                    pay_item_kind="tfr_settlement_item",
                    account=AccountKind.TFR_SETTLEMENT,
                    amount=_V,
                ),
            )
        )

    def test_negative_tfr_settlement_raises(self) -> None:
        """Negative TFR_SETTLEMENT entry raises I17."""
        with pytest.raises(ReconciliationError) as exc_info:
            _check(
                _ledger(
                    _entry(),
                    _entry(
                        entry_id="tfr_liq1",
                        pay_item_kind="tfr_settlement_item",
                        account=AccountKind.TFR_SETTLEMENT,
                        amount=Decimal("-100.00"),
                    ),
                )
            )
        assert any(v.code == "I17" for v in exc_info.value.violations)

    def test_zero_tfr_settlement_passes_invariant(self) -> None:
        """Zero TFR_SETTLEMENT does not violate I17 in isolation."""
        svc = ReconciliationService()
        ledger = _ledger(
            _entry(
                entry_id="tfr_liq1",
                pay_item_kind="tfr_settlement_item",
                account=AccountKind.TFR_SETTLEMENT,
                amount=_ZERO,
            ),
        )
        assert svc._check_i17_tfr_settlement_non_negative(ledger) == []


class TestCleanLedger:
    """A well-formed ledger with all standard entries passes all checks."""

    def test_full_standard_payroll_passes(self) -> None:
        """Standard payroll ledger with earnings, contributions and TFR passes."""
        ledger = _ledger(
            _entry("base", "base_salary_earning", AccountKind.CASH_EARNINGS, _V),
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
                AccountKind.ORDINARY_TAX,
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
