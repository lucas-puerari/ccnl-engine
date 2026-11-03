"""The credit line, decision and issue of the trattamento integrativo speciale.

The amount is not income (L. 199/2025 art. 1 c. 18): it is posted as a tax
credit item on the credits account, outside the INPS, TFR and IRPEF bases,
which the withholding agent recovers in F24 compensation (c. 21).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.ledger.models import AccountKind, PostingIntent
from ccnl_engine.ledger.remittance.models import SPECIAL_SUPPLEMENT_CREDIT
from ccnl_engine.pay_item.facade import TaxCreditItem
from ccnl_engine.pay_item.services import _require_resolution
from ccnl_engine.working_time.tourism.rules import special_supplement

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.event.handlers import _EventHandlerCtx
    from ccnl_engine.pay_item.facade import PayItem

__all__ = ["CAPABILITY", "SupplementLines", "special_supplement_lines"]

#: Capability of the trattamento integrativo speciale.
CAPABILITY = "special_supplement"
_KIND = "tax_credit_item"
_RULE = "law/special-supplement:l199-2025-art1-c18"
_FACTS = {
    "activity_unknown": (
        "activity",
        (
            "the trattamento integrativo speciale (L. 199/2025 art. 1 c. 18) is "
            "due only in food service, tourism and thermal establishments: "
            "state EmployerProfile.activity"
        ),
    ),
    "income_unknown": (
        "employment_income",
        (
            "the trattamento integrativo speciale needs the 2025 employment "
            "income the worker attests (c. 19-20): state "
            "PriorYearTaxFacts.employment_income"
        ),
    ),
    "base_unknown": (
        None,
        (
            "the trattamento integrativo speciale is 15% of the gross pay of "
            "the night hours, which needs their hours and the CCNL hourly "
            "base: state the hours of the event"
        ),
    ),
}


@dataclass
class SupplementLines:
    """What the supplement adds to the effect of an event."""

    items: list[PayItem] = field(default_factory=list)
    intents: list[PostingIntent] = field(default_factory=list)
    decisions: list[CalculationDecision] = field(default_factory=list)
    issues: list[CalculationIssue] = field(default_factory=list)


def special_supplement_lines(
    event: object,
    gross: Decimal,
    decisions: Iterable[CalculationDecision],
    ctx: _EventHandlerCtx,
) -> SupplementLines:
    """Return the credit line of the supplement of ``event``, if any.

    Returns:
        Nothing when no supplement applies; the decision not to pay it above
        the income cap; the credit item, its posting and decision; or the
        issue of the fact it lacks.
    """
    found = special_supplement(event, gross, decisions, ctx.worker_facts)
    if found is None:
        return SupplementLines()
    if found.reason in _FACTS:
        fact, message = _FACTS[found.reason]
        issue = CalculationIssue(
            code=f"special_supplement_{found.reason}",
            message=message,
            status=CalculationStatus.INCOMPLETE,
            capability=CAPABILITY,
            fact=fact,
            cause=IssueCause.FACT if fact else IssueCause.CONDITION,
        )
        return SupplementLines(issues=[issue])
    amount = found.amount if found.amount is not None else Decimal(0)
    decision = CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code=found.reason,
        rule=_RULE,
        rule_version="2026",
        inputs={"base": found.base or Decimal(0), "rate": Decimal("0.15")},
        amount=amount,
    )
    if not amount:
        return SupplementLines(decisions=[decision])
    item_id = f"{ctx.evt_id}_special_supplement"
    resolution = _require_resolution(ctx.resolver, _KIND, ctx.context)
    item = TaxCreditItem(
        item_id=item_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=amount,
        source="L. 199/2025 art. 1 c. 18",
    )
    intent = PostingIntent(
        entry_id=f"special_supplement_{ctx.evt_id}",
        source_item_id=item_id,
        pay_item_kind=_KIND,
        account=AccountKind.CREDITS,
        amount=amount,
        policy_decision_id=resolution.policy_id,
        remittance_code=SPECIAL_SUPPLEMENT_CREDIT,
    )
    return SupplementLines([item], [intent], [decision])
