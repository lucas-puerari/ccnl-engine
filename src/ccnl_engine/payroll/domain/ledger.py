"""Payroll ledger entries with logical accounts per pay-item type.

The ledger records every monetary event in a pay period as a ``LedgerEntry``
posted to one of the eleven ``AccountKind`` buckets.  Net and employer cost
are derived from the posted component balances; they are not recorded as
dedicated summary entries.

This module intentionally carries no business logic — it is pure bookkeeping
infrastructure.  Fiscal rules, contribution rules, and the orchestrator are
responsible for deciding which account each item belongs to.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.payroll.domain.pay_items import CompetencePeriod

# ---------------------------------------------------------------------------
# Domain primitives
# ---------------------------------------------------------------------------

#: All monetary amounts in this package are EUR, represented as Decimal.
type Money = Decimal


class AccountKind(StrEnum):
    """The fourteen logical accounts that partition a payroll pay period."""

    CASH_EARNINGS = "cash_earnings"
    NON_CASH_BENEFITS = "non_cash_benefits"
    EMPLOYEE_DEDUCTIONS = "employee_deductions"
    EMPLOYEE_CONTRIBUTIONS = "employee_contributions"
    EMPLOYER_CONTRIBUTIONS = "employer_contributions"
    BILATERAL_FUND_EMPLOYEE = "bilateral_fund_employee"
    BILATERAL_FUND_EMPLOYER = "bilateral_fund_employer"
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


# ---------------------------------------------------------------------------
# Accounting domain types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PostingIntent:
    """Handler-produced posting decision before period fields are applied.

    Handlers supply identity, account routing, amount, and policy reference.
    :func:`~ccnl_engine.payroll.application._posting_service.post` adds
    ``competence_period`` and ``payment_date`` to produce a :class:`LedgerEntry`.

    Attributes:
        entry_id: Unique ledger entry identifier for this posting.
        source_item_id: The ``item_id`` of the originating :class:`PayItem`.
        pay_item_kind: Pay-item kind string, used for policy resolution lookups.
        account: Logical account this posting targets.
        amount: Monetary amount in EUR (positive increases the account balance).
        policy_decision_id: Stable policy rule identifier from the resolver.
        note: Optional free-text annotation.
    """

    entry_id: str
    source_item_id: str
    pay_item_kind: str
    account: AccountKind
    amount: Money
    policy_decision_id: str | None = None
    note: str = ""
