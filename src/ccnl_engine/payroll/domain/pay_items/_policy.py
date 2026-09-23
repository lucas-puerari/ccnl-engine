"""CompetencePeriod, PolicyDecision, and PayItemPolicy — treatment selection types."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.payroll.domain.treatments import (
    ContributionTreatment,
    CostTreatment,
    TaxTreatment,
    TfrTreatment,
)

__all__ = [
    "CompetencePeriod",
    "ContributionTreatment",
    "CostTreatment",
    "PayItemPolicy",
    "PolicyDecision",
    "TaxTreatment",
    "TfrTreatment",
]


class CompetencePeriod(BaseModel):
    """The calendar month and year to which a pay item belongs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    month: int = Field(ge=1, le=12)


class PolicyDecision(BaseModel):
    """The outcome of applying a PayItemPolicy to one pay item.

    Captures which rules were selected, the legal basis, and the effective
    period so the result is auditable after the fact.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    policy_version: str
    effective_from: date
    effective_until: date | None
    tax_treatment: TaxTreatment
    contribution_treatment: ContributionTreatment
    tfr_treatment: TfrTreatment
    cost_treatment: CostTreatment
    legal_basis: str
    input_facts: tuple[str, ...] = ()
    eligibility: Literal["eligible", "not_eligible", "unknown"] = "eligible"


class PayItemPolicy(BaseModel):
    """Binding from pay-item kind and context to a PolicyDecision.

    A policy is a static rule: given item kind, reference date, worker
    attributes and CCNL slug it returns the applicable PolicyDecision.
    The policy itself is immutable; different scenarios may resolve the
    same policy_id to different decisions (e.g. when thresholds change).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    policy_version: str
    applies_to_kinds: tuple[str, ...]
    effective_from: date
    effective_until: date | None
    default_decision: PolicyDecision

    def resolve(self, kind: str, as_of: date) -> PolicyDecision | None:
        """Return the PolicyDecision when *kind* and *as_of* are in scope.

        Returns:
            The :attr:`default_decision` when *kind* is in
            :attr:`applies_to_kinds` and *as_of* falls within the effective
            period; ``None`` otherwise.
        """
        if kind not in self.applies_to_kinds:
            return None
        if as_of < self.effective_from:
            return None
        if self.effective_until is not None and as_of > self.effective_until:
            return None
        return self.default_decision
