"""Handler of a week of a programme of flexibility: a decision, no pay."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx

if TYPE_CHECKING:
    from ccnl_engine.leave.flexibility.inputs import FlexibilityWeekEvent

__all__ = ["_handle_flexibility_week"]


def _handle_flexibility_week(
    event: FlexibilityWeekEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Decide the week: the month pays it as normal, the permit is credited.

    Returns:
        Handler result with the ``leave`` decision only: final when the CCNL
        sets permits for a flexible week, incomplete otherwise.
    """
    terms = ctx.leave
    rules = None if terms is None else terms.rules
    flex = None if rules is None else rules.flexibility
    decision = CalculationDecision(
        capability="leave",
        status=CalculationStatus.INCOMPLETE
        if flex is None
        else CalculationStatus.FINAL,
        reason_code="flexibility_not_modelled" if flex is None else "flexibility_week",
        rule=(
            "work_rules.leave_rules.flexibility"
            if terms is None
            else f"{terms.ruleset}:work_rules.leave_rules.flexibility"
        ),
        rule_version="unknown" if terms is None else terms.version,
        inputs={
            "hours_worked": event.hours_worked,
            "permit_hours": Decimal(0)
            if flex is None
            else flex.hours_for(event.hours_worked),
        },
        source=None if flex is None else flex.provenance.location,
        amount=Decimal(0),
    )
    return EventEffect(decisions=[decision])
