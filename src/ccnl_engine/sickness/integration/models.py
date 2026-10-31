"""Sickness rule models for CCNL contracts."""

import itertools
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.sickness.comporto.models import (
    ComportoBand,
    ComportoWindow,
    HospitalComportoRule,
    check_windows,
)

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
        window_months: Months of the window of the band, when the CCNL
            counts each band over its own (Logistica Confetra art. 63 c. 8:
            24 months up to 5 years of seniority, 30 above); ``None`` takes
            :attr:`SicknessCumulation.window_years`.
        steps: Rates of the days of the count past the full-pay days, by
            day of the count (PA comparti: 90% for the next 3 months, 50%
            for the next 6); a day in no step takes
            :attr:`SicknessCumulation.reduced_integration_rate`.
        serious_comporto_days: Comporto of a serious illness the CCNL
            extends (Concia art. 60 B: 2, 3, 4 months more), ``None``
            when it does not.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    seniority_months_from: int = Field(ge=0)
    full_pay_days: int = Field(ge=1)
    comporto_days: int = Field(ge=1)
    serious_comporto_days: int | None = Field(default=None, ge=1)
    window_months: int | None = Field(default=None, ge=1)
    steps: tuple[SicknessDayBand, ...] = ()

    @model_validator(mode="after")
    def _steps_after_full_pay(self) -> Self:
        if any(step.day_from <= self.full_pay_days for step in self.steps):
            msg = (
                f"steps must start after the {self.full_pay_days} full-pay days; "
                f"got {[step.day_from for step in self.steps]}"
            )
            raise ValueError(msg)
        return self

    def step_rate(self, count: int) -> Decimal | None:
        """Return the rate of day ``count`` of the count, if a step holds it.

        Returns:
            The rate of the first step holding ``count``, ``None`` otherwise.
        """
        return next((s.integration_rate for s in self.steps if s.holds(count)), None)


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


class HospitalStayRule(BaseModel):
    """Hospital stays paid in full within a reduced treatment.

    Federmeccanica Sez. Quarta Titolo VI art. 2: "I periodi di ricovero
    ospedaliero di durata superiore a 10 giorni continuativi sono retribuiti
    con l'intera retribuzione globale in aggiunta al trattamento economico
    di cui sopra fino ad un massimo di 61 giorni di calendario".

    Attributes:
        more_than_days: A stay counts when it lasts more than these
            consecutive days.
        max_full_days: Days of such stays paid in full at most, counted in
            the episode.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    more_than_days: int = Field(ge=0)
    max_full_days: int = Field(ge=1)


class SeriousIllnessRule(BaseModel):
    """Treatment of a particularly serious illness.

    Logistica Confetra art. 63: the "malattie particolarmente gravi, di cui
    alla circolare Inps 7.6.2016 n.95" are left out of the comporto count
    (c. 8) and paid "con la corresponsione dell'intera retribuzione globale
    mensile per 18 mesi" (c. 12).

    Concia art. 60 B instead extends the comporto of the "malattie
    invalidanti" (:attr:`SicknessSeniorityBand.serious_comporto_days`).

    Attributes:
        full_pay_days: Days of the episode paid in full; ``None`` when the
            CCNL pays it as any other.
        outside_comporto: Whether the episode is left out of the comporto.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    full_pay_days: int | None = Field(default=None, ge=1)
    outside_comporto: bool = False


class SicknessCumulation(BaseModel):
    """Sick pay and comporto counted over the sickness of several episodes.

    The treatment chain sums the sick days of consecutive episodes until one
    starts at least :attr:`reset_after_days` calendar days after the return
    to work; the comporto sums the sick days within the
    :attr:`window_years` that end on the day considered.  Without
    ``reset_after_days`` the full-pay days are counted over the same window
    as the comporto (CCNL lavoro domestico Art. 27 c. 7: "per un massimo di
    8, 10, 15 giorni complessivi nell'anno").

    Attributes:
        window_years: Years of sickness the comporto is counted over.
        reset_after_days: Calendar days of work after which a new episode
            starts a new treatment chain; ``None`` counts the full-pay days
            over the window.
        reduced_integration_rate: Rate of the days of the chain past the
            full-pay days of the band.
        bands: Seniority bands, in increasing seniority; the first starts
            at ``0`` months.
        short_absences: Reduction of repeated short absences, if any.
        hospital_stay: Hospital stays paid in full within the reduced days,
            if the CCNL says so.
        serious_illness: Treatment of a particularly serious illness, if
            the CCNL has one.
        hospital_comporto: Hospital stays left out of the comporto, if the
            CCNL says so.
        hospital_restart_day: Day of a hospital stay from which the
            treatment starts anew (Concia art. 60 C: "Il trattamento
            economico suindicato ricomincia ex novo [...] dal 16° giorno di
            ricovero ospedaliero"); ``None`` when the CCNL has no such rule.
        restart_after_full_pay_months: Months after the end of the full
            pay from which a new episode starts the treatment anew (Concia
            art. 60 C: "assenza per malattia iniziata dopo dodici mesi dal
            giorno in cui è cessato il diritto al trattamento economico del
            100%"); ``None`` without such a rule.
        periodic_checks_outside_comporto: Whether the episodes of periodic
            checks (``SicknessEpisode.periodic_check``) are left out of the
            comporto (Concia art. 60 B).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    window_years: int = Field(ge=1)
    reset_after_days: int | None = Field(default=None, ge=1)
    reduced_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    bands: tuple[SicknessSeniorityBand, ...] = Field(min_length=1)
    short_absences: ShortAbsenceReduction | None = None
    hospital_stay: HospitalStayRule | None = None
    serious_illness: SeriousIllnessRule | None = None
    hospital_comporto: HospitalComportoRule | None = None
    hospital_restart_day: int | None = Field(default=None, ge=1)
    restart_after_full_pay_months: int | None = Field(default=None, ge=1)
    periodic_checks_outside_comporto: bool = False

    @model_validator(mode="after")
    def _ordered_bands(self) -> Self:
        starts = [b.seniority_months_from for b in self.bands]
        full = [b.full_pay_days for b in self.bands]
        comporto = [b.comporto_days for b in self.bands]
        increasing = all(b > a for a, b in itertools.pairwise(starts)) and all(
            later >= earlier
            for values in (full, comporto)
            for earlier, later in itertools.pairwise(values)
        )
        if starts[0] != 0 or not increasing:
            msg = (
                "bands must start at 0 months, increase in seniority, never decrease"
                f" in full-pay or comporto days; got {starts}, {full}, {comporto}"
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
        comporto_windows: Comporto summed over the months before the day,
            by seniority, on top of ``max_duration_days`` for one illness.
        comporto_bands: Comporto of one illness by seniority, in place of
            ``max_duration_days`` (ABI Art. 66 c. 1).
        carenza_by_event: Lower carenza from the n-th event of the year.
        carenza_min_days: The carenza is paid only when the sickness lasts
            more than this many calendar days (Pubblici esercizi FIPE
            Art. 190: "qualora la durata della malattia superi i cinque
            giorni"); ``None`` pays it whatever the length.
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
        inps_regime: Id of the INPS indemnity regime of the workers of the
            CCNL (:class:`~ccnl_engine.sickness.indemnity.models.SickPayRegime`),
            e.g. ``pubblici_esercizi`` (80% for the whole sickness);
            ``None`` for the general bands.
        daily_divisor_method: Daily quota of a sick day when it differs
            from the one of the absence rules (CCNL lavoro domestico,
            chiarimento a verbale 2: sickness counts calendar days, in
            thirtieths, absences working days, in twenty-sixths); ``None``
            takes the absence rules'.
        provenance: Links this rule to its CCNL article.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    carenza_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    full_pay_integration_rate: Decimal = Field(ge=Decimal(0), le=Decimal(1))
    tiers: tuple[SicknessTier, ...] = Field(default=())
    day_bands: tuple[SicknessDayBand, ...] = Field(default=())
    comporto_calendar_year: bool = False
    comporto_windows: tuple[ComportoWindow, ...] = ()
    comporto_bands: tuple[ComportoBand, ...] = ()
    carenza_by_event: CarenzaByEvent | None = None
    carenza_min_days: int | None = Field(default=None, ge=1)
    max_duration_days: int = Field(default=180, ge=1)
    cumulation: SicknessCumulation | None = None
    net_basis: bool = False
    apprentices_excluded: bool = False
    inps_regime: str | None = None
    daily_divisor_method: DailyDivisorMethod | None = None
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _one_model(self) -> Self:
        check_windows(self.comporto_windows)
        check_windows(self.comporto_bands)
        per_episode = (
            self.tiers
            or self.day_bands
            or self.comporto_calendar_year
            or self.comporto_windows
            or self.comporto_bands
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
