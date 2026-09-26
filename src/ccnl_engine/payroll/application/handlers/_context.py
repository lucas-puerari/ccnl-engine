"""Shared context and effect types for event handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.domain.ledger import PostingIntent
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod, PayItem
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.tax.domain.preferential_regime import (
        PreferentialTaxRegime,
    )
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver


@dataclass(frozen=True)
class _EventHandlerCtx:
    """Immutable context passed to every event handler.

    Carries all inputs that are invariant across loop iterations, plus the
    current fringe accumulators which may change after each FringeEvent and
    the work-time regime cap account, which grows after each eligible
    night, holiday or shift supplement.
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
    rinnovo_regime: PreferentialTaxRegime | None = None
    work_time_regime: PreferentialTaxRegime | None = None
    work_time_cap: RegimeCapAccount = field(default_factory=RegimeCapAccount)


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
        substitute_delta: Increase in the PdR substitute-tax base.
        fringe_value: Total fringe benefit value (FringeEvent only).
        fringe_inps: Fringe INPS-taxable portion (FringeEvent only).
        fringe_irpef: Fringe IRPEF-taxable portion (FringeEvent only).
        new_cumulative_fringe: Updated cumulative fringe YTD (FringeEvent only).
        new_cumulative_taxed: Updated cumulative taxed fringe (FringeEvent only).
        regime_cap_used: Part of the annual cap of the work-time regime
            consumed by the event.
        decisions: Decisions taken on the event, e.g. a regime eligibility.
        issues: Conditions raised by the event that lower the result status.
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
    regime_cap_used: Decimal = _ZERO
    decisions: list[CalculationDecision] = field(default_factory=list)
    issues: list[CalculationIssue] = field(default_factory=list)
