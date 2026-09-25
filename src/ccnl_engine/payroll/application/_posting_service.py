"""Convert PostingIntent records to LedgerEntry objects.

PostingService owns the step where period-invariant fields (competence_period,
payment_date) are applied to handler-produced intents, yielding the final
append-only ledger entries for the period.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.ledger import LedgerEntry, PostingIntent

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.pay_items import CompetencePeriod


def post(
    intents: tuple[PostingIntent, ...],
    cp: CompetencePeriod,
    payment_date: date,
) -> tuple[LedgerEntry, ...]:
    """Project posting intents to ledger entries for one competence period.

    Each intent carries the handler-level decision (what, where, which policy).
    This function supplies the period-level context (when) that is invariant
    across all events in the same period run.

    Args:
        intents: Handler-produced posting decisions for this period.
        cp: Competence period shared by all resulting entries.
        payment_date: Payment date shared by all resulting entries.

    Returns:
        One :class:`~ccnl_engine.payroll.domain.ledger.LedgerEntry` per intent,
        in the same order as ``intents``.

    """
    _check_unique_ids(intents)
    return tuple(
        LedgerEntry(
            entry_id=intent.entry_id,
            competence_period=cp,
            payment_date=payment_date,
            pay_item_id=intent.source_item_id,
            pay_item_kind=intent.pay_item_kind,
            account=intent.account,
            amount=intent.amount,
            source_item_id=intent.source_item_id,
            policy_decision_id=intent.policy_decision_id,
            note=intent.note,
        )
        for intent in intents
    )


def _check_unique_ids(intents: tuple[PostingIntent, ...]) -> None:
    """Raise ValueError when any entry_id appears more than once.

    Raises:
        ValueError: On the first duplicate entry_id found.
    """
    seen: set[str] = set()
    for intent in intents:
        if intent.entry_id in seen:
            msg = f"Duplicate entry_id in posting batch: {intent.entry_id!r}"
            raise ValueError(msg)
        seen.add(intent.entry_id)
