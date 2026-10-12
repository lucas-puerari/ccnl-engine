"""Handler of the travel allowance (indennità di trasferta)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.event.handlers import EventEffect, _EventHandlerCtx
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.pay_item.facade import TravelAllowanceItem
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.pay_item.services import _ZERO, _require_resolution

if TYPE_CHECKING:
    from ccnl_engine.variable_pay.inputs import TravelAllowanceEvent
    from ccnl_engine.variable_pay.models import TravelAllowanceRules

__all__ = ["TravelAllowanceAssessment", "_handle_travel_allowance"]

_FEATURE = "travel_allowance"
_KIND = "travel_allowance_item"


@dataclass(frozen=True)
class TravelAllowanceAssessment:
    """Exempt and taxable parts of one block of trasferta days.

    Attributes:
        event: The block of days.
        rules: Daily caps of art. 51 c. 5 TUIR of the tax year.
        tax_year: Tax year of the run, the rule version without a ruleset.
    """

    event: TravelAllowanceEvent
    rules: TravelAllowanceRules
    tax_year: int

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
        return money(self.event.daily_amount * self.event.days)

    @property
    def exempt(self) -> Decimal:
        """Part within the cap, left out of the IRPEF and INPS bases."""
        return money(min(self.event.daily_amount, self.cap) * self.event.days)

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
                "daily_amount": event.daily_amount,
                "outside_municipality": str(event.outside_municipality).lower(),
                "abroad": str(event.abroad).lower(),
                "meals_lodging": event.meals_lodging,
                "daily_cap": self.cap,
                "exempt_amount": self.exempt,
                "in_tfr_base": str(event.in_tfr_base).lower(),
            },
            source=None if rules.provenance is None else rules.provenance.location,
            amount=self.taxable,
        )


def _handle_travel_allowance(
    event: TravelAllowanceEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Handle a block of trasferta days.

    The whole allowance is cash pay; only the part above the cap enters the
    IRPEF and INPS bases, and the whole of it the TFR base when the event
    says so.

    Returns:
        Handler result with the travel allowance item, its ledger entry, the
        base deltas and the ``travel_allowance`` decision.

    Raises:
        ValueError: When the run carries no travel allowance rules.
    """
    if ctx.travel_allowance is None:
        msg = "the travel allowance rules of the tax year are not loaded"
        raise ValueError(msg)
    assessment = TravelAllowanceAssessment(event, ctx.travel_allowance, ctx.tax_year)
    gross, taxable = assessment.gross, assessment.taxable
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
        tfr_delta=gross if event.in_tfr_base else _ZERO,
        decisions=[assessment.decision()],
    )
