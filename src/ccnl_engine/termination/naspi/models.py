"""The contribution an employer owes on ending an open-ended employment."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.ruleset.models import RulesetIdentity
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["NaspiDismissalRules", "SourcedValue"]


class SourcedValue(BaseModel):
    """A value of the contribution and its source.

    Attributes:
        value: The value.
        provenance: Source of the value.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    value: Decimal = Field(gt=Decimal(0))
    provenance: RuleProvenance


class NaspiDismissalRules(BaseModel):
    """The contribution of L. 92/2012 art. 2 c. 31 in a year.

    Attributes:
        year: The year of the end of the employment.
        rate: Share of the monthly NASpI maximum for each twelve months of
            service in the last three years, 41%.
        monthly_maximum: Monthly NASpI maximum of the year.
        ruleset: Identity of the data file.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    year: int
    rate: SourcedValue
    monthly_maximum: SourcedValue
    ruleset: RulesetIdentity | None = None
