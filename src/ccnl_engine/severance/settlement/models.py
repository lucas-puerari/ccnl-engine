"""Rules of the separate taxation of the TFR paid at the termination."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.ruleset.models import RulesetIdentity
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = [
    "TfrReferenceIncome",
    "TfrSeparateTaxation",
    "TfrServicePeriod",
    "TfrSettlementRules",
]


class TfrSeparateTaxation(BaseModel):
    """The TFR is taxed apart from the ordinary IRPEF (art. 17 c. 1 lett. a TUIR)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provenance: RuleProvenance | None = None


class TfrReferenceIncome(BaseModel):
    """Reference income and average rate of the TFR (art. 19 c. 1 TUIR).

    Attributes:
        multiplier: The TFR net of the revaluations already taxed, over the
            years of service, times ``multiplier`` (12) is the income whose
            average IRPEF rate taxes the TFR.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    multiplier: Decimal = Field(gt=Decimal(0))
    provenance: RuleProvenance | None = None


class TfrServicePeriod(BaseModel):
    """How the years of service are counted (art. 2120 c. 1 c.c.).

    Attributes:
        month_minimum_days: A fraction of month of at least this many days
            counts as a whole month of service.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month_minimum_days: int = Field(ge=1, le=31)
    provenance: RuleProvenance | None = None


class TfrFixedTermDeduction(BaseModel):
    """The tax deduction of a short fixed term (art. 19 c. 1-ter TUIR).

    Attributes:
        per_year: Deduction from the tax for each year of a fixed term of
            at most ``max_months``, by the month for a shorter period and
            in proportion to the hours of a part time.
        max_months: Longest effective fixed term that takes it (two years).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    per_year: Decimal = Field(gt=Decimal(0))
    max_months: int = Field(ge=1)
    provenance: RuleProvenance | None = None


class TfrSettlementRules(BaseModel):
    """Separate taxation of the TFR of the employments ending in one year.

    Attributes:
        year: Year of the termination: art. 19 c. 1 takes the brackets of
            the year the right to the TFR matured.
        separate_taxation: The TFR is taxed apart from the ordinary IRPEF.
        reference_income: Multiplier of the reference income.
        service_period: Counting of the months of service.
        fixed_term_deduction: Deduction of a fixed term of up to two years.
        ruleset: Identity of the data file.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    separate_taxation: TfrSeparateTaxation
    reference_income: TfrReferenceIncome
    service_period: TfrServicePeriod
    fixed_term_deduction: TfrFixedTermDeduction
    ruleset: RulesetIdentity | None = None
