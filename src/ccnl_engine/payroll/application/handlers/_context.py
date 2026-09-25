"""Shared context and effect types for event handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.domain.ledger import PostingIntent
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod, PayItem

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver


@dataclass(frozen=True)
class _EventHandlerCtx:
    """Immutable context passed to every event handler.

    Carries all inputs that are invariant across loop iterations, plus the
    current fringe accumulators which may change after each FringeEvent.
    """

    evt_id: str
    cp: CompetencePeriod
    payment_date: date
    resolver: PolicyResolver
    context: PolicyContext
    fringe_threshold: Decimal
    cumulative_fringe: Decimal
    cumulative_taxed: Decimal
    pdr_income_ceiling: Decimal | None = None
    rinnovo_flat_rate: Decimal | None = None
    notte_flat_rate: Decimal | None = None
    notte_income_ceiling: Decimal | None = None


@dataclass
class EventEffect:
    """Accounting outputs and contribution-base deltas from one event.

    Attributes:
        items: Pay items created by the handler.
        intents: Posting intents for ledger projection (converted to entries by
            :func:`~ccnl_engine.payroll.application._posting_service.post`).
        inps_delta: Increase in the INPS contribution base.
        tfr_delta: Increase in the TFR accrual base.
        irpef_delta: Increase in the IRPEF taxable base.
        substitute_delta: Increase in the substitute-tax base (PdR only).
        fringe_value: Total fringe benefit value (FringeEvent only).
        fringe_inps: Fringe INPS-taxable portion (FringeEvent only).
        fringe_irpef: Fringe IRPEF-taxable portion (FringeEvent only).
        new_cumulative_fringe: Updated cumulative fringe YTD (FringeEvent only).
        new_cumulative_taxed: Updated cumulative taxed fringe (FringeEvent only).
    """

    items: list[PayItem] = field(default_factory=list)
    intents: list[PostingIntent] = field(default_factory=list)
    inps_delta: Decimal = _ZERO
    tfr_delta: Decimal = _ZERO
    irpef_delta: Decimal = _ZERO
    substitute_delta: Decimal = _ZERO
    fringe_value: Decimal = _ZERO
    fringe_inps: Decimal = _ZERO
    fringe_irpef: Decimal = _ZERO
    new_cumulative_fringe: Decimal | None = None
    new_cumulative_taxed: Decimal | None = None
