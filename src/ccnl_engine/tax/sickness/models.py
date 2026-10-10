"""INPS statutory sick-pay indemnity rate models."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.ruleset.models import (
    RulesetIdentity,  # noqa: TC001
)
from ccnl_engine.provenance.source.models_chain import RuleProvenance  # noqa: TC001


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


class SickPayCoverage(BaseModel):
    """Whether INPS pays the sickness indemnity to a group of workers.

    A restriction left ``None`` matches every worker.  The first rule of
    :attr:`InpsSickPayRates.coverage` that matches a worker decides.

    Attributes:
        sectors: INPS tax sectors of the CCNL (``industria``...).
        categories: Worker categories (``operaio``, ``impiegato``...).
        contract_types: Contract types (``apprentice``...).
        covered: Whether INPS pays the indemnity to the matching workers.
        source: Normative source of the rule.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    sectors: frozenset[str] | None = Field(default=None, min_length=1)
    categories: frozenset[str] | None = Field(default=None, min_length=1)
    contract_types: frozenset[str] | None = Field(default=None, min_length=1)
    covered: bool
    source: str = Field(min_length=1)

    def matches(self, sector: str, category: str | None, contract_type: str) -> bool:
        """Return whether the rule concerns the worker.

        An unknown category matches only a rule that does not restrict it.

        Returns:
            ``True`` when every restriction set matches.
        """
        return (
            (self.sectors is None or sector in self.sectors)
            and (
                self.categories is None
                or (category is not None and category in self.categories)
            )
            and (self.contract_types is None or contract_type in self.contract_types)
        )


class InpsSickPayRates(BaseModel):
    """Statutory INPS sick-pay indemnity rates (malattia ordinaria).

    The carenza period (first *carenza_days* days) is not covered by INPS;
    coverage is CCNL-specific.  From day ``carenza_days + 1`` onwards the
    ``bands`` list defines the INPS rate for successive day ranges.

    Bands must be ordered by ``day_from`` and must not overlap.  The first
    band must start at ``carenza_days + 1``.  Every statutory field is
    required: the carenza, the bands, the annual maximum and the coverage
    rules have no default, so an incomplete table is rejected instead of
    taking a legal value it does not state.

    Attributes:
        carenza_days: Number of waiting days before INPS indemnity starts.
        bands: Rate bands ordered by ``day_from`` (non-overlapping).
        annual_max_days: Days INPS indemnifies at most in a calendar year.
        coverage: Which workers INPS pays the indemnity to, first match
            wins; a worker no rule matches is not known to be covered.
        ruleset: Provenance of the statutory source.
        bands_provenance: Provenance record of the indemnity rates.
    """

    model_config = ConfigDict(extra="forbid")

    description: str = ""
    carenza_days: int = Field(ge=0)
    bands: list[SickPayBand] = Field(min_length=1)
    annual_max_days: int = Field(ge=1)
    coverage: tuple[SickPayCoverage, ...] = Field(min_length=1)
    ruleset: RulesetIdentity | None = None
    bands_provenance: RuleProvenance | None = None

    def covers(
        self, sector: str, category: str | None, contract_type: str
    ) -> bool | None:
        """Return whether INPS pays the sickness indemnity to the worker.

        Returns:
            The ``covered`` flag of the first matching rule, ``None`` when
            no rule matches.
        """
        rule = next(
            (r for r in self.coverage if r.matches(sector, category, contract_type)),
            None,
        )
        return None if rule is None else rule.covered

    def band_rate(self, day: int) -> Decimal:
        """Return the INPS rate of episode day ``day``.

        Returns:
            The rate of the band holding ``day``, zero outside every band.
        """
        return next(
            (b.rate for b in self.bands if b.day_from <= day <= b.day_to),
            Decimal(0),
        )

    @model_validator(mode="after")
    def _check_bands(self) -> Self:
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
