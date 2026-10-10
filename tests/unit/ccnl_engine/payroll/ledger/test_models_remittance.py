"""Remittance summary: tax and credit entries grouped by account and code."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.amount.facade import CompetencePeriod
from ccnl_engine.payroll.ledger.models import AccountKind, LedgerEntry
from ccnl_engine.payroll.ledger.models_remittance import (
    ACCOUNT_CODES,
    CODED_ACCOUNTS,
    REGIME_CODES,
    REMITTANCE_ACCOUNTS,
    RemittanceColumn,
    RemittanceLine,
    remittance_summary,
)

_DEBIT = RemittanceColumn.DEBIT
_CREDIT = RemittanceColumn.CREDIT


def _entry(
    entry_id: str, account: AccountKind, amount: str, code: str | None = None
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=CompetencePeriod(year=2026, month=12),
        payment_date=date(2026, 12, 18),
        pay_item_id=entry_id,
        pay_item_kind="x",
        account=account,
        amount=Decimal(amount),
        remittance_code=code,
    )


def test_three_flows_are_reported_on_separate_lines() -> None:
    """Withheld, credits paid and credits recovered on one conguaglio run.

    The run withholds 200 IRPEF, pays 100 of trattamento integrativo and
    recovers 40 of somma esente paid in excess and 30 of a trattamento of
    an earlier year; 10 of that recovery is left to the worker for lack of
    pay.  The cash earnings are not a tax account and are not reported.
    """
    entries = (
        _entry("cash", AccountKind.CASH_EARNINGS, "1500"),
        _entry("irpef", AccountKind.ORDINARY_TAX, "200", "1001"),
        _entry("tratt", AccountKind.CREDITS, "100", "1701"),
        _entry("somma_rec", AccountKind.CREDIT_RECOVERIES, "40", "1704"),
        _entry("tratt_rec", AccountKind.CREDIT_RECOVERIES, "30"),
        _entry("shortfall", AccountKind.CREDIT_RECOVERY_SHORTFALL, "10"),
    )

    assert remittance_summary(entries) == (
        RemittanceLine(AccountKind.ORDINARY_TAX, "1001", _DEBIT, Decimal(200)),
        RemittanceLine(AccountKind.CREDITS, "1701", _CREDIT, Decimal(100)),
        RemittanceLine(AccountKind.CREDIT_RECOVERIES, "1704", _DEBIT, Decimal(40)),
        RemittanceLine(AccountKind.CREDIT_RECOVERIES, None, None, Decimal(30)),
        RemittanceLine(AccountKind.CREDIT_RECOVERY_SHORTFALL, None, None, Decimal(10)),
    )


def test_same_code_is_summed_and_zero_totals_dropped() -> None:
    """Two 3802 entries sum; a zero municipal line is not reported."""
    entries = (
        _entry("r1", AccountKind.SURTAX, "12.50", "3802"),
        _entry("r2", AccountKind.SURTAX, "7.50", "3802"),
        _entry("m1", AccountKind.SURTAX, "0"),
    )

    assert remittance_summary(entries) == (
        RemittanceLine(AccountKind.SURTAX, "3802", _DEBIT, Decimal(20)),
    )


def test_coded_lines_come_before_the_uncoded_one_by_code() -> None:
    """Within an account: codes in order, then the uncoded line."""
    entries = (
        _entry("free", AccountKind.SUBSTITUTE_TAX, "5"),
        _entry("night", AccountKind.SUBSTITUTE_TAX, "15", "1076"),
        _entry("pdr", AccountKind.SUBSTITUTE_TAX, "30", "1053"),
    )

    codes = [line.remittance_code for line in remittance_summary(entries)]
    assert codes == ["1053", "1076", None]


def test_every_admitted_code_belongs_to_a_reported_account() -> None:
    """Coded accounts are reported and admit at least one code."""
    assert set(ACCOUNT_CODES) <= set(REMITTANCE_ACCOUNTS)
    assert set(ACCOUNT_CODES) >= CODED_ACCOUNTS
    assert set(REGIME_CODES.values()) <= ACCOUNT_CODES[AccountKind.SUBSTITUTE_TAX]
