"""Shared private utilities for period calculation sub-modules."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.policy import (
    ContributionAxis,
    PolicyContext,
    PolicyResolution,
    PolicyResolver,
    TaxAxis,
    TfrAxis,
)
from ccnl_engine.payroll.domain.treatment import EventTreatment

if TYPE_CHECKING:
    from datetime import date

_ZERO = Decimal(0)


def _require_resolution(
    resolver: PolicyResolver,
    kind: str,
    context: PolicyContext,
) -> PolicyResolution:
    resolution = resolver.resolve(kind, context)
    if resolution is None:
        msg = f"No policy rule found for pay-item kind '{kind}' on {context.as_of}"
        raise DataIntegrityError(msg)
    return resolution


def _treatment_from_resolution(resolution: PolicyResolution) -> EventTreatment:
    inps = resolution.contribution in {
        ContributionAxis.INCLUDED,
        ContributionAxis.CAPPED,
        ContributionAxis.SPECIAL_BASE,
    }
    tfr = resolution.tfr == TfrAxis.INCLUDED
    substitute = resolution.tax == TaxAxis.SUBSTITUTE
    irpef = not substitute and resolution.tax not in {
        TaxAxis.NOT_APPLICABLE,
        TaxAxis.EXEMPT,
    }
    return EventTreatment(inps=inps, tfr=tfr, irpef=irpef, substitute=substitute)


def _make_entry(
    entry_id: str,
    pay_item_id: str,
    pay_item_kind: str,
    competence_period: CompetencePeriod,
    payment_date: date,
    account: AccountKind,
    amount: Decimal,
    policy_id: str | None = None,
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        competence_period=competence_period,
        payment_date=payment_date,
        pay_item_id=pay_item_id,
        pay_item_kind=pay_item_kind,
        account=account,
        amount=amount,
        source_item_id=pay_item_id,
        policy_decision_id=policy_id,
    )


def _sum_ledger(entries: tuple[LedgerEntry, ...], account: AccountKind) -> Decimal:
    """Sum all ledger entry amounts for a given account kind.

    Returns:
        Total for ``account`` in ``entries``, or zero when no entry is present.
    """
    return sum((e.amount for e in entries if e.account == account), _ZERO)
