"""Band of a CCNL injury integration, beginning on a counted day."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InjuryIntegrationBand(BaseModel):
    """Share of the pay the CCNL tops the INAIL indemnity up to, from a day.

    ``day_from`` counts from the injury day (day 0); ``rate`` holds until the
    next band, ``0`` ending the top-up.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    day_from: int = Field(ge=1)
    rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
