"""Append-only payroll ledger with logical accounts per pay-item type.

The ledger records every monetary event in a pay period as a ``LedgerEntry``
posted to one of the eleven ``AccountKind`` buckets.  The ``Ledger`` class is
mutable but append-only: entries can be added, never removed or changed.

Net and employer cost are derived from the posted component balances; they are
not recorded as dedicated summary entries.  The ledger enforces a single
competence period per instance: entries whose ``competence_period`` differs
from the ledger unit are rejected unless the caller explicitly marks them as
adjustments.

This module intentionally carries no business logic — it is pure bookkeeping
infrastructure.  Fiscal rules, contribution rules, and the orchestrator are
responsible for deciding which account each item belongs to.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.payroll.domain.pay_items import CompetencePeriod

_ZERO = Decimal(0)


class AccountKind(StrEnum):
    """The twelve logical accounts that partition a payroll pay period."""

    CASH_EARNINGS = "cash_earnings"
    NON_CASH_BENEFITS = "non_cash_benefits"
    EMPLOYEE_DEDUCTIONS = "employee_deductions"
    EMPLOYEE_CONTRIBUTIONS = "employee_contributions"
    EMPLOYER_CONTRIBUTIONS = "employer_contributions"
    ORDINARY_TAX = "ordinary_tax"
    SUBSTITUTE_TAX = "substitute_tax"
    SEPARATE_TAX = "separate_tax"
    SURTAX = "surtax"
    CREDITS = "credits"
    TFR_ACCRUAL = "tfr_accrual"
    TFR_SETTLEMENT = "tfr_settlement"


class LedgerEntry(BaseModel):
    """One monetary event posted to a single logical account.

    Amounts are signed: positive values increase the account balance,
    negative values decrease it.  All amounts are in EUR.

    Attributes:
        payment_date: Calendar date on which this amount is paid to or
            withheld from the employee (typically the last day of the
            competence month).
        source_item_id: The ``item_id`` of the :class:`PayItem` that
            originated this entry, when available.
        policy_decision_id: The ``policy_id`` of the
            :class:`PolicyDecision` that governs the treatment of this
            item, when available.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_id: str
    competence_period: CompetencePeriod
    payment_date: date
    pay_item_id: str
    pay_item_kind: str
    account: AccountKind
    amount: Decimal = Field(allow_inf_nan=False)
    source_item_id: str = ""
    policy_decision_id: str | None = None
    note: str = ""


class Ledger:
    """Append-only collection of ``LedgerEntry`` records for one pay period.

    The ledger enforces:
    - Append-only semantics: entries can only be added.
    - Period consistency: when initialised with a ``competence_period``,
      entries with a different period are rejected unless the caller passes
      ``allow_adjustment=True``.

    All read access returns immutable views (tuples or Decimal sums).
    """

    __slots__ = ("_competence_period", "_entries")

    def __init__(self, competence_period: CompetencePeriod | None = None) -> None:
        """Initialise an empty ledger.

        Args:
            competence_period: When set, all appended entries must carry
                this period unless they are explicitly marked as adjustments.
        """
        self._entries: list[LedgerEntry] = []
        self._competence_period = competence_period

    def append(self, entry: LedgerEntry, *, allow_adjustment: bool = False) -> None:
        """Add one entry to the ledger.

        Args:
            entry: The entry to append.
            allow_adjustment: When ``True``, skip the period-consistency
                check.  Use this only for prior-period corrections
                (rettifiche) that legitimately land in a different month.

        Raises:
            ValueError: When ``competence_period`` is set on this ledger and
                the entry's period differs and ``allow_adjustment`` is
                ``False``.
        """
        if (
            not allow_adjustment
            and self._competence_period is not None
            and entry.competence_period != self._competence_period
        ):
            msg = (
                f"entry {entry.entry_id!r} competence {entry.competence_period} "
                f"differs from ledger period {self._competence_period}"
            )
            raise ValueError(msg)
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
