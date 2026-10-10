"""Shared context and effect types for event handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.facade import CompetencePeriod, PayItem
from ccnl_engine.payroll.event.policies_overtime_rate import CCNLOvertimeBands
from ccnl_engine.payroll.ledger.models import PostingIntent
from ccnl_engine.payroll.period.services_shared import _ZERO
from ccnl_engine.payroll.sickness.rules_terms import SicknessTerms
from ccnl_engine.payroll.state.models_ytd_account import RegimeCapAccount
from ccnl_engine.payroll.taxation.rules_regime_eligibility import RegimeFacts

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.amount.models_treatment import EventTreatment
    from ccnl_engine.payroll.amount.policies import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.assurance.models_decision import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.sickness.models import SicknessEpisode
    from ccnl_engine.provenance.source.models import SourceLocation
    from ccnl_engine.tax.regime.models import (
        PreferentialTaxRegime,
    )


@dataclass(frozen=True)
class FringeThreshold:
    """Annual fringe-benefit threshold applied in a run, with its rule.

    Attributes:
        amount: Annual exemption threshold in EUR: the standard one unless
            a child is known to be in the condition of art. 12 c. 2 TUIR.
        with_children: Whether a child of the family composition is in the
            condition of art. 12 c. 2 TUIR, which selects the higher
            threshold; ``None`` when unknown.
        higher: The threshold with such a child, which an unknown
            ``with_children`` may select.
        missing_fact: The fact that leaves ``with_children`` unknown:
            ``"own_income"`` of a child, or ``None`` without a family
            composition.
        tax_year: Tax year the threshold belongs to.
        rule: Identifier of the rule the threshold comes from.
        rule_version: Version of that rule.
        source: Normative source of the threshold, when recorded.
    """

    amount: Decimal
    with_children: bool | None
    higher: Decimal
    tax_year: int
    rule: str
    rule_version: str
    source: SourceLocation | None = None
    missing_fact: str | None = None


@dataclass(frozen=True)
class _EventHandlerCtx:
    """Immutable context passed to every event handler.

    Carries all inputs that are invariant across loop iterations, plus the
    current fringe accumulators which may change after each FringeEvent and
    the work-time regime cap account, which grows after each eligible
    night, holiday or shift supplement.  ``worker_facts`` carries the
    prior-year income, the waivers, the sector and the employer activity
    every regime and the PdR read.  ``overtime_bands`` are the CCNL bands an
    overtime event without a multiplier is paid with; ``sickness`` the rules
    and the episodes a sickness episode is paid with, updated after each.
    """

    evt_id: str
    cp: CompetencePeriod
    payment_date: date
    resolver: PolicyResolver
    context: PolicyContext
    fringe_threshold: FringeThreshold
    cumulative_fringe: Decimal
    cumulative_taxed: Decimal
    pdr_income_ceiling: Decimal | None = None
    rinnovo_regime: PreferentialTaxRegime | None = None
    work_time_regime: PreferentialTaxRegime | None = None
    work_time_cap: RegimeCapAccount = field(default_factory=RegimeCapAccount)
    worker_facts: RegimeFacts = field(default_factory=RegimeFacts)
    overtime_bands: CCNLOvertimeBands = field(default_factory=CCNLOvertimeBands)
    sickness: SicknessTerms = field(default_factory=SicknessTerms)

    @property
    def tax_year(self) -> int:
        """Tax year of the run: the fringe threshold is the one of that year."""
        return self.fringe_threshold.tax_year


@dataclass
class EventEffect:
    """Accounting outputs and contribution-base deltas from one event.

    Attributes:
        items: Pay items created by the handler.
        intents: Posting intents for ledger projection (converted to entries by
            :func:`~ccnl_engine.payroll.ledger.services_posting.post`).
        inps_delta: Increase in the INPS contribution base.
        tfr_delta: Increase in the TFR accrual base.
        irpef_delta: Increase in the IRPEF taxable base.
        separate_irpef_delta: Part of ``irpef_delta`` withheld apart from
            the pay of the period, as a premium (art. 23 c. 2 lett. b) DPR
            600/1973).
        substitute_delta: Increase in the PdR substitute-tax base.
        fringe_value: Total fringe benefit value (FringeEvent only).
        fringe_inps: Fringe INPS-taxable portion (FringeEvent only).
        fringe_irpef: Fringe IRPEF-taxable portion (FringeEvent only).
        new_cumulative_fringe: Updated cumulative fringe YTD (FringeEvent only).
        new_cumulative_taxed: Updated cumulative taxed fringe (FringeEvent only).
        regime_cap_used: Part of the annual cap of the work-time regime
            consumed by the event.
        decisions: Decisions taken on the event, e.g. a regime eligibility.
        issues: Conditions raised by the event; each blocks payability.
        sickness_episode: Sickness episode the event processed, cut at its
            last processed day, to record in the accrual state.
        sick_units: Units of the monthly pay the sickness episode deducted.
        sick_days: Sick days within the comporto the episode paid.
        limitations: Ids of the engine limitations whose path it took.
    """

    items: list[PayItem] = field(default_factory=list)
    intents: list[PostingIntent] = field(default_factory=list)
    inps_delta: Decimal = _ZERO
    tfr_delta: Decimal = _ZERO
    irpef_delta: Decimal = _ZERO
    separate_irpef_delta: Decimal = _ZERO
    substitute_delta: Decimal = _ZERO
    fringe_value: Decimal = _ZERO
    fringe_inps: Decimal = _ZERO
    fringe_irpef: Decimal = _ZERO
    new_cumulative_fringe: Decimal | None = None
    new_cumulative_taxed: Decimal | None = None
    regime_cap_used: Decimal = _ZERO
    decisions: list[CalculationDecision] = field(default_factory=list)
    issues: list[CalculationIssue] = field(default_factory=list)
    sickness_episode: SicknessEpisode | None = None
    sick_units: Decimal = _ZERO
    sick_days: frozenset[date] = frozenset()
    limitations: tuple[str, ...] = ()


def _treatment_deltas(
    treatment: EventTreatment, gross: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (inps_delta, tfr_delta, irpef_delta) for a standard event.

    Returns:
        A triple of gross or zero for each axis per the treatment policy.
    """
    return (
        gross if treatment.inps else _ZERO,
        gross if treatment.tfr else _ZERO,
        gross if treatment.irpef else _ZERO,
    )
