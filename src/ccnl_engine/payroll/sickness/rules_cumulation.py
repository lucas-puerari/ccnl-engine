"""CCNL sick pay counted over the sickness of several episodes.

A CCNL with a :class:`~ccnl_engine.contract.sickness.models.SicknessCumulation`
(Federmeccanica, Sez. IV Tit. VI Art. 2) counts, for each sick day:

- the treatment chain: the sick days of the episode and of the earlier
  episodes it follows with fewer than ``reset_after_days`` calendar days of
  work between them.  The days of the chain up to the full-pay days of the
  seniority band are paid in full, the later ones at the reduced rate;
- the comporto: the sick days within the ``window_years`` that end on the
  day.  A day past the comporto days of the band is outside what the CCNL
  integrates;
- the short absences of the calendar year: from the ``from_event``-th
  absence of at most ``max_days`` days, its first days are paid at the
  reduced rate of its rank, unless the CCNL exempts it.

The seniority band is the one of the first day of the episode.  The counts
read the episodes the state records; what the days before
:attr:`SicknessWorker.known_from` could change is reported by
:mod:`~ccnl_engine.payroll.sickness.results_cumulation`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.contract.sickness.models import (
        SicknessCumulation,
        SicknessRules,
        SicknessSeniorityBand,
    )
    from ccnl_engine.payroll.employment.inputs_seniority import SeniorityFact
    from ccnl_engine.payroll.sickness.models import SicknessEpisode

__all__ = [
    "CcnlDay",
    "CumulativeTreatment",
    "ShortAbsence",
    "SicknessWorker",
    "window_start",
]

_ONE = Decimal(1)


@dataclass(frozen=True)
class CcnlDay:
    """CCNL treatment of one sick day.

    Attributes:
        beyond_comporto: Whether the day is past the comporto.
        rate: Integration target of an indemnified day.
        carenza_rate: Share of the daily pay of a waiting day.
    """

    beyond_comporto: bool
    rate: Decimal
    carenza_rate: Decimal


@dataclass(frozen=True)
class SicknessWorker:
    """Facts of the worker the cumulated sickness is counted with.

    Attributes:
        seniority: Recognised seniority, ``None`` when not known.
        hired_on: First day of the employment, ``None`` when not known.
        known_from: First day from which the recorded episodes list every
            sick day of the employment; ``None`` when they list all of them.
    """

    seniority: SeniorityFact | None = None
    hired_on: date | None = None
    known_from: date | None = None


@dataclass(frozen=True)
class ShortAbsence:
    """Rate of the first days of a short absence.

    Attributes:
        rate: The rate, ``1`` without a reduction.
        unknown: Whether an unstated exemption could change it.
    """

    rate: Decimal = _ONE
    unknown: bool = False


def window_start(day: date, years: int) -> date:
    """Return the first day of the ``years`` that end on ``day``.

    Returns:
        The day after the same day ``years`` earlier (28 February for a
        29 February that year lacks).
    """
    try:
        anchor = day.replace(year=day.year - years)
    except ValueError:
        anchor = date(day.year - years, 2, 28)
    return anchor + timedelta(days=1)


def _overlap(episode: SicknessEpisode, first: date, last: date) -> int:
    span = episode.within(first, last)
    return 0 if span is None else (span[1] - span[0]).days + 1


@dataclass(frozen=True)
class CumulativeTreatment:
    """CCNL treatment of the days of one episode, after the earlier ones.

    Attributes:
        rules: CCNL sickness rules.
        cumulation: Their cumulation; the rules carry it.
        episode: The episode, from its first day.
        earlier: Recorded episodes that started before it, in start order.
        worker: Seniority, hire date and known history of the worker.
    """

    rules: SicknessRules
    cumulation: SicknessCumulation
    episode: SicknessEpisode
    earlier: tuple[SicknessEpisode, ...]
    worker: SicknessWorker = field(default_factory=SicknessWorker)

    def band_on(self, day: date) -> SicknessSeniorityBand:
        """Return the band of the seniority on ``day``, the first if unknown.

        Returns:
            The seniority band.
        """
        seniority = self.worker.seniority
        months = 0 if seniority is None else seniority.months_at(day)
        return self.cumulation.band_of(months)

    @cached_property
    def band(self) -> SicknessSeniorityBand:
        """Seniority band on the first day of the episode."""
        return self.band_on(self.episode.started_on)

    @cached_property
    def chain(self) -> tuple[int, date]:
        """Days of the earlier episodes of the chain, and its first day.

        The chain goes back through the recorded episodes while fewer than
        ``reset_after_days`` days of work separate one from the next.
        """
        start, days = self.episode.started_on, 0
        for previous in reversed(self.earlier):
            worked = (start - previous.ended_on).days - 1
            if worked >= self.cumulation.reset_after_days:
                break
            days += previous.days
            start = previous.started_on
        return days, start

    def chain_days(self, day: date) -> int:
        """Return the days of the treatment chain up to ``day``.

        Returns:
            The earlier days of the chain plus the episode up to ``day``.
        """
        return self.chain[0] + (day - self.episode.started_on).days + 1

    def window_days(self, day: date) -> int:
        """Return the sick days within the window that ends on ``day``.

        Returns:
            The recorded sick days from the start of the window, plus the
            episode up to ``day``.
        """
        first = window_start(day, self.cumulation.window_years)
        earlier = sum(_overlap(e, first, day) for e in self.earlier)
        return earlier + _overlap(self.episode, first, day)

    @cached_property
    def short(self) -> ShortAbsence:
        """Rate of the first days of the episode as a short absence.

        An exempt absence is neither reduced nor counted.  The rank of the
        episode ranges from one after the absences of its year known not
        exempt to one after every one not known exempt; when the two ranks
        pay differently, or the episode's own exemption is not stated and a
        rank reduces it, the higher pay is applied and the rate is unknown.
        """
        short = self.cumulation.short_absences
        episode = self.episode
        if short is None or episode.days > short.max_days:
            return ShortAbsence()
        same_year = [
            e
            for e in self.earlier
            if e.started_on.year == episode.started_on.year and e.days <= short.max_days
        ]
        stated = sum(e.short_absence_exempt is False for e in same_year)
        possible = sum(e.short_absence_exempt is not True for e in same_year)
        low, high = short.rate_of(1 + stated), short.rate_of(1 + possible)
        if episode.short_absence_exempt is True or high == _ONE:
            return ShortAbsence()
        if episode.short_absence_exempt is None:
            return ShortAbsence(unknown=True)
        return ShortAbsence(low, unknown=low != high)

    def day(self, index: int, day: date) -> CcnlDay:
        """Return the CCNL treatment of ``day``.

        Args:
            index: Episode day index of the INPS relapse chain; the
                cumulation counts its own days instead.
            day: The sick day.

        Returns:
            Whether the day is past the comporto, and its rates.
        """
        del index
        band = self.band
        rate = (
            self.rules.full_pay_integration_rate
            if self.chain_days(day) <= band.full_pay_days
            else self.cumulation.reduced_integration_rate
        )
        short = self.cumulation.short_absences
        first_days = 0 if short is None else short.first_days
        if (day - self.episode.started_on).days < first_days:
            rate = min(rate, self.short.rate)
        return CcnlDay(
            beyond_comporto=self.window_days(day) > band.comporto_days,
            rate=rate,
            carenza_rate=min(self.rules.carenza_integration_rate, rate),
        )

    def first_reduced(self) -> date:
        """Return the first day of the episode past the full-pay days.

        Returns:
            The day; it precedes the episode when the chain had already
            used the full-pay days.
        """
        offset = self.band.full_pay_days - self.chain[0]
        return self.episode.started_on + timedelta(days=offset)
