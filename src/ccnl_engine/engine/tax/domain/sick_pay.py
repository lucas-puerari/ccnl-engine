"""INPS statutory sick-pay indemnity rate models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.engine.metadata import RulesetIdentity  # noqa: TC001


class SickPayBand(BaseModel):
    """One INPS indemnity rate band for sick leave (malattia ordinaria).

    Attributes:
        day_from: First day of the band (inclusive, 1-indexed).
        day_to: Last day of the band (inclusive).
        rate: Fraction of the daily reference base INPS pays.
        description: Human-readable label (optional).
    """

    model_config = ConfigDict(extra="forbid")

    day_from: int = Field(ge=1)
    day_to: int = Field(ge=1)
    rate: Decimal = Field(gt=Decimal(0), le=Decimal(1))
    description: str = ""


class InpsSickPayRates(BaseModel):
    """Statutory INPS sick-pay indemnity rates (malattia ordinaria).

    The carenza period (first *carenza_days* days) is not covered by INPS;
    coverage is CCNL-specific.  From day ``carenza_days + 1`` onwards the
    ``bands`` list defines the INPS rate for successive day ranges.

    Attributes:
        carenza_days: Number of waiting days before INPS indemnity starts.
        bands: Rate bands ordered by ``day_from`` (non-overlapping).
        ruleset: Provenance of the statutory source.
    """

    model_config = ConfigDict(extra="forbid")

    description: str = ""
    carenza_days: int = Field(default=3, ge=0)
    bands: list[SickPayBand] = Field(default_factory=list)
    ruleset: RulesetIdentity | None = None
