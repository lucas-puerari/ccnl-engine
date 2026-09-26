"""Apply a preferential tax regime to the pay item of one event."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.events import BonusEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.service.regime_eligibility import (
    RegimeFacts,
    assess_regime,
    sector_of_tax_sector,
)
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.handlers._context import _EventHandlerCtx
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )

_ZERO = Decimal(0)


@dataclass(frozen=True, slots=True)
class RegimeOutcome:
    """Postings and records of a regime applied to one pay item.

    Attributes:
        intents: Substitute-tax posting, empty when nothing is eligible.
        ordinary_amount: Part of the pay item left to ordinary IRPEF.
        decision: The eligibility decision taken.
        issue: Provisional issue when the eligibility is unknown.
    """

    intents: tuple[PostingIntent, ...]
    ordinary_amount: Decimal
    decision: CalculationDecision
    issue: CalculationIssue | None


def apply_renewal_regime(
    event: object,
    kind: str,
    substitute: bool,
    ctx: _EventHandlerCtx,
    gross: Decimal,
    policy_id: str,
) -> RegimeOutcome | None:
    """Assess a contract-renewal increment and post its substitute tax.

    The worker facts come from the request: the prior-year income and the
    renunciation from the :class:`BonusEvent`, the sector from the CCNL tax
    sector of the policy context.

    Args:
        event: The event being handled.
        kind: Pay item kind resolved for the event.
        substitute: Whether the accounting policy routes the kind to a
            substitute tax.
        ctx: Handler context carrying the renewal regime.
        gross: Amount of the pay item.
        policy_id: Accounting policy of the pay item, cited by the posting.

    Returns:
        The outcome, or ``None`` when the event is not covered by the
        renewal regime.
    """
    regime = ctx.rinnovo_regime
    if not (
        isinstance(event, BonusEvent)
        and substitute
        and regime is not None
        and kind in regime.eligible_kinds
    ):
        return None
    facts = RegimeFacts(
        prior_income=event.prior_income,
        sector=sector_of_tax_sector(ctx.context.sector),
        waived=event.substitute_tax_waived,
    )
    assessment = assess_regime(regime, facts, gross, ctx.context.year)
    tax = money(assessment.eligible_amount * regime.flat_tax_rate)
    intents: tuple[PostingIntent, ...] = ()
    if tax > _ZERO:
        intents = (
            PostingIntent(
                entry_id=f"{regime.regime_id}_tax_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind=kind,
                account=AccountKind.SUBSTITUTE_TAX,
                amount=tax,
                policy_decision_id=policy_id,
            ),
        )
    return RegimeOutcome(
        intents=intents,
        ordinary_amount=assessment.ordinary_amount,
        decision=assessment.decision(tax),
        issue=assessment.issue(),
    )
