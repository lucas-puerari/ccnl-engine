"""Statutory variable-pay rule models (fringe benefits, PdR, rinnovo, notte)."""

from __future__ import annotations

from datetime import date  # noqa: TC003
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.metadata import RulesetIdentity  # noqa: TC001
from ccnl_engine.engine.tax.domain.preferential_regime import PreferentialTaxRegime


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


class RinnovoRules(PreferentialTaxRegime):
    """Contract-renewal substitute tax (L. 199/2025 art. 1 c. 7).

    Salary increments paid in 2026 under CCNL renewals signed from
    1 January 2024 to 31 December 2026 are taxed at ``flat_tax_rate`` (5%)
    instead of IRPEF and its surtaxes.  The regime applies only to
    private-sector employees whose 2025 employment income (reddito di
    lavoro dipendente) does not exceed ``income_ceiling`` (33,000 EUR),
    unless the worker renounces it in writing.  There is no annual cap.

    The signing window is recorded as data: the engine does not receive the
    signing date of a renewal, so the caller asserts it by declaring the
    increment as a contract renewal.

    Attributes:
        agreements_signed_from: First signing date of a qualifying renewal.
        agreements_signed_until: Last signing date of a qualifying renewal.
    """

    agreements_signed_from: date
    agreements_signed_until: date


class NotteTurnoRules(BaseModel):
    """Night and shift supplement substitute-tax rules (L.199/2025 art. 1 co. 10).

    Night/shift supplements are taxed at ``flat_tax_rate`` when the
    worker's prior-year income does not exceed ``income_ceiling``.

    Attributes:
        flat_tax_rate: Substitutive rate applied to eligible supplements.
        income_ceiling: Maximum prior-year income for eligibility.
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid")

    flat_tax_rate: Decimal = Field(gt=Decimal(0), lt=Decimal(1))
    income_ceiling: Decimal = Field(gt=Decimal(0))
    ruleset: RulesetIdentity | None = None


class VariablePayRules(BaseModel):
    """Container for all statutory variable-pay rules for a fiscal year.

    Attributes:
        year: Fiscal year these rules apply to.
        fringe_benefit: Fringe-benefit exemption thresholds.
        pdr: Premio di risultato flat-tax parameters.
        rinnovo: Contract-renewal substitute-tax regime.
        notte_turno: Night/shift supplement substitute-tax parameters.
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    description: str = ""
    fringe_benefit: FringeBenefitRules
    pdr: PdRRules
    rinnovo: RinnovoRules
    notte_turno: NotteTurnoRules
    ruleset: RulesetIdentity | None = None
