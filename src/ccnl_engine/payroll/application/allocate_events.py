"""Aggregate variable work events into accounting entries and totals."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._event_items import _check_event_date
from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application._posting_service import post as _post
from ccnl_engine.payroll.application.handlers.registry import (
    _HANDLER_REGISTRY,
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
from ccnl_engine.payroll.domain.events import WorkEvent
from ccnl_engine.payroll.domain.ledger import LedgerEntry, PostingIntent
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod, PayItem

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver


@dataclass(frozen=True)
class _EventTotals:
    """Aggregated INPS/TFR/IRPEF bases from variable work events."""

    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal
    fringe_value: Decimal
    fringe_inps: Decimal
    fringe_irpef: Decimal
    substitute_base: Decimal


def _process_events(
    events: tuple[WorkEvent, ...],
    cp: CompetencePeriod,
    payment_date: date,
    tag: str,
    date_ctx: EffectiveDateContext,
    resolver: PolicyResolver,
    context: PolicyContext,
    fringe_threshold: Decimal = _ZERO,
    opening_fringe_ytd: Decimal = _ZERO,
    opening_fringe_taxed: Decimal = _ZERO,
    pdr_income_ceiling: Decimal | None = None,
    rinnovo_flat_rate: Decimal | None = None,
    notte_flat_rate: Decimal | None = None,
    notte_income_ceiling: Decimal | None = None,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.

    Raises:
        TypeError: When an event type has no registered handler (should never
            occur in practice; indicates a missing registry entry).
    """
    total_inps = _ZERO
    total_tfr = _ZERO
    total_irpef = _ZERO
    total_substitute = _ZERO
    total_fringe_value = _ZERO
    total_fringe_inps = _ZERO
    total_fringe_irpef = _ZERO
    cumulative_fringe = opening_fringe_ytd
    cumulative_taxed = opening_fringe_taxed
    items: list[PayItem] = []
    intents: list[PostingIntent] = []

    for i, event in enumerate(events):
        evt_id = f"{tag}_evt{i}"
        _check_event_date(event, date_ctx, i)

        handler = _HANDLER_REGISTRY.get(type(event))
        if handler is None:  # pragma: no cover
            msg = f"No handler registered for event type {type(event).__name__}"
            raise TypeError(msg)

        ctx: _EventHandlerCtx = _EventHandlerCtx(
            evt_id=evt_id,
            cp=cp,
            payment_date=payment_date,
            resolver=resolver,
            context=context,
            fringe_threshold=fringe_threshold,
            cumulative_fringe=cumulative_fringe,
            cumulative_taxed=cumulative_taxed,
            pdr_income_ceiling=pdr_income_ceiling,
            rinnovo_flat_rate=rinnovo_flat_rate,
            notte_flat_rate=notte_flat_rate,
            notte_income_ceiling=notte_income_ceiling,
        )
        result: EventEffect = handler(event, ctx)

        items.extend(result.items)
        intents.extend(result.intents)
        total_inps += result.inps_delta
        total_tfr += result.tfr_delta
        total_irpef += result.irpef_delta
        total_substitute += result.substitute_delta
        total_fringe_value += result.fringe_value
        total_fringe_inps += result.fringe_inps
        total_fringe_irpef += result.fringe_irpef
        if result.new_cumulative_fringe is not None:
            cumulative_fringe = result.new_cumulative_fringe
        if result.new_cumulative_taxed is not None:
            cumulative_taxed = result.new_cumulative_taxed

    return (
        _EventTotals(
            inps_base=total_inps,
            tfr_base=total_tfr,
            irpef_base=total_irpef,
            fringe_value=total_fringe_value,
            fringe_inps=total_fringe_inps,
            fringe_irpef=total_fringe_irpef,
            substitute_base=total_substitute,
        ),
        tuple(items),
        _post(tuple(intents), cp, payment_date),
    )
