"""CCNL sick pay counted over the sickness of several episodes.

A CCNL with a :class:`~ccnl_engine.sickness.integration.models.SicknessCumulation`
(Federmeccanica, Sez. IV Tit. VI Art. 2) counts, for each sick day:

- the treatment chain: the sick days of the episode and of the earlier
  episodes it follows with fewer than ``reset_after_days`` calendar days of
  work between them, or, without ``reset_after_days``, the sick days within
  the window of the comporto (CCNL lavoro domestico Art. 27 c. 7).  The
  days of the chain up to the full-pay days of the seniority band are paid
  in full, the later ones at the rate of the step of the band holding them
  (PA comparti: 90%, then 50%), else at the reduced rate;
- the comporto: the sick days within the ``window_years``, or the months
  of the band's own window, that end on the day.  A day past the comporto
  days of the band is outside what the CCNL integrates;
- the short absences of the calendar year: from the ``from_event``-th
  absence of at most ``max_days`` days, its first days are paid at the
  reduced rate of its rank, unless the CCNL exempts it.

The seniority band is the one of the first day of the episode.  The counts
read the episodes the state records; what the days before
:attr:`SicknessWorker.known_from` could change is reported by
:mod:`~ccnl_engine.sickness.cumulation.results`.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.seniority.inputs import SeniorityFact
    from ccnl_engine.sickness.integration.models import (
        SicknessCumulation,
        SicknessRules,
        SicknessSeniorityBand,
    )
    from ccnl_engine.sickness.models import SicknessEpisode

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


def window_start(day: date, years: int, months: int = 0) -> date:
    """Return the first day of the ``years`` and ``months`` that end on ``day``.

    Returns:
        The day after the same day ``years`` and ``months`` earlier, or
        after the last day of that month when it is shorter (28 February
        for a 29 February that year lacks).
    """
    total = (day.year - years) * 12 + day.month - 1 - months
    year, month = divmod(total, 12)
    last = calendar.monthrange(year, month + 1)[1]
    anchor = date(year, month + 1, min(day.day, last))
    return anchor + timedelta(days=1)


def _stay_overlap(stay: tuple[date, date], first: date, last: date) -> int:
    start, end = max(stay[0], first), min(stay[1], last)
    return max((end - start).days + 1, 0)


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
        ``reset_after_days`` days of work separate one from the next; a
        window count (no ``reset_after_days``) has no chain before the
        episode.
        """
        start, days = self.episode.started_on, 0
        reset = self.cumulation.reset_after_days
        if reset is None:
            return days, start
        for previous in reversed(self.earlier):
            worked = (start - previous.ended_on).days - 1
            if worked >= reset:
                break
            days += previous.days
            start = previous.started_on
        return days, start

    def chain_days(self, day: date) -> int:
        """Return the days of the treatment chain up to ``day``.

        Returns:
            The earlier days of the chain plus the episode up to ``day``;
            the sick days of the window for a window count.
        """
        if self.cumulation.reset_after_days is None:
            return self.window_days(day)
        return self.chain[0] + (day - self.episode.started_on).days + 1

    def window_first(self, day: date) -> date:
        """Return the first day of the window of the band that ends on ``day``.

        Returns:
            The start of the band's own window in months when it has one,
            else of the ``window_years`` of the cumulation.
        """
        months = self.band.window_months
        if months is None:
            return window_start(day, self.cumulation.window_years)
        return window_start(day, 0, months)

    def window_days(self, day: date) -> int:
        """Return the sick days within the window that ends on ``day``.

        Returns:
            The recorded sick days from the start of the window, plus the
            episode up to ``day``.
        """
        first = self.window_first(day)
        earlier = sum(_overlap(e, first, day) for e in self.earlier if self._counted(e))
        own = _overlap(self.episode, first, day) if self._counted(self.episode) else 0
        return earlier + own

    def comporto_count(self, day: date) -> int:
        """Return the sick days the comporto counts on ``day``.

        Returns:
            :meth:`window_days` less the days of long hospital stays the
            CCNL leaves out, up to their maximum.
        """
        days = self.window_days(day)
        rule = self.cumulation.hospital_comporto
        if rule is None:
            return days
        first = self.window_first(day)
        episodes = [e for e in (*self.earlier, self.episode) if self._counted(e)]
        stays = sum(
            _stay_overlap(stay, first, day)
            for e in episodes
            for stay in e.hospital_stays or ()
            if (stay[1] - stay[0]).days + 1 > rule.more_than_days
        )
        return days - min(stays, rule.max_days)

    def comporto_limit(self) -> int:
        """Return the comporto of the band, extended for a serious illness.

        Returns:
            ``serious_comporto_days`` for a serious illness when the band
            has it, else ``comporto_days``.
        """
        band = self.band
        extended = band.serious_comporto_days
        if extended is not None and self.episode.serious_illness:
            return extended
        return band.comporto_days

    def _counted(self, episode: SicknessEpisode) -> bool:
        """Return whether ``episode`` counts toward the comporto.

        Returns:
            ``False`` for a serious illness the CCNL leaves out of it.
        """
        rule = self.cumulation.serious_illness
        return not (
            rule is not None and rule.outside_comporto and episode.serious_illness
        )

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
        count = self.chain_days(day)
        rate = self._rate(count, day)
        short = self.cumulation.short_absences
        first_days = 0 if short is None else short.first_days
        if (day - self.episode.started_on).days < first_days:
            rate = min(rate, self.short.rate)
        return CcnlDay(
            beyond_comporto=self.comporto_count(day) > self.comporto_limit(),
            rate=rate,
            carenza_rate=min(self.rules.carenza_integration_rate, rate),
        )

    def _rate(self, count: int, day: date) -> Decimal:
        """Return the integration rate of ``day``, the ``count``-th of the chain.

        A serious illness the CCNL treats apart is paid in full for its days
        and at the reduced rate after them; otherwise the band decides, a
        long hospital stay paying a reduced day in full.

        Returns:
            The rate of the day.
        """
        serious = self.cumulation.serious_illness
        if (
            serious is not None
            and serious.full_pay_days is not None
            and self.episode.serious_illness
        ):
            if (day - self.episode.started_on).days < serious.full_pay_days:
                return self.rules.full_pay_integration_rate
            return self.cumulation.reduced_integration_rate
        band = self.band
        if count <= band.full_pay_days:
            return self.rules.full_pay_integration_rate
        step = band.step_rate(count)
        rate = self.cumulation.reduced_integration_rate if step is None else step
        return self._hospital(day, rate)

    def _hospital(self, day: date, rate: Decimal) -> Decimal:
        """Return the rate of a reduced day, full within a long hospital stay.

        Returns:
            The full-pay rate for a day of a stay longer than the CCNL days,
            within the days paid in full at most; ``rate`` otherwise.
        """
        stay = self.cumulation.hospital_stay
        if stay is None:
            return rate
        days = self.episode.long_stay_days(stay.more_than_days, day)
        if 0 < days <= stay.max_full_days:
            return self.rules.full_pay_integration_rate
        return rate

    def first_reduced(self) -> date:
        """Return the first day of the episode past the full-pay days.

        Returns:
            The day; it precedes the episode when the chain had already
            used the full-pay days.  For a window count, the first day of
            the episode whose window holds more than the full-pay days, or
            the day after the episode when none does.
        """
        if self.cumulation.reset_after_days is None:
            first, last = self.episode.started_on, self.episode.ended_on
            days = (first + timedelta(days=n) for n in range((last - first).days + 1))
            return next(
                (d for d in days if self.window_days(d) > self.band.full_pay_days),
                last + timedelta(days=1),
            )
        offset = self.band.full_pay_days - self.chain[0]
        return self.episode.started_on + timedelta(days=offset)
