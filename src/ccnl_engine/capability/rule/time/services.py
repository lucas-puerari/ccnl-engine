"""The CCNL rules the working-time events of a run were paid with."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.absence.policies import RULE_PATH as ABSENCE_RULE_PATH
from ccnl_engine.event.facade import (
    AbsenceEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.hourly.policies import BASE_PATH
from ccnl_engine.working_time.hourly.services import hourly_terms
from ccnl_engine.working_time.overtime.policies import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)
from ccnl_engine.working_time.services import HOURLY_RATE_DERIVED, resolve_work_event
from ccnl_engine.working_time.supplement.policies import (
    resolve_supplement,
    supplement_rule,
)

if TYPE_CHECKING:
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.period.context.services import RunContext


def _overtime_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the CCNL rules the multipliers and rates of the run came from.

    Returns:
        One entry per distinct band an overtime event without a caller
        multiplier was paid with, and the hourly base when an event took its
        rate from it; empty when every value is the caller's.
    """
    contract = ctx.contract
    bands = CCNLOvertimeBands.of(
        contract.ccnl, contract.tctx.competence.year, ctx.request.level_code
    )
    hourly = hourly_terms(ctx)
    rules: dict[str, Rule] = {}
    events = ctx.request.events
    for event in (e for e in events if isinstance(e, OvertimeEvent)):
        band = resolve_overtime_rate(event, bands).derived_band
        if band is not None:
            rule = bands.rule_of(band)
            rules.setdefault(rule, (rule, band.provenance))
        decisions = resolve_work_event(event, bands, hourly).decisions
        if any(d.reason_code == HOURLY_RATE_DERIVED for d in decisions):
            rules.update((_hourly_base_rule(ctx),))
    return tuple(rules.values())


def _hourly_base_rule(ctx: RunContext) -> tuple[str, Rule]:
    """Return the hourly base rule of the CCNL, keyed by its identifier.

    Returns:
        ``(rule, (rule, record))`` for ``work_rules.time_supplements.
        hourly_base_method`` with its recorded provenance.
    """
    hourly = hourly_terms(ctx)
    supplements = hourly.supplements
    record = None if supplements is None else supplements.hourly_base_provenance
    rule = hourly.rule_of(BASE_PATH)
    return rule, (rule, record)


def _supplement_rules(ctx: RunContext, event_type: type) -> tuple[Rule, ...]:
    """Return the CCNL bands and hourly base the supplements came from.

    Returns:
        One entry per distinct band an event of ``event_type`` without a
        caller amount was paid with, and the hourly base; empty when every
        amount is the caller's.
    """
    hourly = hourly_terms(ctx)
    rules: dict[str, Rule] = {}
    for event in ctx.request.events:
        if (
            isinstance(event, (NightShiftEvent, HolidayWorkEvent, ShiftWorkEvent))
            and isinstance(event, event_type)
            and event.supplement_amount is None
        ):
            band = resolve_supplement(event, hourly).band
            rule = supplement_rule(hourly, band)
            rules.setdefault(rule, (rule, band.provenance))
            rules.update((_hourly_base_rule(ctx),))
    return tuple(rules.values())


def _absence_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the CCNL absence rule and hourly base the deductions came from.

    Returns:
        The absence rule and the hourly base when an absence took the CCNL
        quota; empty when every rate is the caller's.
    """
    if not any(
        isinstance(e, AbsenceEvent) and e.hourly_rate is None
        for e in ctx.request.events
    ):
        return ()
    hourly = hourly_terms(ctx)
    work = ctx.contract.ccnl.work_rules
    absence = None if work is None else work.absence_rules
    rule = hourly.rule_of(ABSENCE_RULE_PATH)
    return (
        (rule, None if absence is None else absence.provenance),
        _hourly_base_rule(ctx)[1],
    )
