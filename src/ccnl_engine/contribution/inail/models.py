"""The INAIL rate a sector sets for a category of workers."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["SectorInail"]


class SectorInail(BaseModel):
    """The INAIL premium rate of a sector, set by law, not by the position.

    Agricoltura: the operai pay the "Assicurazione INAIL in agricoltura"
    with the INPS contributions, at one rate for every employer (INPS circ.
    43/2026, allegati 1 and 2, col. A: 8,5000).

    Attributes:
        rate_by_category: Share of the contribution base by category.
        provenance: The source of the rates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate_by_category: dict[WorkerCategory, Decimal] = Field(min_length=1)
    provenance: RuleProvenance
