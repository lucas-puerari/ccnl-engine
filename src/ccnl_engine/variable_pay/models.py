"""Statutory variable-pay rules: fringe benefits, PdR and L. 199/2025 regimes."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.ruleset.models import (
    RulesetIdentity,
)
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.regime.models import (
    PreferentialTaxRegime,
)


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
        provenance: Source and status of the thresholds.
    """

    model_config = ConfigDict(extra="forbid")

    threshold_standard: Decimal = Field(gt=Decimal(0))
    threshold_with_children: Decimal = Field(gt=Decimal(0))
    ruleset: RulesetIdentity | None = None
    provenance: RuleProvenance | None = None


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
        provenance: Source and status of the PdR parameters.
    """

    model_config = ConfigDict(extra="forbid")

    max_amount: Decimal = Field(gt=Decimal(0))
    flat_tax_rate: Decimal = Field(gt=Decimal(0), lt=Decimal(1))
    income_ceiling: Decimal = Field(gt=Decimal(0))
    ruleset: RulesetIdentity | None = None
    provenance: RuleProvenance | None = None


class TravelAllowanceCaps(BaseModel):
    """Daily amounts of a travel allowance left out of the income.

    Attributes:
        none: Cap when neither meals nor lodging are reimbursed or provided.
        one: Cap reduced by one third, when meals or lodging are.
        both: Cap reduced by two thirds, when both are.
    """

    model_config = ConfigDict(extra="forbid")

    none: Decimal = Field(gt=Decimal(0))
    one: Decimal = Field(gt=Decimal(0))
    both: Decimal = Field(gt=Decimal(0))


class TravelAllowanceRules(BaseModel):
    """Exempt part of the travel allowance (indennità di trasferta).

    Art. 51 c. 5 TUIR: the allowance of a trasferta outside the comune is
    income for the part above a daily cap, reduced by one third when meals
    or lodging are reimbursed or provided and by two thirds when both are;
    within the comune it is income in full.  The contribution base follows
    (art. 12 c. 2 L. 153/1969).

    Attributes:
        italy: Daily caps of a trasferta in Italy.
        abroad: Daily caps of a trasferta abroad.
        ruleset: Ruleset the caps belong to.
        provenance: Source and status of the caps.
    """

    model_config = ConfigDict(extra="forbid")

    italy: TravelAllowanceCaps
    abroad: TravelAllowanceCaps
    ruleset: RulesetIdentity | None = None
    provenance: RuleProvenance | None = None

    def cap(self, *, abroad: bool, meals_lodging: str) -> Decimal:
        """Return the exempt daily cap of a trasferta outside the comune.

        Returns:
            The cap of the place, reduced as ``meals_lodging`` says.
        """
        caps = self.abroad if abroad else self.italy
        return {"none": caps.none, "one": caps.one, "both": caps.both}[meals_lodging]


class VariablePayRules(BaseModel):
    """Container for all statutory variable-pay rules for a fiscal year.

    Attributes:
        year: Fiscal year these rules apply to.
        fringe_benefit: Fringe-benefit exemption thresholds.
        pdr: Premio di risultato flat-tax parameters.
        rinnovo: Contract-renewal substitute-tax regime (L. 199/2025 art. 1
            c. 7): increments paid in 2026 under renewals signed within its
            signing window.
        notte_festivi_turni: Substitute-tax regime for night, holiday and
            rest-day, and shift supplements (L. 199/2025 art. 1 cc. 10-11).
        travel_allowance: Exempt daily caps of the travel allowance (art.
            51 c. 5 TUIR).
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    description: str = ""
    fringe_benefit: FringeBenefitRules
    pdr: PdRRules
    rinnovo: PreferentialTaxRegime
    notte_festivi_turni: PreferentialTaxRegime
    travel_allowance: TravelAllowanceRules
    ruleset: RulesetIdentity | None = None
