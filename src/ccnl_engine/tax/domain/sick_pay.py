"""INPS statutory sick-pay indemnity rate models."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.domain.ruleset_identity import (
    RulesetIdentity,  # noqa: TC001
)


class SickPayBand(BaseModel):
    """One INPS indemnity rate band for sick leave (malattia ordinaria).

    Attributes:
        day_from: First day of the band (inclusive, 1-indexed).
        day_to: Last day of the band (inclusive, must be >= day_from).
        rate: Fraction of the daily reference base INPS pays.
        description: Human-readable label (optional).
    """

    model_config = ConfigDict(extra="forbid")

    day_from: int = Field(ge=1)
    day_to: int = Field(ge=1)
    rate: Decimal = Field(gt=Decimal(0), le=Decimal(1))
    description: str = ""

    @model_validator(mode="after")
    def _check_day_range(self) -> Self:
        if self.day_to < self.day_from:
            msg = (
                f"SickPayBand: day_to ({self.day_to}) must be "
                f">= day_from ({self.day_from})"
            )
            raise ValueError(msg)
        return self


class InpsSickPayRates(BaseModel):
    """Statutory INPS sick-pay indemnity rates (malattia ordinaria).

    The carenza period (first *carenza_days* days) is not covered by INPS;
    coverage is CCNL-specific.  From day ``carenza_days + 1`` onwards the
    ``bands`` list defines the INPS rate for successive day ranges.

    Bands must be ordered by ``day_from`` and must not overlap.  The first
    band must start at ``carenza_days + 1``.

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

    @model_validator(mode="after")
    def _check_bands(self) -> Self:
        if not self.bands:
            return self
        expected_start = self.carenza_days + 1
        first = self.bands[0]
        if first.day_from != expected_start:
            msg = (
                f"InpsSickPayRates: first band day_from must be "
                f"carenza_days + 1 = {expected_start}, "
                f"got {first.day_from}"
            )
            raise ValueError(msg)
        for i in range(len(self.bands) - 1):
            curr = self.bands[i]
            nxt = self.bands[i + 1]
            if nxt.day_from <= curr.day_to:
                msg = (
                    f"InpsSickPayRates: bands[{i}] (days {curr.day_from}-"
                    f"{curr.day_to}) overlaps bands[{i + 1}] "
                    f"(day_from={nxt.day_from})"
                )
                raise ValueError(msg)
            if nxt.day_from != curr.day_to + 1:
                msg = (
                    f"InpsSickPayRates: gap between bands[{i}] "
                    f"(day_to={curr.day_to}) and bands[{i + 1}] "
                    f"(day_from={nxt.day_from})"
                )
                raise ValueError(msg)
        return self
