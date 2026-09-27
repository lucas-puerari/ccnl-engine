"""Handlers for welfare and fringe benefit events."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO, _require_resolution
from ccnl_engine.payroll.application.handlers._context import (
    EventEffect,
    FringeThreshold,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.events import FringeEvent, WelfareEvent
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.domain.pay_items import FringeBenefitItem, WelfareItem

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.variable_pay import FringeBenefitRules

_FRINGE = "fringe_benefit"


def _handle_welfare(event: WelfareEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle welfare benefit events.

    Returns:
        Handler result with WelfareItem posted to NON_CASH_BENEFITS.
    """
    gross = event.amount
    welfare_resolution = _require_resolution(ctx.resolver, "welfare_item", ctx.context)
    item = WelfareItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
    )
    return EventEffect(
        items=[item],
        intents=[
            PostingIntent(
                entry_id=f"ncb_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="welfare_item",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=gross,
                policy_decision_id=welfare_resolution.policy_id,
            )
        ],
    )


def fringe_threshold_of(
    rules: FringeBenefitRules, tax_year: int, *, with_children: bool
) -> FringeThreshold:
    """Return the fringe-benefit threshold of a run and the rule behind it.

    Args:
        rules: Fringe-benefit rules of the tax year.
        tax_year: Tax year of the run, the rule version when the rules
            carry no ruleset.
        with_children: Whether the worker declared a fiscally dependent
            child (L. 207/2024 art. 1 c. 391).

    Returns:
        The higher threshold when ``with_children`` is set, the standard one
        otherwise, with the ruleset identity and source of the rules.
    """
    ruleset = rules.ruleset
    provenance = rules.provenance
    return FringeThreshold(
        amount=(
            rules.threshold_with_children if with_children else rules.threshold_standard
        ),
        with_children=with_children,
        tax_year=tax_year,
        rule=_FRINGE if ruleset is None else ruleset.id,
        rule_version=str(tax_year) if ruleset is None else ruleset.version,
        source=None if provenance is None else provenance.location,
    )


@dataclass(frozen=True)
class FringeAssessment:
    """Taxability of one fringe benefit against the annual threshold.

    The threshold is all or nothing (L. 207/2024 art. 1 c. 390; AdE circ.
    4/E/2025 par. 2.7): once the annual total exceeds it, the whole amount
    of the year is taxable, not only the excess.  The event that crosses
    the threshold therefore also taxes the earlier exempt amounts.

    Attributes:
        threshold: Annual threshold applied.
        amount: Value of this benefit.
        ytd_before: Fringe value of the year before this benefit.
        taxed_before: Part of ``ytd_before`` already taxed.
    """

    threshold: FringeThreshold
    amount: Decimal
    ytd_before: Decimal
    taxed_before: Decimal

    @property
    def ytd_total(self) -> Decimal:
        """Fringe value of the year including this benefit."""
        return self.ytd_before + self.amount

    @property
    def taxable(self) -> Decimal:
        """Amount that becomes taxable with this benefit.

        Zero within the threshold; above it, every amount of the year not
        yet taxed, so it can exceed :attr:`amount`.
        """
        if self.ytd_total > self.threshold.amount:
            return self.ytd_total - self.taxed_before
        return _ZERO

    @property
    def retroactive(self) -> Decimal:
        """Part of :attr:`taxable` that belongs to earlier exempt amounts."""
        return max(self.taxable - self.amount, _ZERO)

    @property
    def reason_code(self) -> str:
        """``within_threshold``, ``above_threshold`` or its retroactive form.

        ``above_threshold_retroactive`` means earlier exempt amounts of the
        year are taxed now with this benefit;
        ``above_threshold`` means only this benefit is taxed.
        """
        if not self.taxable:
            return "within_threshold"
        return "above_threshold_retroactive" if self.retroactive else "above_threshold"

    def decision(self) -> CalculationDecision:
        """Return the ``fringe_benefit`` decision of this benefit.

        Returns:
            A final decision whose amount is :attr:`taxable`.
        """
        threshold = self.threshold
        return CalculationDecision(
            capability=_FRINGE,
            status=CalculationStatus.FINAL,
            reason_code=self.reason_code,
            rule=threshold.rule,
            rule_version=threshold.rule_version,
            inputs={
                "tax_year": str(threshold.tax_year),
                "threshold_annual": threshold.amount,
                "dependent_children": str(threshold.with_children).lower(),
                "amount": self.amount,
                "ytd_before": self.ytd_before,
                "ytd_total": self.ytd_total,
                "taxed_before": self.taxed_before,
                "retroactive_amount": self.retroactive,
            },
            source=threshold.source,
            amount=self.taxable,
        )


def _handle_fringe(event: FringeEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Handle fringe benefit events (with running accumulator update).

    Returns:
        Handler result with the fringe item and its ``fringe_benefit``
        decision, the ledger entry, the contribution-base deltas and the
        updated ``new_cumulative_fringe`` / ``new_cumulative_taxed`` values.
    """
    gross = event.amount
    assessment = FringeAssessment(
        threshold=ctx.fringe_threshold,
        amount=gross,
        ytd_before=ctx.cumulative_fringe,
        taxed_before=ctx.cumulative_taxed,
    )
    taxable = assessment.taxable
    fringe_resolution = _require_resolution(
        ctx.resolver, "fringe_benefit_item", ctx.context
    )
    item = FringeBenefitItem(
        item_id=ctx.evt_id,
        competence_period=ctx.cp,
        payment_date=ctx.payment_date,
        quantity=Decimal(1),
        amount=gross,
        threshold_annual=ctx.fringe_threshold.amount,
        ytd_total=assessment.ytd_total,
        taxable_amount=taxable,
    )
    return EventEffect(
        items=[item],
        intents=[
            PostingIntent(
                entry_id=f"ncb_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind="fringe_benefit_item",
                account=AccountKind.NON_CASH_BENEFITS,
                amount=gross,
                policy_decision_id=fringe_resolution.policy_id,
            )
        ],
        inps_delta=taxable,
        irpef_delta=taxable,
        fringe_value=gross,
        fringe_inps=taxable,
        fringe_irpef=taxable,
        new_cumulative_fringe=assessment.ytd_total,
        new_cumulative_taxed=ctx.cumulative_taxed + taxable,
        decisions=[assessment.decision()],
    )
