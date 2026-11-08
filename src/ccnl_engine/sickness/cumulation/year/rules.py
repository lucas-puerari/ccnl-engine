"""Per-episode sick pay with a comporto or a carenza counted over episodes.

A CCNL may keep the per-episode rates and still count over several
episodes:

- the comporto: the sick days of every episode of the calendar year,
  against ``max_duration_days`` (Commercio Art. 186);
- the comporto: the sick days of the months of a window that end on the
  day, against the days of the window of the worker's seniority, on top of
  ``max_duration_days`` for one illness (Edilizia ANCE Art. 26: nine months
  in 20, twelve in 24 above three and a half years);
- the comporto of one illness by the worker's seniority, in place of
  ``max_duration_days`` (ABI Art. 66 c. 1: 6 to 22 months);
- the carenza: paid at a lower rate from the n-th event of the year
  (:class:`~ccnl_engine.sickness.integration.condition.models.CarenzaByEvent`).  A
  relapse continues its event; an event the CCNL exempts is not counted.

The count reads the recorded episodes.  When the history is known only from
a day after the start of the year or of the window, or an earlier event
does not say whether the CCNL exempts it, the count can be wrong: the
higher pay is applied and the treatment says so
(:attr:`YearTreatment.history_reach`, :attr:`YearTreatment.exemption_reach`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING

from ccnl_engine.sickness.comporto.models import window_of
from ccnl_engine.sickness.cumulation.rules import CcnlDay
from ccnl_engine.sickness.diagnosis import SeriousIllnessKind
from ccnl_engine.sickness.window.rules import window_start

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.sickness.comporto.models import ComportoBand, ComportoWindow
    from ccnl_engine.sickness.cumulation.rules import SicknessWorker
    from ccnl_engine.sickness.integration.models import SicknessRules
    from ccnl_engine.sickness.models import SicknessEpisode

__all__ = ["YearTreatment"]

_ONE = Decimal(1)


def _overlap(episode: SicknessEpisode, first: date, last: date) -> int:
    span = episode.within(first, last)
    return 0 if span is None else (span[1] - span[0]).days + 1


def _hospital(episode: SicknessEpisode, first: date, last: date) -> int:
    """Return the hospital days of ``episode`` from ``first`` to ``last``.

    Returns:
        The days of its stated stays within the span, zero without stays.
    """
    return sum(
        max(0, (min(end, last) - max(start, first)).days + 1)
        for start, end in episode.hospital_stays or ()
    )


@dataclass(frozen=True)
class YearTreatment:
    """CCNL treatment of the days of one episode, counted over episodes.

    Attributes:
        rules: CCNL sickness rules, with a calendar-year comporto, comporto
            windows or bands, or a carenza by event.
        episode: The episode.
        earlier: Recorded episodes that started before it.
        worker: Seniority and known history of the worker; the history is
            complete from ``known_from``, all of it when ``None``.
        target_rate: Integration target of an episode day index.
        offset: Sick days of the episodes the episode continues as a relapse.
    """

    rules: SicknessRules
    episode: SicknessEpisode
    earlier: tuple[SicknessEpisode, ...]
    worker: SicknessWorker
    target_rate: Callable[[int], Decimal]
    offset: int = 0

    def year_days(self, day: date) -> int:
        """Return the sick days of the calendar year of ``day`` up to ``day``.

        Returns:
            The recorded days of the year and those of the episode.
        """
        return self.days_from(date(day.year, 1, 1), day)

    def days_from(self, first: date, day: date) -> int:
        """Return the sick days from ``first`` up to ``day``.

        Returns:
            The recorded days and those of the episode.
        """
        episodes = (*self.earlier, self.episode)
        days = sum(_overlap(e, first, day) for e in episodes)
        if self.rules.excluded_treatment_days:
            days -= sum(
                first <= excluded <= day
                for e in episodes
                for excluded in e.excluded_comporto_days or ()
            )
        return days

    def window_days(self, window: ComportoWindow, day: date) -> int:
        """Return the sick days of ``window`` ending on ``day``.

        Returns:
            The days from the start of the window, less the days of the
            hospital stays when the window leaves them out.
        """
        first = window_start(day, 0, window.window_months)
        days = self.days_from(first, day)
        if window.hospital_excluded:
            episodes = (*self.earlier, self.episode)
            days -= sum(_hospital(e, first, day) for e in episodes)
        return days

    @cached_property
    def _months(self) -> int:
        """Seniority months on the first day of the episode, ``0`` if unknown."""
        seniority = self.worker.seniority
        return 0 if seniority is None else seniority.months_at(self.episode.started_on)

    @cached_property
    def window(self) -> ComportoWindow | None:
        """Comporto window of the seniority on the first day of the episode.

        An unknown seniority takes the first window.
        """
        return window_of(self.rules.comporto_windows, self._months)

    @cached_property
    def band(self) -> ComportoBand | None:
        """Comporto band of the seniority on the first day of the episode.

        An unknown seniority takes the first band.
        """
        return window_of(self.rules.comporto_bands, self._months)

    @property
    def limit(self) -> int:
        """Comporto of one illness: of the seniority band, if the CCNL has bands."""
        band = self.band
        return self._limit(band) if band is not None else self.rules.max_duration_days

    def _limit(self, band: ComportoBand) -> int:
        """Select the documented diagnosis-specific limit, if provided.

        Returns:
            The qualifying limit, otherwise the ordinary limit.
        """
        kind = self.episode.serious_illness_kind
        if kind is SeriousIllnessKind.ONCOLOGICAL and band.oncological_comporto_days:
            return band.oncological_comporto_days
        if kind is not None or (
            band.oncological_comporto_days is None and self.episode.serious_illness
        ):
            return band.serious_comporto_days or band.comporto_days
        return band.comporto_days

    @property
    def seniority_reach(self) -> bool:
        """Whether an unknown seniority could keep the job past the first band.

        The days of the episode and of those it continues pass the comporto
        of the first band, and a later band would give more.
        """
        bands = self.rules.comporto_bands
        return (
            self.worker.seniority is None
            and len(bands) > 1
            and self.offset + self.episode.days > bands[0].comporto_days
        )

    @cached_property
    def _events(self) -> tuple[Decimal, Decimal]:
        """Carenza rates of the lowest and of the highest rank of the episode.

        The lowest rank follows every earlier event not known exempt, the
        highest only those known not exempt.
        """
        events = self.rules.carenza_by_event
        if events is None or self.episode.relapse_of is not None:
            return _ONE, _ONE
        year = self.episode.started_on.year
        same = [
            e
            for e in self.earlier
            if e.started_on.year == year and e.relapse_of is None
        ]
        stated = sum(e.short_absence_exempt is False for e in same)
        possible = sum(e.short_absence_exempt is not True for e in same)
        return events.rate_of(1 + possible), events.rate_of(1 + stated)

    @property
    def carenza_rate(self) -> Decimal:
        """Carenza rate of the episode: the higher one when the rank is unsure."""
        if self.episode.short_absence_exempt is True:
            return self.rules.carenza_integration_rate
        return min(self.rules.carenza_integration_rate, self._events[1])

    @property
    def exemption_reach(self) -> bool:
        """Whether an unstated exemption could lower the carenza paid."""
        low, high = self._events
        if self.episode.short_absence_exempt is True or high == _ONE == low:
            return False
        return low != high or self.episode.short_absence_exempt is None

    @property
    def history_reach(self) -> bool:
        """Whether sick days before the known history could change the count."""
        known = self.worker.known_from
        start = self.episode.started_on
        rules = self.rules
        firsts = []
        if rules.comporto_calendar_year or rules.carenza_by_event is not None:
            firsts.append(date(start.year, 1, 1))
        if self.window is not None:
            firsts.append(window_start(start, 0, self.window.window_months))
        return known is not None and bool(firsts) and known > min(firsts)

    def day(self, index: int, day: date) -> CcnlDay:
        """Return the CCNL treatment of ``day``.

        Args:
            index: Episode day index of the relapse chain.
            day: The sick day.

        Returns:
            Whether the day is past the comporto of the illness (of the
            seniority band, if any), of the calendar year or of the window,
            and its rates.
        """
        limit = self.limit
        count = self._count(index, day)
        window = self.window
        summed = window is not None and self.window_days(window, day) > self._limit(
            window
        )
        return CcnlDay(
            beyond_comporto=count > limit or summed,
            rate=self._rate(index, day, count),
            carenza_rate=self.carenza_rate,
        )

    def _count(self, index: int, day: date) -> int:
        """Count the day against one illness, excluding qualifying treatment.

        Returns:
            Days counted toward the episode or calendar-year limit.
        """
        count = self.year_days(day) if self.rules.comporto_calendar_year else index
        if not self.rules.excluded_treatment_days or self.rules.comporto_calendar_year:
            return count
        chain = {self.episode.episode_id}
        previous = self.episode.relapse_of
        while previous is not None:
            found = next((e for e in self.earlier if e.episode_id == previous), None)
            if found is None or found.episode_id in chain:
                break
            chain.add(found.episode_id)
            previous = found.relapse_of
        return count - sum(
            excluded <= day
            for e in (*self.earlier, self.episode)
            if e.episode_id in chain
            for excluded in e.excluded_comporto_days or ()
        )

    def _rate(self, index: int, day: date, count: int) -> Decimal:
        """Apply the serious-illness pay bands to the counted days.

        Returns:
            The qualifying rate, or the ordinary day rate.
        """
        rate = self.target_rate(index)
        if not self.episode.serious_illness:
            return rate
        window = self.window
        paid_count = self.window_days(window, day) if window is not None else count
        band = next(
            (b for b in self.rules.serious_day_bands if b.holds(paid_count)), None
        )
        return band.integration_rate if band is not None else rate
