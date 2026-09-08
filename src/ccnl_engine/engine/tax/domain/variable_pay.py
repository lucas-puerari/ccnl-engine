"""Statutory variable-pay rule models (fringe benefits and PdR)."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.metadata import RulesetIdentity  # noqa: TC001


class FringeBenefitRules(BaseModel):
    """Statutory fringe-benefit exemption thresholds (Art. 51 c. 3 TUIR).

    Amounts above the applicable threshold become taxable income.
    The threshold depends on whether the worker has at least one
    dependent child (figlio fiscalmente a carico).

    Attributes:
        threshold_standard: Annual exemption for workers without
            dependent children.
        threshold_with_children: Annual exemption for workers with at
            least one dependent child.
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_standard: Decimal = Field(gt=Decimal(0))
    threshold_with_children: Decimal = Field(gt=Decimal(0))
    ruleset: RulesetIdentity | None = None


class PdRRules(BaseModel):
    """Statutory premio di risultato (PdR) tax rules.

    Eligible bonuses are taxed at ``flat_tax_rate`` up to ``max_amount``
    per year.  The preferential rate applies only when the worker's
    gross income from employment does not exceed ``income_ceiling``.

    Attributes:
        max_amount: Maximum bonus amount eligible for the flat tax.
        flat_tax_rate: Substitutive income-tax rate (imposta sostitutiva).
        income_ceiling: Maximum gross employment income for eligibility.
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid")

    max_amount: Decimal = Field(gt=Decimal(0))
    flat_tax_rate: Decimal = Field(gt=Decimal(0), lt=Decimal(1))
    income_ceiling: Decimal = Field(gt=Decimal(0))
    ruleset: RulesetIdentity | None = None


class VariablePayRules(BaseModel):
    """Container for all statutory variable-pay rules for a fiscal year.

    Attributes:
        year: Fiscal year these rules apply to.
        fringe_benefit: Fringe-benefit exemption thresholds.
        pdr: Premio di risultato flat-tax parameters.
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    description: str = ""
    fringe_benefit: FringeBenefitRules
    pdr: PdRRules
    ruleset: RulesetIdentity | None = None
