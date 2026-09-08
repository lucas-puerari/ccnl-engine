"""Domain models for Art. 15 TUIR oneri detraibili rules."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MortgageInterestRules(BaseModel):
    """Art. 15 c. 1 lett. b TUIR: interessi passivi mutuo prima casa.

    A 19 % credit is applied to interest paid on a mortgage for the
    acquisition of the worker's main dwelling (*abitazione principale*),
    up to ``ceiling`` per household per year.

    Note: the ceiling is a household ceiling — when two spouses share a
    mortgage, each may deduct up to ``ceiling / 2``.  This split is not
    modelled; the engine applies the full ceiling to the declared amount.
    """

    model_config = ConfigDict(extra="forbid")

    ceiling: Decimal = Field(gt=Decimal(0))
    rate: Decimal = Field(gt=Decimal(0), lt=Decimal(1))
    notes: str = ""


class Art15DeductionRules(BaseModel):
    """Art. 15 TUIR oneri detraibili parameters for one fiscal year.

    The engine applies a flat ``rate`` credit on eligible expenditure up to
    the statutory ``ceiling`` for each modelled category.

    Only interessi passivi mutuo prima casa (lett. b) is modelled.  Other
    Art. 15 categories (medical expenses, educational expenses, funeral
    expenses, etc.) are out of scope and reported as
    ``FiscalSimplification.NO_DETRAZIONI_ART15`` when not provided.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    description: str = ""
    mortgage_interest: MortgageInterestRules
