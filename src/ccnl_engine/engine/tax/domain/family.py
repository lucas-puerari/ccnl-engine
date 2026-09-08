"""Domain models for Art. 12 TUIR family deduction rules."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.tax.domain.rules import DeductionBreakpoint


class SpouseDeductionRules(BaseModel):
    """Art. 12 c. 1 lett. a TUIR: deduction for a fiscally dependent spouse.

    The piecewise-linear schedule is encoded as :class:`DeductionBreakpoint`
    entries, reusing the same interpolation machinery as the Art. 13 work-income
    deduction.

    ``dependent_income_threshold`` is the spouse's own-income limit (EUR 2840.51)
    above which they are no longer considered fiscally dependent.

    Note: the sub-band supplements of EUR 10-30 in the EUR 29001-35200 income
    range are not modelled; EUR 690 flat is assumed for that segment.
    """

    model_config = ConfigDict(extra="forbid")

    dependent_income_threshold: Decimal = Field(gt=Decimal(0))
    breakpoints: list[DeductionBreakpoint]
    notes: str = ""


class ChildrenDeductionRules(BaseModel):
    """Art. 12 c. 1 lett. c TUIR: deduction for eligible dependent children.

    Post D.Lgs. 230/2021 (Assegno Unico), children under ``auu_age_cutoff``
    (21) are covered by AUU and are no longer eligible for Art. 12 deductions.
    Eligible children are those aged 21 or older (up to 29) and those aged
    30+ with certified disability.

    Tapering formula per child::

        deduction = base_amount
            * max(0, (income_ceiling - gross_annual) / income_ceiling)

    When there are N children, ``income_ceiling`` increases by
    ``income_ceiling_increment_per_child`` for each child beyond the first.
    """

    model_config = ConfigDict(extra="forbid")

    auu_age_cutoff: int = Field(ge=0)
    base_amount: Decimal = Field(gt=Decimal(0))
    disabled_amount: Decimal = Field(gt=Decimal(0))
    income_ceiling: Decimal = Field(gt=Decimal(0))
    income_ceiling_increment_per_child: Decimal = Field(ge=Decimal(0))
    notes: str = ""


class OtherDependentRules(BaseModel):
    """Art. 12 c. 1 lett. d TUIR: deduction for other qualifying ascendants.

    Post L. 207/2024, only ``ascendenti conviventi`` (parents/grandparents
    living with the taxpayer) qualify.  Other categories (siblings, in-laws)
    were removed.

    Tapering formula per ascendant::

        deduction = amount * max(0, (income_ceiling - gross_annual) / income_ceiling)
    """

    model_config = ConfigDict(extra="forbid")

    dependent_income_threshold: Decimal = Field(gt=Decimal(0))
    amount: Decimal = Field(gt=Decimal(0))
    income_ceiling: Decimal = Field(gt=Decimal(0))
    notes: str = ""


class FamilyDeductionRules(BaseModel):
    """Art. 12 TUIR family deduction parameters for one fiscal year.

    The engine uses ``gross_annual`` (RAL) as a proxy for *reddito complessivo*
    when applying the tapering formulas.  This is a simplification: other
    income sources (rental income, financial income, etc.) are not modelled.
    Annual deductions are computed; monthly withholding conguaglio is out of
    scope.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    description: str = ""
    spouse: SpouseDeductionRules
    children: ChildrenDeductionRules
    other_dependents: OtherDependentRules
