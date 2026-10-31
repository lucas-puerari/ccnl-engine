"""Per-episode sick pay with a comporto or a carenza counted over episodes.

A CCNL may keep the per-episode rates and still count over several
episodes:

- the comporto: the sick days of every episode of the calendar year,
  against ``max_duration_days`` (Commercio Art. 186);
- the comporto: the sick days of the months of a window that end on the
  day, against the days of the window of the worker's seniority, on top of
  ``max_duration_days`` for one illness (Edilizia ANCE Art. 26: nine months
  in 20, twelve in 24 above three and a half years);
- the carenza: paid at a lower rate from the n-th event of the year
  (:class:`~ccnl_engine.sickness.integration.models.CarenzaByEvent`).  A
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
from ccnl_engine.sickness.cumulation.rules import CcnlDay, window_start

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine.sickness.comporto.models import ComportoWindow
    from ccnl_engine.sickness.cumulation.rules import SicknessWorker
    from ccnl_engine.sickness.integration.models import SicknessRules
    from ccnl_engine.sickness.models import SicknessEpisode

__all__ = ["YearTreatment"]

_ONE = Decimal(1)


def _overlap(episode: SicknessEpisode, first: date, last: date) -> int:
    span = episode.within(first, last)
    return 0 if span is None else (span[1] - span[0]).days + 1


@dataclass(frozen=True)
class YearTreatment:
    """CCNL treatment of the days of one episode, counted over episodes.

    Attributes:
        rules: CCNL sickness rules, with a calendar-year comporto, comporto
            windows or a carenza by event.
        episode: The episode.
        earlier: Recorded episodes that started before it.
        worker: Seniority and known history of the worker; the history is
            complete from ``known_from``, all of it when ``None``.
        target_rate: Integration target of an episode day index.
    """

    rules: SicknessRules
    episode: SicknessEpisode
    earlier: tuple[SicknessEpisode, ...]
    worker: SicknessWorker
    target_rate: Callable[[int], Decimal]

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
        earlier = sum(_overlap(e, first, day) for e in self.earlier)
        return earlier + _overlap(self.episode, first, day)

    @cached_property
    def window(self) -> ComportoWindow | None:
        """Comporto window of the seniority on the first day of the episode.

        An unknown seniority takes the first window.
        """
        seniority = self.worker.seniority
        start = self.episode.started_on
        months = 0 if seniority is None else seniority.months_at(start)
        return window_of(self.rules.comporto_windows, months)

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
        first = date(start.year, 1, 1)
        if self.window is not None:
            first = min(first, window_start(start, 0, self.window.window_months))
        return known is not None and known > first

    def day(self, index: int, day: date) -> CcnlDay:
        """Return the CCNL treatment of ``day``.

        Args:
            index: Episode day index of the relapse chain.
            day: The sick day.

        Returns:
            Whether the day is past the comporto of the illness, of the
            calendar year or of the window, and its rates.
        """
        limit = self.rules.max_duration_days
        count = self.year_days(day) if self.rules.comporto_calendar_year else index
        window = self.window
        summed = window is not None and (
            self.days_from(window_start(day, 0, window.window_months), day)
            > window.comporto_days
        )
        return CcnlDay(
            beyond_comporto=count > limit or summed,
            rate=self.target_rate(index),
            carenza_rate=self.carenza_rate,
        )
