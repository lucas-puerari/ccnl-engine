"""Handler of the travel allowance (indennità di trasferta)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import rule_scope
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.facade import TravelAllowanceItem
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _ZERO, _require_resolution

if TYPE_CHECKING:
    from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
    from ccnl_engine.variable_pay.models import TravelAllowanceRules
    from ccnl_engine.working_time.models import CcnlTravelAllowance

__all__ = ["TravelAllowanceAssessment", "TravelTerms", "_handle_travel_allowance"]

_FEATURE = "travel_allowance"
_KIND = "travel_allowance_item"


@dataclass(frozen=True)
class TravelAllowanceAssessment:
    """Exempt and taxable parts of one block of trasferta days.

    Attributes:
        event: The block of days.
        rules: Daily caps of art. 51 c. 5 TUIR of the tax year.
        tax_year: Tax year of the run, the rule version without a ruleset.
        daily_amount: Allowance of each day, the CCNL's for its hours away;
            ``None`` takes the event's.
    """

    event: TravelAllowanceEvent
    rules: TravelAllowanceRules
    tax_year: int
    daily_amount: Decimal | None = None

    @property
    def daily(self) -> Decimal:
        """Allowance of each day."""
        if self.daily_amount is not None:
            return self.daily_amount
        return self.event.daily_amount or _ZERO

    @property
    def cap(self) -> Decimal:
        """Exempt daily cap: zero within the comune."""
        event = self.event
        if not event.outside_municipality:
            return _ZERO
        return self.rules.cap(abroad=event.abroad, meals_lodging=event.meals_lodging)

    @property
    def gross(self) -> Decimal:
        """Allowance of the block: the days times the daily amount."""
        return money(self.daily * self.event.days)

    @property
    def exempt(self) -> Decimal:
        """Part within the cap, left out of the IRPEF and INPS bases."""
        return money(min(self.daily, self.cap) * self.event.days)

    @property
    def taxable(self) -> Decimal:
        """Part above the cap."""
        return self.gross - self.exempt

    @property
    def reason_code(self) -> str:
        """Why the part is exempt or not."""
        if not self.event.outside_municipality:
            return "within_municipality"
        return "above_cap" if self.taxable else "within_cap"

    def decision(self) -> CalculationDecision:
        """Return the ``travel_allowance`` decision of the block.

        Returns:
            A final decision whose amount is the taxable part.
        """
        rules, event = self.rules, self.event
        ruleset = rules.ruleset
        return CalculationDecision(
            capability=_FEATURE,
            status=CalculationStatus.FINAL,
            reason_code=self.reason_code,
            rule=_FEATURE if ruleset is None else ruleset.id,
            rule_version=str(self.tax_year) if ruleset is None else ruleset.version,
            inputs={
                "days": str(event.days),
                "daily_amount": self.daily,
                "outside_municipality": str(event.outside_municipality).lower(),
                "abroad": str(event.abroad).lower(),
                "meals_lodging": event.meals_lodging,
                "daily_cap": self.cap,
                "exempt_amount": self.exempt,
                "hours_away": "none" if event.hours_away is None else event.hours_away,
            },
            source=None if rules.provenance is None else rules.provenance.location,
            amount=self.taxable,
        )


@dataclass(frozen=True)
class TravelTerms:
    """The CCNL travel allowance a run pays a trasferta with.

    Attributes:
        rules: CCNL amounts and TFR rule, ``None`` when the CCNL has none.
        ruleset: Ruleset identifier of the CCNL.
    """

    rules: CcnlTravelAllowance | None
    ruleset: str


def _daily_amount(event: TravelAllowanceEvent, terms: TravelTerms | None) -> Decimal:
    """Return the allowance of each day: the event's or the CCNL's.

    Returns:
        ``daily_amount``, else the CCNL amount of the span of ``hours_away``
        (zero below the first span).

    Raises:
        MissingRuleError: When the event has no amount and the CCNL none.
    """
    if event.daily_amount is not None:
        return event.daily_amount
    rules = None if terms is None else terms.rules
    if terms is None or rules is None:
        msg = "the CCNL of the run has no travel allowance amounts: state daily_amount"
        raise MissingRuleError(msg, as_of=event.event_date, feature=_FEATURE)
    band = rules.band_of(event.hours_away or _ZERO)
    if band is None:
        return _ZERO
    series = band.abroad if event.abroad else band.italy
    with rule_scope(ruleset=terms.ruleset, feature=_FEATURE):
        return series.value_at(event.event_date)


def _night(event: TravelAllowanceEvent, terms: TravelTerms | None) -> Decimal:
    """Return the CCNL night allowance of the days of the event.

    Returns:
        The amount for each day of the hours the CCNL requires, zero
        without the allowance or the hours.
    """
    if terms is None or terms.rules is None:
        return _ZERO
    rules, hours = terms.rules, event.hours_away
    night = rules.night_allowance
    if night is None or hours is None or hours < rules.night_from_hours:
        return _ZERO
    with rule_scope(ruleset=terms.ruleset, feature=_FEATURE):
        return money(night.value_at(event.event_date) * event.days)


def _tfr_base(event: TravelAllowanceEvent, terms: TravelTerms | None) -> str:
    """Return what of the allowance enters the TFR base.

    Returns:
        The event's choice, else the CCNL's.

    Raises:
        MissingRuleError: When neither states it.
    """
    if event.tfr_base is not None:
        return event.tfr_base
    rules = None if terms is None else terms.rules
    if rules is None:
        msg = (
            "the CCNL states no TFR rule for the allowance (art. 2120 c.c. "
            "leaves it to the CCNL)"
        )
        raise MissingRuleError(
            msg,
            as_of=event.event_date,
            feature=_FEATURE,
            remediation="Pass TravelAllowanceEvent.tfr_base.",
        )
    return rules.tfr_base


def _handle_travel_allowance(
    event: TravelAllowanceEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle a block of trasferta days.

    The whole allowance is cash pay; only the part above the cap enters the
    IRPEF and INPS bases, and the TFR base what the event or the CCNL says.

    Returns:
        Handler result with the travel allowance item, its ledger entry, the
        base deltas and the ``travel_allowance`` decision.

    Raises:
        ValueError: When the run carries no travel allowance rules.
    """
    if ctx.travel_allowance is None:
        msg = "the travel allowance rules of the tax year are not loaded"
        raise ValueError(msg)
    tfr_base = _tfr_base(event, ctx.ccnl_travel)
    assessment = TravelAllowanceAssessment(
        event,
        ctx.travel_allowance,
        ctx.tax_year,
        _daily_amount(event, ctx.ccnl_travel),
    )
    gross, taxable = assessment.gross, assessment.taxable
    tfr = {"none": _ZERO, "whole": gross, "above_exempt": taxable}[tfr_base]
    night = _night(event, ctx.ccnl_travel)
    gross, taxable, tfr = gross + night, taxable + night, tfr + night
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.context)
    item = TravelAllowanceItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(event.days),
        amount=gross,
        exempt_amount=assessment.exempt,
        taxable_amount=taxable,
    )
    decision = assessment.decision()
    decision = replace(
        decision,
        inputs={**decision.inputs, "tfr_base": tfr_base, "night_allowance": night},
        amount=taxable,
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
        inps_delta=taxable,
        irpef_delta=taxable,
        tfr_delta=tfr,
        decisions=[decision],
    )
