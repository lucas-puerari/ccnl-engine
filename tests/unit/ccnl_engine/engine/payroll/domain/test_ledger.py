"""Unit tests for the append-only Ledger and LedgerEntry."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.payroll.domain.ledger import (
    AccountKind,
    Ledger,
    LedgerEntry,
)
from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod

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
    """AccountKind covers all eleven logical payroll accounts."""

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

    def test_tfr_settlement(self) -> None:
        """TFR_SETTLEMENT maps to 'tfr_settlement'."""
        assert AccountKind.TFR_SETTLEMENT.value == "tfr_settlement"

    def test_eleven_members(self) -> None:
        """AccountKind has exactly eleven members."""
        assert len(AccountKind) == 11

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


class TestLedgerAppend:
    """Ledger append and read-only views."""

    def test_empty_ledger(self) -> None:
        """A new ledger has zero entries."""
        ledger = Ledger()
        assert len(ledger) == 0
        assert ledger.entries() == ()

    def test_append_single(self) -> None:
        """Appending one entry increases len to 1."""
        ledger = Ledger()
        ledger.append(_entry())
        assert len(ledger) == 1

    def test_append_multiple_order_preserved(self) -> None:
        """Entries are returned in insertion order."""
        ledger = Ledger()
        e1 = _entry(entry_id="e1", amount="100.00")
        e2 = _entry(entry_id="e2", amount="200.00")
        ledger.append(e1)
        ledger.append(e2)
        entries = ledger.entries()
        assert entries[0].entry_id == "e1"
        assert entries[1].entry_id == "e2"

    def test_entries_returns_tuple(self) -> None:
        """entries() returns an immutable tuple."""
        ledger = Ledger()
        ledger.append(_entry())
        assert isinstance(ledger.entries(), tuple)

    def test_iter(self) -> None:
        """Ledger is iterable and yields each entry."""
        ledger = Ledger()
        e = _entry()
        ledger.append(e)
        assert list(ledger) == [e]


class TestLedgerPeriodValidator:
    """Ledger period validator rejects mismatched competence periods."""

    def test_no_validator_when_no_period(self) -> None:
        """Ledger without period allows any competence period."""
        ledger = Ledger()
        e1 = _entry(entry_id="e1")
        e2 = LedgerEntry(
            entry_id="e2",
            competence_period=CompetencePeriod(year=2026, month=7),
            payment_date=date(2026, 7, 31),
            pay_item_id="p2",
            pay_item_kind="base_salary_earning",
            account=AccountKind.CASH_EARNINGS,
            amount=_D("1000.00"),
        )
        ledger.append(e1)
        ledger.append(e2)
        assert len(ledger) == 2

    def test_period_validator_rejects_mismatch(self) -> None:
        """When competence_period is set, mismatched entry raises ValueError."""
        ledger = Ledger(competence_period=_PERIOD)
        wrong_entry = LedgerEntry(
            entry_id="e_wrong",
            competence_period=CompetencePeriod(year=2026, month=7),
            payment_date=date(2026, 7, 31),
            pay_item_id="p_wrong",
            pay_item_kind="base_salary_earning",
            account=AccountKind.CASH_EARNINGS,
            amount=_D("1000.00"),
        )
        with pytest.raises(ValueError, match="e_wrong"):
            ledger.append(wrong_entry)

    def test_period_validator_accepts_matching_period(self) -> None:
        """When competence_period is set, matching entry is accepted."""
        ledger = Ledger(competence_period=_PERIOD)
        ledger.append(_entry())
        assert len(ledger) == 1

    def test_allow_adjustment_bypasses_validator(self) -> None:
        """allow_adjustment=True bypasses the period check."""
        ledger = Ledger(competence_period=_PERIOD)
        adj_entry = LedgerEntry(
            entry_id="e_adj",
            competence_period=CompetencePeriod(year=2026, month=5),
            payment_date=date(2026, 5, 31),
            pay_item_id="p_adj",
            pay_item_kind="contract_renewal_arrears",
            account=AccountKind.CASH_EARNINGS,
            amount=_D("200.00"),
        )
        ledger.append(adj_entry, allow_adjustment=True)
        assert len(ledger) == 1


class TestLedgerTotal:
    """Ledger total and by_account aggregation."""

    def test_total_empty_account(self) -> None:
        """total() for an account with no entries returns zero."""
        ledger = Ledger()
        ledger.append(_entry(account=AccountKind.CASH_EARNINGS))
        assert ledger.total(AccountKind.ORDINARY_TAX) == _D(0)

    def test_total_single_entry(self) -> None:
        """total() sums a single entry correctly."""
        ledger = Ledger()
        ledger.append(_entry(account=AccountKind.CASH_EARNINGS, amount="1500.00"))
        assert ledger.total(AccountKind.CASH_EARNINGS) == _D("1500.00")

    def test_total_multiple_entries_same_account(self) -> None:
        """total() sums multiple entries in the same account."""
        ledger = Ledger()
        ledger.append(_entry(entry_id="e1", amount="1000.00"))
        ledger.append(_entry(entry_id="e2", amount="200.00"))
        assert ledger.total(AccountKind.CASH_EARNINGS) == _D("1200.00")

    def test_total_signed(self) -> None:
        """total() respects negative amounts."""
        ledger = Ledger()
        ledger.append(
            _entry(
                account=AccountKind.EMPLOYEE_CONTRIBUTIONS,
                amount="-300.00",
            )
        )
        assert ledger.total(AccountKind.EMPLOYEE_CONTRIBUTIONS) == _D("-300.00")

    def test_by_account_filters_correctly(self) -> None:
        """by_account() returns only entries for the given account."""
        ledger = Ledger()
        e_cash = _entry(
            entry_id="e1",
            account=AccountKind.CASH_EARNINGS,
        )
        e_tax = _entry(
            entry_id="e2",
            account=AccountKind.ORDINARY_TAX,
            amount="400.00",
        )
        ledger.append(e_cash)
        ledger.append(e_tax)
        assert ledger.by_account(AccountKind.CASH_EARNINGS) == (e_cash,)
        assert ledger.by_account(AccountKind.ORDINARY_TAX) == (e_tax,)

    def test_totals_all_accounts(self) -> None:
        """totals() returns all eleven accounts, zeros for empty ones."""
        ledger = Ledger()
        ledger.append(_entry(account=AccountKind.CASH_EARNINGS, amount="1000.00"))
        result = ledger.totals()
        assert set(result.keys()) == set(AccountKind)
        assert result[AccountKind.CASH_EARNINGS] == _D("1000.00")
        assert result[AccountKind.ORDINARY_TAX] == _D(0)

    def test_totals_accumulates_multiple(self) -> None:
        """totals() correctly accumulates multiple entries per account."""
        ledger = Ledger()
        ledger.append(
            _entry(
                entry_id="e1",
                account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                amount="500.00",
            )
        )
        ledger.append(
            _entry(
                entry_id="e2",
                account=AccountKind.EMPLOYER_CONTRIBUTIONS,
                amount="300.00",
            )
        )
        assert ledger.totals()[AccountKind.EMPLOYER_CONTRIBUTIONS] == _D("800.00")
