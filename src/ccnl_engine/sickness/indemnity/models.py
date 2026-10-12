"""INPS statutory sick-pay indemnity rate models."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.ruleset.models import (
    RulesetIdentity,
)
from ccnl_engine.provenance.source.rule.models import RuleProvenance


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
        ccnls: CCNL ids, for a group INPS names by its contract (the
            portieri of the CCNL Confedilizia are outside the cover whatever
            their sector).
        covered: Whether INPS pays the indemnity to the matching workers.
        source: Normative source of the rule.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    sectors: frozenset[str] | None = Field(default=None, min_length=1)
    categories: frozenset[str] | None = Field(default=None, min_length=1)
    contract_types: frozenset[str] | None = Field(default=None, min_length=1)
    ccnls: frozenset[str] | None = Field(default=None, min_length=1)
    covered: bool
    source: str = Field(min_length=1)

    def matches(
        self,
        sector: str,
        category: str | None,
        contract_type: str,
        ccnl: str | None = None,
    ) -> bool:
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
            and (self.ccnls is None or ccnl in self.ccnls)
        )


def _check_band_chain(bands: list[SickPayBand], carenza_days: int, owner: str) -> None:
    """Check that ``bands`` start after the carenza and leave no gap or overlap.

    Raises:
        ValueError: When a band starts elsewhere, overlaps the next or leaves
            a gap before it.
    """
    expected_start = carenza_days + 1
    first = bands[0]
    if first.day_from != expected_start:
        msg = (
            f"{owner}: first band day_from must be "
            f"carenza_days + 1 = {expected_start}, "
            f"got {first.day_from}"
        )
        raise ValueError(msg)
    for i in range(len(bands) - 1):
        curr = bands[i]
        nxt = bands[i + 1]
        if nxt.day_from <= curr.day_to:
            msg = (
                f"{owner}: bands[{i}] (days {curr.day_from}-"
                f"{curr.day_to}) overlaps bands[{i + 1}] "
                f"(day_from={nxt.day_from})"
            )
            raise ValueError(msg)
        if nxt.day_from != curr.day_to + 1:
            msg = (
                f"{owner}: gap between bands[{i}] "
                f"(day_to={curr.day_to}) and bands[{i + 1}] "
                f"(day_from={nxt.day_from})"
            )
            raise ValueError(msg)


class SickPayRegime(BaseModel):
    """INPS indemnity bands of a group of workers that differs from the rule.

    A CCNL names the regime of its workers in
    :attr:`~ccnl_engine.sickness.integration.models.SicknessRules.inps_regime`;
    the regime replaces the general bands, while the carenza, the annual
    maximum and the coverage stay those of :class:`InpsSickPayRates`.

    Attributes:
        id: Name the CCNL refers to (``pubblici_esercizi``...).
        description: Who the regime covers.
        bands: Rate bands ordered by ``day_from`` (non-overlapping).
        additional_contribution: Whether the employers of the regime pay an
            additional sickness contribution, listed in the INPS table of
            the year (``inps.sick_pay_supplements``); ``False`` for a regime
            funded by the ordinary rates (the lavoratori dello spettacolo).
        min_daily_contributions: Daily contributions from 1 January of the
            year before the episode the worker needs for the indemnity
            (spettacolo: 40, art. 66 D.L. 73/2021); ``None`` without such a
            requirement.
        provenance: Provenance record of the regime rates.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    description: str = ""
    bands: list[SickPayBand] = Field(min_length=1)
    additional_contribution: bool = True
    min_daily_contributions: int | None = Field(default=None, ge=1)
    provenance: RuleProvenance | None = None


class FixedTermSickLimit(BaseModel):
    """Sickness of a fixed-term contract (D.L. 463/1983 art. 5).

    Sickness is paid for no more days than those of work in the 12 months
    before the episode (c. 1); with :attr:`short_work_days` days of work or
    fewer, for at most that many days in the calendar year, the INPS share
    paid by INPS directly (c. 3); beyond the days of work with the employer
    INPS pays its share directly (c. 5).

    Attributes:
        short_work_days: The 30 days of c. 3.
        provenance: Source and status of the rule.
    """

    model_config = ConfigDict(extra="forbid")

    short_work_days: int = Field(ge=1)
    provenance: RuleProvenance | None = None


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
        regimes: Bands of the groups of workers whose rates differ from
            ``bands``, each named by an id unique in the table.
        fixed_term: Limit of a fixed-term contract; ``None`` when the
            table does not state it, and then not applied.
        min_daily_contributions: Requirement of the regime the table was
            resolved for (:meth:`for_regime`), ``None`` without one.
    """

    model_config = ConfigDict(extra="forbid")

    description: str = ""
    carenza_days: int = Field(ge=0)
    bands: list[SickPayBand] = Field(min_length=1)
    annual_max_days: int = Field(ge=1)
    coverage: tuple[SickPayCoverage, ...] = Field(min_length=1)
    ruleset: RulesetIdentity | None = None
    bands_provenance: RuleProvenance | None = None
    regimes: tuple[SickPayRegime, ...] = ()
    fixed_term: FixedTermSickLimit | None = None
    min_daily_contributions: int | None = None

    def for_regime(self, regime: str | None) -> InpsSickPayRates:
        """Return the table with the bands of ``regime`` in place of the rule.

        Args:
            regime: Id of a regime of :attr:`regimes`; ``None`` keeps the
                general bands.

        Returns:
            This table for ``None``; otherwise a copy whose bands and their
            provenance are the regime's.

        Raises:
            KeyError: When no regime has the id ``regime``.
        """
        if regime is None:
            return self
        found = next((r for r in self.regimes if r.id == regime), None)
        if found is None:
            raise KeyError(regime)
        return self.model_copy(
            update={
                "bands": found.bands,
                "bands_provenance": found.provenance,
                "min_daily_contributions": found.min_daily_contributions,
            }
        )

    def covers(
        self,
        sector: str,
        category: str | None,
        contract_type: str,
        ccnl: str | None = None,
    ) -> bool | None:
        """Return whether INPS pays the sickness indemnity to the worker.

        Returns:
            The ``covered`` flag of the first matching rule, ``None`` when
            no rule matches.
        """
        rule = next(
            (
                r
                for r in self.coverage
                if r.matches(sector, category, contract_type, ccnl)
            ),
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
        _check_band_chain(self.bands, self.carenza_days, "InpsSickPayRates")
        ids = [r.id for r in self.regimes]
        if len(set(ids)) != len(ids):
            msg = f"InpsSickPayRates: regime ids must be unique: {ids}"
            raise ValueError(msg)
        for regime in self.regimes:
            owner = f"InpsSickPayRates.regimes[{regime.id}]"
            _check_band_chain(regime.bands, self.carenza_days, owner)
        return self
