"""Handler of the standby pay (indennità di reperibilità)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.facade import StandbyEarning
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _ZERO, _require_resolution
from ccnl_engine.working_time.standby.inputs import StandbyKind

if TYPE_CHECKING:
    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.working_time.standby.inputs import StandbyEvent
    from ccnl_engine.working_time.standby.models import StandbyRates, StandbyRules

__all__ = ["StandbyTerms", "_handle_standby"]

_FEATURE = "standby"
_KIND = "standby_earning"


@dataclass(frozen=True)
class StandbyTerms:
    """The CCNL standby rules a run pays standby with.

    Attributes:
        rules: Standby rules of the CCNL, ``None`` when it has none.
        level_code: Level of the worker, selecting the band.
        ruleset: Ruleset identifier of the CCNL.
        version: Ruleset version.
    """

    rules: StandbyRules | None
    level_code: str
    ruleset: str
    version: str


def _series(rates: StandbyRates, kind: StandbyKind) -> TimeSeries:
    if kind is StandbyKind.HOURS:
        return rates.worked_day
    series: TimeSeries = getattr(rates, kind.value)
    return series


def _turn_pay(
    event: StandbyEvent, rules: StandbyRules, ruleset: str
) -> tuple[Decimal, Decimal]:
    """Return the complete-turn hourly rate and the prorated turn payment.

    Returns:
        The hourly rate and the rounded turn payment.

    Raises:
        MissingRuleError: When the event does not describe a permitted turn.
    """
    duration = rules.turn_hours
    minimum = rules.minimum_turn_hours
    if (
        event.kind is not StandbyKind.HOURS
        or event.calls
        or duration is None
        or minimum is None
        or not minimum <= event.quantity <= duration
    ):
        msg = "the CCNL turn rate requires a permitted turn duration without calls"
        raise MissingRuleError(
            msg,
            as_of=event.event_date,
            feature=_FEATURE,
            ruleset=ruleset,
            remediation=(
                "state a permitted on-call turn; report interventions separately"
            ),
        )
    assert rules.turn_rate is not None
    with rule_scope(ruleset=ruleset, feature=_FEATURE):
        complete_rate = rules.turn_rate.value_at(event.event_date)
    rate = complete_rate / duration
    multiplier = 1 + rules.short_turn_premium if event.quantity < duration else 1
    return rate, money(rate * event.quantity * multiplier)


def _handle_standby(event: StandbyEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle a standby period at the CCNL rates of the worker's level.

    Returns:
        Handler result with the standby item, its ledger entry, the base
        deltas and the ``standby`` decision.

    Raises:
        MissingRuleError: When the CCNL has no standby rules, the level is
            in no band, or no rate is in force on the event date.
    """
    terms = ctx.standby
    rules = None if terms is None else terms.rules
    band = None if rules is None or terms is None else rules.band_of(terms.level_code)
    turn = rules is not None and rules.turn_rate is not None
    if terms is None or rules is None or (band is None and not turn):
        detail = (
            "the CCNL of the run has no standby rates"
            if terms is None or rules is None
            else f"level {terms.level_code!r} is in no standby band of the CCNL"
        )
        raise MissingRuleError(
            detail,
            as_of=event.event_date,
            feature=_FEATURE,
            ruleset=None if terms is None else terms.ruleset,
            remediation="pay the standby as a bonus with the CCNL amount",
        )
    if turn:
        rate, standby = _turn_pay(event, rules, terms.ruleset)
        fee = _ZERO
    else:
        assert band is not None
        assert rules.call_fee is not None
        with rule_scope(ruleset=terms.ruleset, feature=_FEATURE):
            rate = _series(band.rates, event.kind).value_at(event.event_date)
            fee = rules.call_fee.value_at(event.event_date)
        if event.kind is StandbyKind.HOURS:
            assert rules.hourly_divisor is not None
            rate /= rules.hourly_divisor
        standby = money(rate * event.quantity)
    call_pay = money(fee * event.calls)
    gross = standby + call_pay
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.context)
    item = StandbyEarning(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=event.quantity,
        amount=gross,
    )
    decision = CalculationDecision(
        capability=_FEATURE,
        status=CalculationStatus.FINAL,
        reason_code="ccnl_standby_rate_applied",
        rule=terms.ruleset,
        rule_version=terms.version,
        inputs={
            "level_code": terms.level_code,
            "kind": event.kind.value,
            "quantity": event.quantity,
            "rate": rate,
            "calls": str(event.calls),
            "call_fee": fee,
            "in_tfr_base": str(rules.in_tfr_base).lower(),
        },
        source=None if rules.provenance is None else rules.provenance.location,
        amount=gross,
    )
    return EventEffect(
        items=[item],
        intents=[
            PostingIntent(
                entry_id=f"cash_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind=_KIND,
                account=AccountKind.CASH_EARNINGS,
                amount=gross,
                policy_decision_id=resolution.policy_id,
            )
        ],
        inps_delta=gross,
        irpef_delta=gross,
        tfr_delta=gross if rules.in_tfr_base else _ZERO,
        decisions=[decision],
    )
