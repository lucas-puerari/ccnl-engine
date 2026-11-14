"""A week of flexibility decides ``leave``: no pay, a permit credited."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.leave.flexibility.handlers import _handle_flexibility_week
from ccnl_engine.leave.flexibility.inputs import FlexibilityWeekEvent
from ccnl_engine.leave.handlers import LeaveTerms
from ccnl_engine.leave.models import LeaveRules

if TYPE_CHECKING:
    from ccnl_engine.event.handlers import _EventHandlerCtx

_EVENT = FlexibilityWeekEvent(date(2026, 3, 9), Decimal(46))


def _ctx(terms: LeaveTerms | None) -> _EventHandlerCtx:
    return cast("_EventHandlerCtx", SimpleNamespace(leave=terms))


def test_a_week_of_studi_earns_an_hour() -> None:
    """Studi art. 92: 46 hours earn 60 minutes, final, nothing paid."""
    work = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert work is not None
    rules = work.leave_rules
    assert rules is not None
    effect = _handle_flexibility_week(_EVENT, _ctx(LeaveTerms(rules, "ccnl/s", "3")))

    (decision,) = effect.decisions
    assert (decision.status, decision.reason_code, decision.amount) == (
        CalculationStatus.FINAL,
        "flexibility_week",
        Decimal(0),
    )
    assert decision.rule == "ccnl/s:work_rules.leave_rules.flexibility"
    assert decision.inputs == {"hours_worked": Decimal(46), "permit_hours": Decimal(1)}


def test_a_ccnl_without_flexibility_is_incomplete() -> None:
    """No flexibility rule, or no leave rules at all."""
    rules = LeaveRules(default_annual_days=Decimal(26))
    for terms in (LeaveTerms(rules, "ccnl/x", "1"), None):
        (decision,) = _handle_flexibility_week(_EVENT, _ctx(terms)).decisions
        assert (decision.status, decision.reason_code) == (
            CalculationStatus.INCOMPLETE,
            "flexibility_not_modelled",
        )
        assert decision.inputs["permit_hours"] == Decimal(0)
