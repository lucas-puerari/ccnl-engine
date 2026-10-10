"""Postings of the somma esente: the tax credit item and its ledger entry."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.facade import PayItem, TaxCreditItem
from ccnl_engine.payroll.ledger.models import AccountKind, LedgerEntry
from ccnl_engine.payroll.ledger.models_remittance import SOMMA_ESENTE_CREDIT
from ccnl_engine.payroll.period.services_shared import (
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.withholding.models_recovery_plan import InstallmentRun

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.amount.facade import CompetencePeriod
    from ccnl_engine.payroll.amount.policies import PolicyContext, PolicyResolver

__all__ = ["SommaEsentePosting", "postings"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class SommaEsentePosting:
    """Where the somma esente of a run is posted.

    Attributes:
        resolver: Policy resolver of the run.
        policy_context: Policy context of the run.
        competence_period: Competence period of the run.
        payment_date: Payment date of the run.
        run_id: Identifier of the run, used in the item id.
        run: The run as a recovery sees it: final or adjustment.
    """

    resolver: PolicyResolver
    policy_context: PolicyContext
    competence_period: CompetencePeriod
    payment_date: date
    run_id: str
    run: InstallmentRun = field(default_factory=InstallmentRun)


def postings(
    amount: Decimal, posting: SommaEsentePosting
) -> tuple[tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Return the signed item and the entry of ``amount``, coded 1704.

    Returns:
        Nothing for a zero amount; else ``somma_esente_{run_id}`` on
        ``CREDITS`` or ``somma_esente_recovery_{run_id}`` on
        ``CREDIT_RECOVERIES`` (ris. AdE 9/E/2025).
    """
    if amount == _ZERO:
        return (), ()
    policy_id = _require_resolution(
        posting.resolver, "tax_credit_item", posting.policy_context
    ).policy_id
    prefix = "somma_esente" if (paid := amount > _ZERO) else "somma_esente_recovery"
    item_id = f"{prefix}_{posting.run_id}"
    item = TaxCreditItem(
        item_id=item_id,
        competence_period=posting.competence_period,
        payment_date=posting.payment_date,
        quantity=Decimal(1),
        amount=amount,
    )
    entry = _make_entry(
        item_id,
        item_id,
        "tax_credit_item",
        posting.competence_period,
        posting.payment_date,
        AccountKind.CREDITS if paid else AccountKind.CREDIT_RECOVERIES,
        abs(amount),
        policy_id=policy_id,
        remittance_code=SOMMA_ESENTE_CREDIT,
    )
    return (item,), (entry,)
