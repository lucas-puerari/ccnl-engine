"""Annual construction loyalty premium parameters."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance


class LoyaltyPremium(BaseModel):
    """Annual anniversary award for clerical employees and middle managers.

    The monthly run-chain pay approximates the CCNL's enumerated elements;
    interruptions of actual service and group-company continuity are not
    represented by the employment start date alone.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    service_years: int = Field(gt=0)
    months: Decimal = Field(default=Decimal(1), gt=0)
    provenance: RuleProvenance
