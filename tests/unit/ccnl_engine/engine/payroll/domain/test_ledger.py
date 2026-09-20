"""Unit tests for the append-only Ledger and LedgerEntry."""

from __future__ import annotations

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
_D = Decimal


def _entry(
    account: AccountKind = AccountKind.GROSS_EARNINGS,
    amount: str = "1000.00",
    entry_id: str = "e1",
    pay_item_id: str = "p1",
    pay_item_kind: str = "base_salary_earning",
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=_PERIOD,
        pay_item_id=pay_item_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=_D(amount),
    )


class TestAccountKind:
    """AccountKind covers all seven logical payroll accounts."""

    def test_gross_earnings(self) -> None:
        """GROSS_EARNINGS maps to 'gross_earnings'."""
        assert AccountKind.GROSS_EARNINGS.value == "gross_earnings"

    def test_employee_contributions(self) -> None:
        """EMPLOYEE_CONTRIBUTIONS maps to 'employee_contributions'."""
        assert AccountKind.EMPLOYEE_CONTRIBUTIONS.value == "employee_contributions"

    def test_employer_contributions(self) -> None:
        """EMPLOYER_CONTRIBUTIONS maps to 'employer_contributions'."""
        assert AccountKind.EMPLOYER_CONTRIBUTIONS.value == "employer_contributions"

    def test_irpef(self) -> None:
        """IRPEF maps to 'irpef'."""
        assert AccountKind.IRPEF.value == "irpef"

    def test_net_pay(self) -> None:
        """NET_PAY maps to 'net_pay'."""
        assert AccountKind.NET_PAY.value == "net_pay"

    def test_employer_cost(self) -> None:
        """EMPLOYER_COST maps to 'employer_cost'."""
        assert AccountKind.EMPLOYER_COST.value == "employer_cost"

    def test_tfr_accrual(self) -> None:
        """TFR_ACCRUAL maps to 'tfr_accrual'."""
        assert AccountKind.TFR_ACCRUAL.value == "tfr_accrual"

    def test_seven_members(self) -> None:
        """AccountKind has exactly seven members."""
        assert len(AccountKind) == 7

    def test_is_str(self) -> None:
        """AccountKind members are strings (StrEnum)."""
        assert isinstance(AccountKind.NET_PAY, str)


class TestLedgerEntry:
    """LedgerEntry construction and immutability."""

    def test_basic_construction(self) -> None:
        """LedgerEntry constructs with required fields."""
        e = _entry()
        assert e.entry_id == "e1"
        assert e.account == AccountKind.GROSS_EARNINGS
        assert e.amount == _D("1000.00")

    def test_note_defaults_empty(self) -> None:
        """Note field defaults to empty string."""
        assert not _entry().note

    def test_note_stored(self) -> None:
        """Note field is preserved when provided."""
        e = LedgerEntry(
            entry_id="e2",
            competence_period=_PERIOD,
            pay_item_id="p2",
            pay_item_kind="overtime_earning",
            account=AccountKind.GROSS_EARNINGS,
            amount=_D("200.00"),
            note="straordinario",
        )
        assert e.note == "straordinario"

    def test_negative_amount_allowed(self) -> None:
        """Negative amounts (debits) are valid."""
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
                pay_item_id="p",
                pay_item_kind="k",
                account=AccountKind.NET_PAY,
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


class TestLedgerTotal:
    """Ledger total and by_account aggregation."""

    def test_total_empty_account(self) -> None:
        """total() for an account with no entries returns zero."""
        ledger = Ledger()
        ledger.append(_entry(account=AccountKind.GROSS_EARNINGS))
        assert ledger.total(AccountKind.NET_PAY) == _D(0)

    def test_total_single_entry(self) -> None:
        """total() sums a single entry correctly."""
        ledger = Ledger()
        ledger.append(_entry(account=AccountKind.GROSS_EARNINGS, amount="1500.00"))
        assert ledger.total(AccountKind.GROSS_EARNINGS) == _D("1500.00")

    def test_total_multiple_entries_same_account(self) -> None:
        """total() sums multiple entries in the same account."""
        ledger = Ledger()
        ledger.append(_entry(entry_id="e1", amount="1000.00"))
        ledger.append(_entry(entry_id="e2", amount="200.00"))
        assert ledger.total(AccountKind.GROSS_EARNINGS) == _D("1200.00")

    def test_total_signed(self) -> None:
        """total() respects negative (debit) amounts."""
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
        e_gross = _entry(
            entry_id="e1",
            account=AccountKind.GROSS_EARNINGS,
        )
        e_irpef = _entry(
            entry_id="e2",
            account=AccountKind.IRPEF,
            amount="-400.00",
        )
        ledger.append(e_gross)
        ledger.append(e_irpef)
        assert ledger.by_account(AccountKind.GROSS_EARNINGS) == (e_gross,)
        assert ledger.by_account(AccountKind.IRPEF) == (e_irpef,)

    def test_totals_all_accounts(self) -> None:
        """totals() returns all seven accounts, zeros for empty ones."""
        ledger = Ledger()
        ledger.append(_entry(account=AccountKind.GROSS_EARNINGS, amount="1000.00"))
        result = ledger.totals()
        assert set(result.keys()) == set(AccountKind)
        assert result[AccountKind.GROSS_EARNINGS] == _D("1000.00")
        assert result[AccountKind.NET_PAY] == _D(0)

    def test_totals_accumulates_multiple(self) -> None:
        """totals() correctly accumulates multiple entries per account."""
        ledger = Ledger()
        ledger.append(
            _entry(entry_id="e1", account=AccountKind.EMPLOYER_COST, amount="500.00")
        )
        ledger.append(
            _entry(entry_id="e2", account=AccountKind.EMPLOYER_COST, amount="300.00")
        )
        assert ledger.totals()[AccountKind.EMPLOYER_COST] == _D("800.00")
