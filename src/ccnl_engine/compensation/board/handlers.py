"""Handler of the days without board and lodging: their value in cash.

The value of a day is the monthly value of the benefits in kind of the pay
chain over 30 (CCNL lavoro domestico Art. 36 c. 3: "valori mensili =
giornalieri x 30"; Tabella F 2026: 2.33 + 2.33 + 2.00 = 6.66 a day, 199.80
a month).  The cash is pay and taxable income of the worker.  It does not
add to the TFR base: the value in kind of the whole month already enters it
(Art. 41 c. 1), and the cash only replaces it on those days.
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
    from ccnl_engine.compensation.board.inputs import BoardLodgingEvent

__all__ = ["SUBSTITUTE", "_handle_board_lodging"]

#: Reason of the decision on the days without board and lodging.
SUBSTITUTE = "board_lodging_substitute"
_KIND = "fixed_allowance_earning"
_DAYS = Decimal(30)


def _handle_board_lodging(
    event: BoardLodgingEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the value of the board and lodging of the days without them.

    Returns:
        The cash item, its ledger entry, the IRPEF and INPS deltas and the
        ``board_lodging`` decision.

    Raises:
        InvalidInputError: When the pay chain of the worker provides no
            benefit in kind.
    """
    chain = ctx.hourly.chain
    if chain is None or not chain.in_kind_total:
        msg = (
            "BoardLodgingEvent: the pay of the worker provides no board and "
            "lodging in kind"
        )
        raise InvalidInputError(msg, field="BoardLodgingEvent", feature="board_lodging")
    monthly = chain.in_kind_total
    amount = money(monthly * event.days / _DAYS)
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.context)
    item = FixedAllowanceEarning(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(event.days),
        amount=amount,
    )
    decision = CalculationDecision(
        capability="board_lodging",
        status=CalculationStatus.FINAL,
        reason_code=SUBSTITUTE,
        rule=f"{ctx.hourly.ruleset}:board_lodging",
        rule_version=ctx.hourly.version,
        amount=amount,
        inputs={
            "days": Decimal(event.days),
            "monthly_in_kind": monthly,
            "daily_value": monthly / _DAYS,
        },
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
