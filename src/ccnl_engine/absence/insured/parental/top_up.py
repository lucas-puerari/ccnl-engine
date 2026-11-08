"""CCNL supplement to the statutory parental leave indemnity."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["ParentalTopUp"]


class ParentalTopUp(BaseModel):
    """Employer supplement capped by days previously supplemented.

    ``only_standard_rate`` excludes enhanced statutory months. Three months
    are represented as 90 days under the INPS thirty-day convention.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: Annotated[Decimal, Field(gt=Decimal(0), le=Decimal(1))]
    max_days: int = Field(ge=1)
    valid_from: date | None = None
    only_standard_rate: bool = False
    provenance: RuleProvenance
