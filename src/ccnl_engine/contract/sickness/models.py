"""Sickness rule models for CCNL contracts."""

import itertools
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.models_chain import RuleProvenance

_ONE = Decimal(1)


class SicknessTier(BaseModel):
    """One month-gated sick-pay integration tier.

    When the total sick days in the episode fall within
    ``[month_from, month_until)`` calendar months (30 days each), the
    ``integration_rate`` applies instead of ``full_pay_integration_rate``.
    Tiers are evaluated in descending order of ``month_from``; the first
    matching tier wins.  Use :attr:`SicknessRules.full_pay_integration_rate`
    as the flat fallback when no tier matches or when cumulative context is
    not available.

    Attributes:
        month_from: First month (1-indexed) in which this tier applies.
        month_until: First month in which this tier no longer applies
            (exclusive upper bound).  ``None`` means open-ended.
        integration_rate: Target fraction of gross daily pay for this tier.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    month_from: int = Field(ge=1)
    month_until: int | None = Field(default=None, ge=2)
    integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))


class SicknessDayBand(BaseModel):
    """One day-gated sick-pay integration band of an episode.

    The days of an episode (relapses continuing it) from ``day_from`` up to
    ``day_until`` (exclusive) take ``integration_rate``, e.g. Commercio
    Art. 187: 75% from day 4 to day 20, 100% from day 21.

    Attributes:
        day_from: First episode day of the band (1-indexed).
        day_until: First episode day past the band; ``None`` is open-ended.
        integration_rate: Target fraction of the daily pay of the band.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    day_from: int = Field(ge=1)
    day_until: int | None = Field(default=None, ge=2)
    integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))

    def holds(self, index: int) -> bool:
        """Return whether episode day ``index`` falls in the band.

        Returns:
            ``True`` from :attr:`day_from` up to :attr:`day_until`.
        """
        return self.day_from <= index and (
            self.day_until is None or index < self.day_until
        )


class SicknessSeniorityBand(BaseModel):
    """Sick-pay entitlement of the workers of one seniority band.

    Attributes:
        seniority_months_from: Completed months of seniority from which the
            band applies; ``0`` for the first band.
        full_pay_days: Calendar days of the treatment chain paid at
            :attr:`SicknessRules.full_pay_integration_rate`; the later days
            are paid at :attr:`SicknessCumulation.reduced_integration_rate`.
        comporto_days: Calendar days of sickness within the window the job
            is kept for (comporto breve); the days past it are outside what
            the CCNL integrates.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    seniority_months_from: int = Field(ge=0)
    full_pay_days: int = Field(ge=1)
    comporto_days: int = Field(ge=1)


class ShortAbsenceReduction(BaseModel):
    """Lower pay of the first days of repeated short absences in a year.

    Attributes:
        max_days: Longest absence, in calendar days, that counts as short.
        from_event: First short absence of the calendar year reduced.
        first_days: Days of each reduced absence paid at the reduced rate.
        rates: Rate of the ``from_event``-th short absence, then of each
            later one; the last rate applies to every absence after it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_days: int = Field(ge=1)
    from_event: int = Field(ge=2)
    first_days: int = Field(ge=1)
    rates: tuple[Decimal, ...] = Field(min_length=1)

    def rate_of(self, ordinal: int) -> Decimal:
        """Return the pay rate of the first days of the ``ordinal``-th absence.

        Returns:
            ``1`` before :attr:`from_event`, the matching rate after.
        """
        if ordinal < self.from_event:
            return _ONE
        return self.rates[min(ordinal - self.from_event, len(self.rates) - 1)]


class CarenzaByEvent(BaseModel):
    """Carenza paid at a lower rate from the n-th sickness event of a year.

    Commercio Art. 187: the carenza is integrated at 100% for the first two
    events of the calendar year, 66% for the third, 50% for the fourth and
    not from the fifth.  A relapse continues its event; an event the CCNL
    exempts (``SicknessEpisode.short_absence_exempt``) is not counted.

    Attributes:
        from_event: First event of the calendar year paid less.
        rates: Carenza rate of the ``from_event``-th event, then of each
            later one; the last rate applies to every event after it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    from_event: int = Field(ge=2)
    rates: tuple[Decimal, ...] = Field(min_length=1)

    def rate_of(self, ordinal: int) -> Decimal:
        """Return the carenza rate of the ``ordinal``-th event of the year.

        Returns:
            ``1`` before :attr:`from_event`, the matching rate after.
        """
        if ordinal < self.from_event:
            return _ONE
        return self.rates[min(ordinal - self.from_event, len(self.rates) - 1)]


class SicknessCumulation(BaseModel):
    """Sick pay and comporto counted over the sickness of several episodes.

    The treatment chain sums the sick days of consecutive episodes until one
    starts at least :attr:`reset_after_days` calendar days after the return
    to work; the comporto sums the sick days within the
    :attr:`window_years` that end on the day considered.

    Attributes:
        window_years: Years of sickness the comporto is counted over.
        reset_after_days: Calendar days of work after which a new episode
            starts a new treatment chain.
        reduced_integration_rate: Rate of the days of the chain past the
            full-pay days of the band.
        bands: Seniority bands, in increasing seniority; the first starts
            at ``0`` months.
        short_absences: Reduction of repeated short absences, if any.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    window_years: int = Field(ge=1)
    reset_after_days: int = Field(ge=1)
    reduced_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    bands: tuple[SicknessSeniorityBand, ...] = Field(min_length=1)
    short_absences: ShortAbsenceReduction | None = None

    @model_validator(mode="after")
    def _ordered_bands(self) -> Self:
        starts = [b.seniority_months_from for b in self.bands]
        full = [b.full_pay_days for b in self.bands]
        comporto = [b.comporto_days for b in self.bands]
        increasing = all(
            later > earlier
            for values in (starts, full, comporto)
            for earlier, later in itertools.pairwise(values)
        )
        if starts[0] != 0 or not increasing:
            msg = (
                "bands must start at 0 months and increase in seniority, "
                f"full-pay days and comporto days; got {starts}, {full}, {comporto}"
            )
            raise ValueError(msg)
        return self

    def band_of(self, months: int) -> SicknessSeniorityBand:
        """Return the band of a seniority of ``months`` completed months.

        Returns:
            The last band whose start is at most ``months``.
        """
        return [b for b in self.bands if b.seniority_months_from <= months][-1]


class SicknessRules(BaseModel):
    """Layer 3 rules for sick leave (malattia ordinaria) integration.

    Defines how the CCNL supplements the statutory INPS indemnity during
    illness.  The engine computes INPS indemnity from the bundled rate
    file; ``carenza_integration_rate`` and ``full_pay_integration_rate``
    determine the company's share on top.

    The CCNL tier and the comporto are counted either on the days of one
    episode and the relapses it continues (``tiers`` and
    ``max_duration_days``), or over the sickness of several episodes
    (``cumulation``); a rule sets one model, not both.

    Attributes:
        carenza_integration_rate: Fraction of gross daily pay the company
            covers during the waiting period (days 1-``carenza_days``).
            ``1.0`` = full pay; ``0.0`` = no company coverage.  With
            ``cumulation`` the waiting day takes the lower of this rate and
            the rate of the day.
        full_pay_integration_rate: Target fraction of gross daily pay the
            worker should receive during INPS-covered days.  The company
            pays the difference above the INPS indemnity.  ``1.0`` = 100%
            guaranteed by the CCNL (company tops up to full gross).
            Used as flat fallback when ``tiers`` is empty or cumulative
            context is unavailable.
        tiers: Optional list of month-gated integration tiers for CCNLs
            that reduce the integration rate after several months of
            sickness (e.g. 100% for months 1-9, 90% for months 10-12).
        day_bands: Day-gated integration bands, for CCNLs that set the rate
            by the day of the episode; a day in a band takes its rate
            before any tier.
        comporto_calendar_year: Whether ``max_duration_days`` counts the
            sick days of every episode of the calendar year of the day
            (Commercio Art. 186: 180 days "in un anno solare") instead of
            the days of one episode.
        carenza_by_event: Lower carenza from the n-th event of the year.
        max_duration_days: Number of calendar days after which sick leave
            exceeds the comporto period.  Days beyond this limit are not
            modelled by the engine.
        cumulation: Treatment chain, comporto window and seniority bands of
            a CCNL that counts the sickness of several episodes.
        net_basis: The rates are of the net daily pay (Commercio Art. 187):
            the INPS share, free of contributions, is grossed up by the
            worker's INPS rate before the company tops it up.
        apprentices_excluded: The company owes apprentices no integration
            and no carenza (Commercio Art. 187: "né agli apprendisti").
        provenance: Links this rule to its CCNL article.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    carenza_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    full_pay_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    tiers: tuple[SicknessTier, ...] = Field(default=())
    day_bands: tuple[SicknessDayBand, ...] = Field(default=())
    comporto_calendar_year: bool = False
    carenza_by_event: CarenzaByEvent | None = None
    max_duration_days: int = Field(default=180, ge=1)
    cumulation: SicknessCumulation | None = None
    net_basis: bool = False
    apprentices_excluded: bool = False
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _one_model(self) -> Self:
        per_episode = (
            self.tiers
            or self.day_bands
            or self.comporto_calendar_year
            or self.carenza_by_event is not None
            or "max_duration_days" in self.model_fields_set
        )
        if self.cumulation is not None and per_episode:
            msg = (
                "sickness rules with a cumulation count the tier and the "
                "comporto over it: drop tiers and max_duration_days"
            )
            raise ValueError(msg)
        return self
