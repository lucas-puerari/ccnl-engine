"""The leave taken decides ``leave``: no pay of its own, a balance consumed."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.leave.handlers import LeaveTerms, _handle_leave_taken
from ccnl_engine.leave.inputs import LeaveTakenEvent
from ccnl_engine.leave.models import FerieAccrual, LeaveRules
from ccnl_engine.leave.types import LeaveBucket

if TYPE_CHECKING:
    from ccnl_engine.event.handlers import _EventHandlerCtx

_EVENT = LeaveTakenEvent(date(2026, 7, 6), LeaveBucket.FERIE, Decimal(10))


def _ctx(terms: LeaveTerms | None) -> _EventHandlerCtx:
    return cast("_EventHandlerCtx", SimpleNamespace(leave=terms))


def test_leave_of_an_accrued_bucket_is_final_and_pays_nothing() -> None:
    """Ferie of a CCNL that accrues them: final, amount zero, no posting."""
    rules = LeaveRules(default_annual_days=Decimal(26), ferie_accrual=FerieAccrual())
    effect = _handle_leave_taken(_EVENT, _ctx(LeaveTerms(rules, "ccnl/x", "1")))

    (decision,) = effect.decisions
    assert (decision.status, decision.reason_code, decision.amount) == (
        CalculationStatus.FINAL,
        "paid_in_monthly_pay",
        Decimal(0),
    )
    assert decision.rule == "ccnl/x:work_rules.leave_rules"
    assert effect.intents == []


def test_leave_without_rules_is_incomplete() -> None:
    """No leave rules in the context: the bucket is not modelled."""
    effect = _handle_leave_taken(_EVENT, _ctx(None))

    (decision,) = effect.decisions
    assert (decision.status, decision.reason_code, decision.rule_version) == (
        CalculationStatus.INCOMPLETE,
        "leave_bucket_not_modelled",
        "unknown",
    )
    assert decision.source is None
