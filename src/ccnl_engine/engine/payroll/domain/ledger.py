"""Append-only payroll ledger with minimal logical accounts.

The ledger records every monetary event in a pay period as a ``LedgerEntry``
posted to one of the seven ``AccountKind`` buckets.  The ``Ledger`` class is
mutable but append-only: entries can be added, never removed or changed.

This module intentionally carries no business logic — it is pure bookkeeping
infrastructure.  Fiscal rules, contribution rules, and the orchestrator are
responsible for deciding which account each item belongs to.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod

_ZERO = Decimal(0)


class AccountKind(StrEnum):
    """The seven logical accounts that partition a payroll pay period."""

    GROSS_EARNINGS = "gross_earnings"
    EMPLOYEE_CONTRIBUTIONS = "employee_contributions"
    EMPLOYER_CONTRIBUTIONS = "employer_contributions"
    IRPEF = "irpef"
    NET_PAY = "net_pay"
    EMPLOYER_COST = "employer_cost"
    TFR_ACCRUAL = "tfr_accrual"


class LedgerEntry(BaseModel):
    """One monetary event posted to a single logical account.

    Amounts are signed: positive values increase the account balance (credits),
    negative values decrease it (debits).  All amounts are in EUR.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_id: str
    competence_period: CompetencePeriod
    pay_item_id: str
    pay_item_kind: str
    account: AccountKind
    amount: Decimal = Field(allow_inf_nan=False)
    note: str = ""


class Ledger:
    """Append-only collection of ``LedgerEntry`` records for one pay period.

    The ledger enforces append-only semantics: the only mutation is adding new
    entries.  All read access returns immutable views (tuples or Decimal sums).
    """

    __slots__ = ("_entries",)

    def __init__(self) -> None:
        """Initialise an empty ledger."""
        self._entries: list[LedgerEntry] = []

    def append(self, entry: LedgerEntry) -> None:
        """Add one entry to the ledger."""
        self._entries.append(entry)

    def entries(self) -> tuple[LedgerEntry, ...]:
        """Return all entries in insertion order.

        Returns:
            Immutable tuple of every ``LedgerEntry`` appended so far.
        """
        return tuple(self._entries)

    def __len__(self) -> int:
        """Return the number of entries in the ledger.

        Returns:
            Count of appended entries.
        """
        return len(self._entries)

    def __iter__(self) -> Iterator[LedgerEntry]:
        """Iterate over entries in insertion order.

        Returns:
            Iterator over every ``LedgerEntry`` in append order.
        """
        return iter(self._entries)

    def by_account(self, account: AccountKind) -> tuple[LedgerEntry, ...]:
        """Return all entries posted to ``account``.

        Returns:
            Immutable tuple of entries whose ``account`` matches.
        """
        return tuple(e for e in self._entries if e.account == account)

    def total(self, account: AccountKind) -> Decimal:
        """Return the signed sum of all amounts posted to ``account``.

        Returns:
            Sum of ``amount`` for matching entries, or zero if none.
        """
        return sum(
            (e.amount for e in self._entries if e.account == account),
            _ZERO,
        )

    def totals(self) -> dict[AccountKind, Decimal]:
        """Return a mapping of every account to its signed total.

        Accounts with no entries are included with a zero balance so callers
        can always read any account without a key-existence check.

        Returns:
            Dict keyed by every ``AccountKind``, values are signed totals.
        """
        result: dict[AccountKind, Decimal] = dict.fromkeys(AccountKind, _ZERO)
        for entry in self._entries:
            result[entry.account] += entry.amount
        return result
