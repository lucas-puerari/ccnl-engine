"""Posting intent of one base line of a run: its pay item and ledger entry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.facade import (
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    SeniorityEarning,
    TaxCreditItem,
    TaxRefundItem,
    TfrAccrualItem,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.ledger.models import AccountKind

_ItemType = (
    type[BaseSalaryEarning]
    | type[SeniorityEarning]
    | type[EmployeeWithholdingItem]
    | type[EmployerContributionItem]
    | type[TfrAccrualItem]
    | type[TaxRefundItem]
    | type[TaxCreditItem]
)

WITHHOLDING = "employee_withholding_item"


@dataclass(frozen=True)
class _BaseLine:
    """Posting intent of one base line: its pay item and its ledger entry.

    Attributes:
        stem: Id of the pay item and of the entry, before the run tag.
        kind: Pay-item kind of the entry and of its policy resolution.
        account: Ledger account the entry is posted to.
        amount: Amount of the item and of the entry.
        item_type: Pay-item class, or ``None`` for a line posted to the
            ledger only (the PdR substitute tax).
        entry_stem: Entry id stem when it differs from ``stem``.
        allowance_code: Code of a fixed allowance line.
        item_amount: Amount of the pay item when it differs from the
            entry, e.g. the negative trattamento integrativo item of a
            recovery posted as a positive ``CREDIT_RECOVERIES`` entry.
        remittance_code: F24 codice tributo of the entry, when verified.
    """

    stem: str
    kind: str
    account: AccountKind
    amount: Decimal
    item_type: _ItemType | None
    entry_stem: str | None = None
    allowance_code: str | None = None
    item_amount: Decimal | None = None
    remittance_code: str | None = None
