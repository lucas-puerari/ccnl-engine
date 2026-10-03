"""Domain models for Art. 12 TUIR family deduction rules.

Every amount and limit is a statutory parameter of the bundle; the formulas
of art. 12 are applied by :mod:`ccnl_engine.payroll.service.family`.
"""

from __future__ import annotations

import itertools
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.provenance.domain.ruleset_identity import RulesetIdentity

_ZERO = Decimal(0)


class SpouseDeductionRules(BaseModel):
    """Art. 12 c. 1 lett. a TUIR: deduction for a fiscally dependent spouse.

    With ``R`` the reddito complessivo:

    1. up to ``low_income_limit``: ``full_amount - low_income_reduction *
       R / low_income_limit``;
    2. above it, up to ``flat_income_limit``: ``flat_amount``;
    3. above that, up to ``phase_out_limit``: ``flat_amount * (phase_out_limit
       - R) / (phase_out_limit - flat_income_limit)``.

    ``dependent_income_threshold`` is the spouse's own-income limit (c. 2).
    """

    model_config = ConfigDict(extra="forbid")

    dependent_income_threshold: Decimal = Field(gt=_ZERO)
    full_amount: Decimal = Field(gt=_ZERO)
    low_income_reduction: Decimal = Field(gt=_ZERO)
    low_income_limit: Decimal = Field(gt=_ZERO)
    flat_amount: Decimal = Field(gt=_ZERO)
    flat_income_limit: Decimal = Field(gt=_ZERO)
    phase_out_limit: Decimal = Field(gt=_ZERO)
    notes: str = ""
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _ordered_limits(self) -> SpouseDeductionRules:
        if not self.low_income_limit < self.flat_income_limit < self.phase_out_limit:
            msg = "spouse income limits must increase: low < flat < phase-out"
            raise ValueError(msg)
        return self


class IncomeIncrease(BaseModel):
    """One band of art. 12 c. 1 lett. b: above ``above``, not above ``up_to``."""

    model_config = ConfigDict(extra="forbid")

    above: Decimal = Field(ge=_ZERO)
    up_to: Decimal
    amount: Decimal = Field(gt=_ZERO)

    @model_validator(mode="after")
    def _non_empty(self) -> IncomeIncrease:
        if self.up_to <= self.above:
            msg = f"increase band {self.above}-{self.up_to} is empty"
            raise ValueError(msg)
        return self

    def contains(self, income: Decimal) -> bool:
        """Return whether ``income`` is above :attr:`above`, not above :attr:`up_to`.

        Returns:
            ``above < income <= up_to``, the "superiore a ... ma non a" form.
        """
        return self.above < income <= self.up_to


class SpouseIncreaseRules(BaseModel):
    """Art. 12 c. 1 lett. b TUIR: increases of the lett. a spouse deduction.

    The bands do not overlap; an income outside every band has no increase.
    """

    model_config = ConfigDict(extra="forbid")

    bands: tuple[IncomeIncrease, ...]
    notes: str = ""
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _disjoint(self) -> SpouseIncreaseRules:
        ordered = sorted(self.bands, key=lambda band: band.above)
        for low, high in itertools.pairwise(ordered):
            if high.above < low.up_to:
                msg = f"increase bands overlap at {high.above}"
                raise ValueError(msg)
        return self

    def increase(self, income: Decimal) -> Decimal:
        """Return the increase of the band ``income`` falls in.

        Returns:
            Zero when ``income`` is in no band.
        """
        return next((b.amount for b in self.bands if b.contains(income)), _ZERO)


class ChildrenDeductionRules(BaseModel):
    """Art. 12 c. 1 lett. c TUIR: deduction for eligible dependent children.

    A child gives right to the deduction from the age of ``auu_age_cutoff``
    (21; younger children are covered by the assegno unico, D.Lgs.
    230/2021) and below ``age_limit`` (30), or at any age from 21 with a
    disability under art. 3 L. 104/1992.

    Per child, with ``R`` the reddito complessivo::

        base_amount * (ceiling - R) / ceiling

    where ``ceiling`` is ``income_ceiling`` raised by
    ``income_ceiling_increment_per_child`` for each child beyond the first.

    Own-income limit (c. 2): ``dependent_income_threshold``, raised to
    ``young_child_income_threshold`` for a child who turns at most
    ``young_child_max_age`` in the year.
    """

    model_config = ConfigDict(extra="forbid")

    auu_age_cutoff: int = Field(ge=0)
    age_limit: int = Field(gt=0)
    base_amount: Decimal = Field(gt=_ZERO)
    income_ceiling: Decimal = Field(gt=_ZERO)
    income_ceiling_increment_per_child: Decimal = Field(ge=_ZERO)
    dependent_income_threshold: Decimal = Field(gt=_ZERO)
    young_child_income_threshold: Decimal = Field(gt=_ZERO)
    young_child_max_age: int = Field(ge=0)
    notes: str = ""
    provenance: RuleProvenance | None = None


class OtherDependentRules(BaseModel):
    """Art. 12 c. 1 lett. d TUIR: deduction for cohabiting ascendants.

    Post L. 207/2024, only ascendants living with the taxpayer qualify.
    Per ascendant::

        amount * (income_ceiling - R) / income_ceiling
    """

    model_config = ConfigDict(extra="forbid")

    dependent_income_threshold: Decimal = Field(gt=_ZERO)
    amount: Decimal = Field(gt=_ZERO)
    income_ceiling: Decimal = Field(gt=_ZERO)
    notes: str = ""
    provenance: RuleProvenance | None = None


class FamilyDeductionRules(BaseModel):
    """Art. 12 TUIR family deduction parameters for one tax year.

    ``ratio_decimals`` is the number of decimals every ratio of the
    formulas is taken to, discarding the rest (art. 12 c. 4).
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    description: str = ""
    ratio_decimals: int = Field(ge=0)
    spouse: SpouseDeductionRules
    spouse_increases: SpouseIncreaseRules
    children: ChildrenDeductionRules
    other_dependents: OtherDependentRules
    ruleset: RulesetIdentity | None = None
