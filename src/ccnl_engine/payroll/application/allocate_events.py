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
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
)
from ccnl_engine.payroll.domain.employment_context import EffectiveDateContext
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.domain.ledger import LedgerEntry, PostingIntent
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod, PayItem
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount
from ccnl_engine.payroll.service.regime_eligibility import RegimeFacts

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.tax.domain.preferential_regime import (
        PreferentialTaxRegime,
    )
    from ccnl_engine.payroll.domain.period import PeriodCalculationRequest
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver


_NO_FACTS = RegimeFacts()

#: Catalog feature each event type executes.  A bonus has none of its own:
#: its PdR substitute tax is the ``bonus_pdr`` decision of the run.
EVENT_FEATURES: dict[type, str] = {
    OvertimeEvent: "overtime",
    NightShiftEvent: "night_work",
    HolidayWorkEvent: "holiday_work",
    ShiftWorkEvent: "shift_work",
    AbsenceEvent: "absence",
    SickLeaveEvent: "leave",
    SicknessCaseEvent: "sickness",
    FringeEvent: "fringe_benefit",
    WelfareEvent: "welfare",
    ArrearsEvent: "contract_renewal_arrears",
    BilateralFundEvent: "bilateral_funds",
    TerminationTFREvent: "termination_tfr",
}


def _has_effect(effect: EventEffect) -> bool:
    """Return whether a handler posted a non-zero amount or took a decision.

    Returns:
        ``True`` when ``effect`` changes the payslip or records a decision.
    """
    return bool(effect.decisions) or any(i.amount for i in effect.intents)


@dataclass(frozen=True)
class _EventTotals:
    """Aggregated INPS/TFR/IRPEF bases, decisions and issues of the events.

    ``executed_features`` are the catalog features of the events whose
    handler had an effect (see :func:`_has_effect`).
    """

    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal
    fringe_value: Decimal
    fringe_inps: Decimal
    fringe_irpef: Decimal
    substitute_base: Decimal
    work_time_cap_used: Decimal = _ZERO
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()
    executed_features: frozenset[str] = frozenset()


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
    opening_cap = opening_work_time_cap or RegimeCapAccount()
    work_time_cap = opening_cap
    items: list[PayItem] = []
    intents: list[PostingIntent] = []
    decisions: list[CalculationDecision] = []
    issues: list[CalculationIssue] = []
    executed: set[str] = set()

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
            rinnovo_regime=rinnovo_regime,
            work_time_regime=work_time_regime,
            work_time_cap=work_time_cap,
            worker_facts=worker_facts,
        )
        result: EventEffect = handler(event, ctx)

        items.extend(result.items)
        intents.extend(result.intents)
        decisions.extend(result.decisions)
        issues.extend(result.issues)
        feature = EVENT_FEATURES.get(type(event))
        if feature is not None and _has_effect(result):
            executed.add(feature)
        total_inps += result.inps_delta
        total_tfr += result.tfr_delta
        total_irpef += result.irpef_delta
        total_substitute += result.substitute_delta
        total_fringe_value += result.fringe_value
        total_fringe_inps += result.fringe_inps
        total_fringe_irpef += result.fringe_irpef
        work_time_cap = RegimeCapAccount(work_time_cap.used + result.regime_cap_used)
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
            work_time_cap_used=work_time_cap.used - opening_cap.used,
            decisions=tuple(decisions),
            issues=tuple(issues),
            executed_features=frozenset(executed),
        ),
        tuple(items),
        _post(tuple(intents), cp, payment_date),
    )
