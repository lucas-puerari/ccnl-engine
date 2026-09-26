"""Unit tests for AccountKind and LedgerEntry."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.payroll.domain.ledger import (
    AccountKind,
    LedgerEntry,
)
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod

_PERIOD = CompetencePeriod(year=2026, month=6)
_PAYMENT = date(2026, 6, 30)
_D = Decimal


def _entry(
    account: AccountKind = AccountKind.CASH_EARNINGS,
    amount: str = "1000.00",
    entry_id: str = "e1",
    pay_item_id: str = "p1",
    pay_item_kind: str = "base_salary_earning",
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=_PERIOD,
        payment_date=_PAYMENT,
        pay_item_id=pay_item_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=_D(amount),
    )


class TestAccountKind:
    """AccountKind covers all twelve logical payroll accounts."""

    def test_cash_earnings(self) -> None:
        """CASH_EARNINGS maps to 'cash_earnings'."""
        assert AccountKind.CASH_EARNINGS.value == "cash_earnings"

    def test_non_cash_benefits(self) -> None:
        """NON_CASH_BENEFITS maps to 'non_cash_benefits'."""
        assert AccountKind.NON_CASH_BENEFITS.value == "non_cash_benefits"

    def test_employee_deductions(self) -> None:
        """EMPLOYEE_DEDUCTIONS maps to 'employee_deductions'."""
        assert AccountKind.EMPLOYEE_DEDUCTIONS.value == "employee_deductions"

    def test_employee_contributions(self) -> None:
        """EMPLOYEE_CONTRIBUTIONS maps to 'employee_contributions'."""
        assert AccountKind.EMPLOYEE_CONTRIBUTIONS.value == "employee_contributions"

    def test_employer_contributions(self) -> None:
        """EMPLOYER_CONTRIBUTIONS maps to 'employer_contributions'."""
        assert AccountKind.EMPLOYER_CONTRIBUTIONS.value == "employer_contributions"

    def test_bilateral_fund_employee(self) -> None:
        """BILATERAL_FUND_EMPLOYEE maps to 'bilateral_fund_employee'."""
        assert AccountKind.BILATERAL_FUND_EMPLOYEE.value == "bilateral_fund_employee"

    def test_bilateral_fund_employer(self) -> None:
        """BILATERAL_FUND_EMPLOYER maps to 'bilateral_fund_employer'."""
        assert AccountKind.BILATERAL_FUND_EMPLOYER.value == "bilateral_fund_employer"

    def test_ordinary_tax(self) -> None:
        """ORDINARY_TAX maps to 'ordinary_tax'."""
        assert AccountKind.ORDINARY_TAX.value == "ordinary_tax"

    def test_substitute_tax(self) -> None:
        """SUBSTITUTE_TAX maps to 'substitute_tax'."""
        assert AccountKind.SUBSTITUTE_TAX.value == "substitute_tax"

    def test_separate_tax(self) -> None:
        """SEPARATE_TAX maps to 'separate_tax'."""
        assert AccountKind.SEPARATE_TAX.value == "separate_tax"

    def test_credits(self) -> None:
        """CREDITS maps to 'credits'."""
        assert AccountKind.CREDITS.value == "credits"

    def test_tfr_accrual(self) -> None:
        """TFR_ACCRUAL maps to 'tfr_accrual'."""
        assert AccountKind.TFR_ACCRUAL.value == "tfr_accrual"

    def test_surtax(self) -> None:
        """SURTAX maps to 'surtax'."""
        assert AccountKind.SURTAX.value == "surtax"

    def test_tfr_settlement(self) -> None:
        """TFR_SETTLEMENT maps to 'tfr_settlement'."""
        assert AccountKind.TFR_SETTLEMENT.value == "tfr_settlement"

    def test_fourteen_members(self) -> None:
        """AccountKind has exactly fourteen members."""
        assert len(AccountKind) == 14

    def test_is_str(self) -> None:
        """AccountKind members are strings (StrEnum)."""
        assert isinstance(AccountKind.CASH_EARNINGS, str)


class TestLedgerEntry:
    """LedgerEntry construction and immutability."""

    def test_basic_construction(self) -> None:
        """LedgerEntry constructs with required fields."""
        e = _entry()
        assert e.entry_id == "e1"
        assert e.account == AccountKind.CASH_EARNINGS
        assert e.amount == _D("1000.00")

    def test_payment_date_stored(self) -> None:
        """payment_date field is preserved."""
        assert _entry().payment_date == _PAYMENT

    def test_source_item_id_defaults_empty(self) -> None:
        """source_item_id defaults to empty string."""
        assert not _entry().source_item_id

    def test_policy_decision_id_defaults_none(self) -> None:
        """policy_decision_id defaults to None."""
        assert _entry().policy_decision_id is None

    def test_note_defaults_empty(self) -> None:
        """Note field defaults to empty string."""
        assert not _entry().note

    def test_note_stored(self) -> None:
        """Note field is preserved when provided."""
        e = LedgerEntry(
            entry_id="e2",
            competence_period=_PERIOD,
            payment_date=_PAYMENT,
            pay_item_id="p2",
            pay_item_kind="overtime_supplement",
            account=AccountKind.CASH_EARNINGS,
            amount=_D("200.00"),
            note="straordinario",
        )
        assert e.note == "straordinario"

    def test_source_item_id_stored(self) -> None:
        """source_item_id is preserved when provided."""
        e = LedgerEntry(
            entry_id="e3",
            competence_period=_PERIOD,
            payment_date=_PAYMENT,
            pay_item_id="p3",
            pay_item_kind="base_salary_earning",
            account=AccountKind.CASH_EARNINGS,
            amount=_D("1000.00"),
            source_item_id="base_salary_2026_06",
        )
        assert e.source_item_id == "base_salary_2026_06"

    def test_policy_decision_id_stored(self) -> None:
        """policy_decision_id is preserved when provided."""
        e = LedgerEntry(
            entry_id="e4",
            competence_period=_PERIOD,
            payment_date=_PAYMENT,
            pay_item_id="p4",
            pay_item_kind="base_salary_earning",
            account=AccountKind.CASH_EARNINGS,
            amount=_D("1000.00"),
            policy_decision_id="it/earning/ordinary",
        )
        assert e.policy_decision_id == "it/earning/ordinary"

    def test_negative_amount_allowed(self) -> None:
        """Negative amounts are valid (e.g. for corrections)."""
        e = _entry(amount="-500.00")
        assert e.amount == _D("-500.00")

    def test_frozen(self) -> None:
        """LedgerEntry is immutable (frozen Pydantic model)."""
        e = _entry()
        with pytest.raises(ValidationError):
            e.amount = _D("0")  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        """Extra fields raise ValidationError."""
        with pytest.raises(ValidationError):
            LedgerEntry(  # type: ignore[call-arg]
                entry_id="x",
                competence_period=_PERIOD,
                payment_date=_PAYMENT,
                pay_item_id="p",
                pay_item_kind="k",
                account=AccountKind.CASH_EARNINGS,
                amount=_D(0),
                unknown_field="oops",
            )
