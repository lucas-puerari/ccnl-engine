"""Aggregate variable work events into accounting entries and totals."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application._posting_service import post as _post
from ccnl_engine.payroll.application.handlers._totals import (
    _EventAccumulator,
    _EventTotals,
)
from ccnl_engine.payroll.application.handlers.registry import (
    _HANDLER_REGISTRY,
    _EventHandlerCtx,
    _EventHandlerFn,
)
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.ledger import LedgerEntry
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod, PayItem
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount
from ccnl_engine.payroll.service.regime_eligibility import RegimeFacts
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.period import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.tax.domain.preferential_regime import (
        PreferentialTaxRegime,
    )


_NO_FACTS = RegimeFacts()
_MAX_MONTHLY_HOURS = Decimal(240)


def worker_facts_of(request: PeriodCalculationRequest) -> RegimeFacts:
    """Return the worker facts the regimes of a run are checked against.

    Returns:
        The prior-year income and waivers, the sector of the employment and
        the activity of the employer, as declared on ``request``.
    """
    return RegimeFacts(
        prior_income=request.prior_year.employment_income,
        sector=request.sector,
        activity=request.employer.activity,
        waived_regimes=frozenset(request.prior_year.waived_regimes),
    )


def _check_event_date(
    event: WorkEvent, date_ctx: EffectiveDateContext, idx: int
) -> None:
    """Raise InvalidInputError if event is invalid for the competence period.

    Raises:
        InvalidInputError: When any validation fails.
    """
    if isinstance(event, ArrearsEvent):
        return
    if not date_ctx.contains(event.event_date):
        msg = (
            f"event {idx} ({type(event).__name__}) event_date {event.event_date} "
            f"is outside period [{date_ctx.period_start}, {date_ctx.period_end}]"
        )
        raise InvalidInputError(msg)
    if isinstance(event, AbsenceEvent) and (
        event.hours <= _ZERO or event.hours > _MAX_MONTHLY_HOURS
    ):
        msg = (
            f"event {idx} (AbsenceEvent) hours={event.hours} is invalid: "
            f"must be > 0 and <= {_MAX_MONTHLY_HOURS} per period"
        )
        raise InvalidInputError(msg)


def _handler_of(event: WorkEvent) -> _EventHandlerFn:
    """Return the registered handler of ``event``.

    Returns:
        The handler function of the event type.

    Raises:
        TypeError: When an event type has no registered handler (should never
            occur in practice; indicates a missing registry entry).
    """
    handler = _HANDLER_REGISTRY.get(type(event))
    if handler is None:  # pragma: no cover
        msg = f"No handler registered for event type {type(event).__name__}"
        raise TypeError(msg)
    return handler


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
    rinnovo_regime: PreferentialTaxRegime | None = None,
    work_time_regime: PreferentialTaxRegime | None = None,
    opening_work_time_cap: RegimeCapAccount | None = None,
    worker_facts: RegimeFacts = _NO_FACTS,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    The work-time regime cap starts from ``opening_work_time_cap`` and grows
    after each eligible supplement, so later events of the run only get the
    substitute rate on what is left of the annual cap.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.
    """
    opening_cap = opening_work_time_cap or RegimeCapAccount()
    acc = _EventAccumulator(
        opening_fringe_ytd, opening_fringe_taxed, opening_cap, opening_cap
    )
    base_ctx = _EventHandlerCtx(
        evt_id="",
        cp=cp,
        payment_date=payment_date,
        resolver=resolver,
        context=context,
        fringe_threshold=fringe_threshold,
        cumulative_fringe=acc.cumulative_fringe,
        cumulative_taxed=acc.cumulative_taxed,
        pdr_income_ceiling=pdr_income_ceiling,
        rinnovo_regime=rinnovo_regime,
        work_time_regime=work_time_regime,
        work_time_cap=acc.work_time_cap,
        worker_facts=worker_facts,
    )
    for i, event in enumerate(events):
        _check_event_date(event, date_ctx, i)
        handler = _handler_of(event)
        ctx = replace(
            base_ctx,
            evt_id=f"{tag}_evt{i}",
            cumulative_fringe=acc.cumulative_fringe,
            cumulative_taxed=acc.cumulative_taxed,
            work_time_cap=acc.work_time_cap,
        )
        acc.add(event, handler(event, ctx))
    return (
        acc.totals(),
        tuple(acc.items),
        _post(tuple(acc.intents), cp, payment_date),
    )
