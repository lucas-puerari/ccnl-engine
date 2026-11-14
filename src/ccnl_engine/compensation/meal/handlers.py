"""Handler of the days owed a meal not given: its valore convenzionale in cash.

CCNL lavoro domestico Art. 14 c. 8 pays the meal not given at its valore
convenzionale, Tabella F (2026: pranzo e/o colazione 2.33 a day).  The cash
is pay and taxable income of the worker, as the board and lodging paid in
cash (:mod:`ccnl_engine.compensation.board.handlers`).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.facade import FixedAllowanceEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _require_resolution

if TYPE_CHECKING:
    from ccnl_engine.compensation.meal.inputs import MealIndennityEvent

__all__ = ["MEAL_INDENNITY", "_handle_meal_indennity"]

#: Reason of the decision on the days owed a meal not given.
MEAL_INDENNITY = "meal_indennity_paid"
_KIND = "fixed_allowance_earning"


def _daily_value(event: MealIndennityEvent, ctx: _EventHandlerCtx) -> Decimal:
    ccnl = ctx.hourly.ccnl
    series = ccnl.parameters.meal_indennity_daily if ccnl is not None else None
    period = series.period_at(event.event_date) if series is not None else None
    if period is None or period.value is None:
        msg = (
            "MealIndennityEvent: the CCNL states no valore convenzionale of the "
            f"meal on {event.event_date.isoformat()}"
        )
        raise InvalidInputError(
            msg, field="MealIndennityEvent", feature="meal_indennity"
        )
    return period.value


def _handle_meal_indennity(
    event: MealIndennityEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the valore convenzionale of the meals owed and not given.

    Returns:
        The cash item, its ledger entry, the IRPEF and INPS deltas and the
        ``meal_indennity`` decision.
    """
    daily = _daily_value(event, ctx)
    amount = money(daily * event.days)
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.context)
    item = FixedAllowanceEarning(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(event.days),
        amount=amount,
    )
    decision = CalculationDecision(
        capability="meal_indennity",
        status=CalculationStatus.FINAL,
        reason_code=MEAL_INDENNITY,
        rule=f"{ctx.hourly.ruleset}:meal_indennity",
        rule_version=ctx.hourly.version,
        amount=amount,
        inputs={"days": Decimal(event.days), "daily_value": daily},
    )
    return EventEffect(
        items=[item],
        intents=[
            PostingIntent(
                entry_id=f"cash_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind=_KIND,
                account=AccountKind.CASH_EARNINGS,
                amount=amount,
                policy_decision_id=resolution.policy_id,
            )
        ],
        inps_delta=amount,
        irpef_delta=amount,
        decisions=[decision],
    )
