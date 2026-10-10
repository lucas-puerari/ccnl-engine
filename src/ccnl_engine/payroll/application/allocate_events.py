"""Aggregate variable work events into accounting entries and totals."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application._posting_service import post as _post
from ccnl_engine.payroll.application.handlers._overtime_rate import CCNLOvertimeBands
from ccnl_engine.payroll.application.handlers._sickness_month import (
    check_absences_off_sick_days,
    month_issues,
)
from ccnl_engine.payroll.application.handlers._sickness_terms import SicknessTerms
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
from ccnl_engine.payroll.domain.sickness import SicknessEpisode
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount
from ccnl_engine.payroll.service.regime_eligibility import RegimeFacts

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.application.handlers._context import FringeThreshold
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.tax.regime.models import (
        PreferentialTaxRegime,
    )


_NO_FACTS = RegimeFacts()
_MAX_MONTHLY_HOURS = Decimal(240)


def worker_facts_of(
    request: PeriodCalculationRequest, *, withholding_agent: bool
) -> RegimeFacts:
    """Return the worker facts the regimes of a run are checked against.

    Args:
        request: The period calculation request.
        withholding_agent: Whether the employer withholds tax; the regimes
            are applied only by a withholding agent.

    Returns:
        The prior-year income and waivers, the sector of the employment and
        the activity of the employer, as declared on ``request``.
    """
    return RegimeFacts(
        prior_income=request.prior_year.employment_income,
        sector=request.sector,
        activity=request.employer.activity,
        waived_regimes=frozenset(request.prior_year.waived_regimes),
        withholding_agent=withholding_agent,
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
    if isinstance(event, SicknessEpisode):
        if event.within(date_ctx.period_start, date_ctx.period_end) is None:
            msg = (
                f"event {idx} (SicknessEpisode) from {event.started_on} to "
                f"{event.ended_on} does not touch period "
                f"[{date_ctx.period_start}, {date_ctx.period_end}]"
            )
            raise InvalidInputError(msg)
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


def _processing_order(
    events: tuple[WorkEvent, ...],
) -> list[tuple[int, WorkEvent]]:
    """Return the events with their index, sickness episodes by first day.

    The sickness episodes fill the places the episodes hold in ``events``,
    in the order of their first day, so the sick days a month counts past
    its pay are always its last ones, whatever order the caller gave; every
    other event keeps its place.

    Returns:
        ``(index in events, event)`` pairs in the order they are processed.
    """
    order: list[tuple[int, WorkEvent]] = list(enumerate(events))
    places = [k for k, event in order if isinstance(event, SicknessEpisode)]
    episodes = sorted(
        ((k, e) for k, e in order if isinstance(e, SicknessEpisode)),
        key=lambda pair: pair[1].started_on,
    )
    for place, episode in zip(places, episodes, strict=True):
        order[place] = episode
    return order


def _run_handlers(
    events: tuple[WorkEvent, ...],
    base_ctx: _EventHandlerCtx,
    run: tuple[str, EffectiveDateContext],
    acc: _EventAccumulator,
) -> None:
    """Run the handler of each event, then check the sick days of the month.

    Each handler sees the fringe totals, the work-time cap and the sickness
    episodes and units the earlier events recorded.  An unpaid absence on a
    sick day is rejected before any handler runs.
    """
    tag, date_ctx = run
    terms = base_ctx.sickness
    check_absences_off_sick_days(events)
    for i, event in _processing_order(events):
        _check_event_date(event, date_ctx, i)
        handler = _handler_of(event)
        ctx = replace(
            base_ctx,
            evt_id=f"{tag}_evt{i}",
            cumulative_fringe=acc.cumulative_fringe,
            cumulative_taxed=acc.cumulative_taxed,
            work_time_cap=acc.work_time_cap,
            sickness=replace(terms, history=acc.sickness, counted=acc.sick_units),
        )
        acc.add(event, handler(event, ctx))
    acc.issues.extend(
        month_issues(events, terms, frozenset(acc.sick_days), acc.sick_units)
    )


def _process_events(
    events: tuple[WorkEvent, ...],
    cp: CompetencePeriod,
    payment_date: date,
    tag: str,
    date_ctx: EffectiveDateContext,
    resolver: PolicyResolver,
    context: PolicyContext,
    fringe_threshold: FringeThreshold,
    opening_fringe_ytd: Decimal = _ZERO,
    opening_fringe_taxed: Decimal = _ZERO,
    pdr_income_ceiling: Decimal | None = None,
    rinnovo_regime: PreferentialTaxRegime | None = None,
    work_time_regime: PreferentialTaxRegime | None = None,
    opening_work_time_cap: RegimeCapAccount | None = None,
    worker_facts: RegimeFacts = _NO_FACTS,
    overtime_bands: CCNLOvertimeBands | None = None,
    sickness: SicknessTerms | None = None,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Translate variable work events into accounting entries and aggregated totals.

    The work-time regime cap starts from ``opening_work_time_cap`` and grows
    after each eligible supplement, so later events of the run only get the
    substitute rate on what is left of the annual cap.  ``overtime_bands``
    are the CCNL bands an overtime event without a multiplier is paid with;
    without them such an event is rejected.  ``sickness`` holds the rules
    and recorded episodes a sickness episode is paid with; each episode and
    its deducted units are recorded before the next event.

    Returns:
        Tuple of ``(_EventTotals, pay_items, ledger_entries)``.
    """
    opening_cap = opening_work_time_cap or RegimeCapAccount()
    terms = sickness or SicknessTerms()
    acc = _EventAccumulator(
        opening_fringe_ytd, opening_fringe_taxed, opening_cap, opening_cap
    )
    acc.sickness = terms.history
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
        overtime_bands=overtime_bands or CCNLOvertimeBands(),
        sickness=terms,
    )
    _run_handlers(events, base_ctx, (tag, date_ctx), acc)
    return (
        acc.totals(),
        tuple(acc.items),
        _post(tuple(acc.intents), cp, payment_date),
    )
