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

    model_config = ConfigDict(extra="forbid")

    provenance: RuleProvenance | None = None


class TfrReferenceIncome(BaseModel):
    """Reference income and average rate of the TFR (art. 19 c. 1 TUIR).

    Attributes:
        multiplier: The TFR net of the revaluations already taxed, over the
            years of service, times ``multiplier`` (12) is the income whose
            average IRPEF rate taxes the TFR.
    """

    model_config = ConfigDict(extra="forbid")

    multiplier: Decimal = Field(gt=Decimal(0))
    provenance: RuleProvenance | None = None


class TfrServicePeriod(BaseModel):
    """How the years of service are counted (art. 2120 c. 1 c.c.).

    Attributes:
        month_minimum_days: A fraction of month of at least this many days
            counts as a whole month of service.
    """

    model_config = ConfigDict(extra="forbid")

    month_minimum_days: int = Field(ge=1, le=31)
    provenance: RuleProvenance | None = None


class TfrSettlementRules(BaseModel):
    """Separate taxation of the TFR of the employments ending in one year.

    Attributes:
        year: Year of the termination: art. 19 c. 1 takes the brackets of
            the year the right to the TFR matured.
        separate_taxation: The TFR is taxed apart from the ordinary IRPEF.
        reference_income: Multiplier of the reference income.
        service_period: Counting of the months of service.
        ruleset: Identity of the data file.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    separate_taxation: TfrSeparateTaxation
    reference_income: TfrReferenceIncome
    service_period: TfrServicePeriod
    ruleset: RulesetIdentity | None = None
