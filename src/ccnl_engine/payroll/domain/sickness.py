"""Sickness episode: one illness, its interval and the episode it continues.

An episode is a fact of the medical certificates: the first and last day of
the illness and, for a relapse (*ricaduta*), the episode it continues.  The
engine derives everything else from the CCNL and the INPS rules
(:mod:`~ccnl_engine.payroll.domain.sick_days`).

An episode that spans several months is passed, with the same
:attr:`~SicknessEpisode.episode_id` and start, to every regular run whose
month it touches; each run pays the days of its own month.  The runs record
the days they processed in the accrual state, so later episodes see the
earlier ones whatever run computes them.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta

from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    require_bool,
    require_date,
    require_str,
)

__all__ = ["SicknessEpisode", "SicknessHistory"]

_FEATURE = "sickness"
_OWNER = "SicknessEpisode"


@dataclass(frozen=True)
class SicknessEpisode:
    """One sickness episode, a work event of every run whose month it touches.

    Attributes:
        episode_id: Stable identifier of the episode, the same in every run
            (e.g. the protocol number of the first certificate).
        started_on: First day of illness.
        ended_on: Last day of illness on the certificates known so far.  A
            later run may pass a later day when the illness is extended.
        relapse_of: Identifier of the episode this one continues, when the
            certificate marks it as a relapse (*ricaduta*): the days of both
            count as one episode, so no new waiting period applies.
        short_absence_exempt: Whether the CCNL exempts the absence from the
            lower pay of repeated absences (for Federmeccanica: a hospital
            stay or day hospital, sickness during a certified pregnancy, or
            one of the diseases the CCNL lists; for Commercio, Art. 187: a
            hospital stay, day hospital or dialysis, an initial prognosis of
            at least 12 days, the listed diseases, or a pregnancy); ``None``
            when not stated.  Read only by a CCNL that reduces short
            absences or the carenza by event, when the reduction could
            apply.

    Raises:
        InvalidInputError: When the identifier is blank, a day is not a
            date, ``short_absence_exempt`` is not a bool, the episode ends
            before it starts or continues itself.
    """

    episode_id: str
    started_on: date
    ended_on: date
    relapse_of: str | None = None
    short_absence_exempt: bool | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_str(
            self.episode_id, f"{_OWNER}.episode_id", feature=_FEATURE, non_blank=True
        )
        require_date(self.started_on, f"{_OWNER}.started_on", feature=_FEATURE)
        require_date(self.ended_on, f"{_OWNER}.ended_on", feature=_FEATURE)
        require_str(
            self.relapse_of,
            f"{_OWNER}.relapse_of",
            feature=_FEATURE,
            non_blank=True,
            optional=True,
        )
        if self.short_absence_exempt is not None:
            require_bool(
                self.short_absence_exempt,
                f"{_OWNER}.short_absence_exempt",
                feature=_FEATURE,
            )
        if self.ended_on < self.started_on:
            msg = (
                f"{_OWNER}.ended_on ({self.ended_on}) must not precede "
                f"started_on ({self.started_on})"
            )
            raise InvalidInputError(msg, field=f"{_OWNER}.ended_on", feature=_FEATURE)
        if self.relapse_of == self.episode_id:
            msg = f"{_OWNER} '{self.episode_id}' cannot be a relapse of itself"
            raise InvalidInputError(msg, field=f"{_OWNER}.relapse_of", feature=_FEATURE)

    @property
    def event_date(self) -> date:
        """First day of the episode: the date of the event."""
        return self.started_on

    @property
    def days(self) -> int:
        """Calendar days from :attr:`started_on` to :attr:`ended_on`."""
        return (self.ended_on - self.started_on).days + 1

    def within(self, first: date, last: date) -> tuple[date, date] | None:
        """Return the days of the episode from ``first`` to ``last``.

        Returns:
            The first and last sick day of the interval, ``None`` when the
            episode does not touch it.
        """
        start, end = max(first, self.started_on), min(last, self.ended_on)
        return None if end < start else (start, end)

    def through(self, day: date) -> SicknessEpisode:
        """Return the episode cut at ``day``, the last day processed.

        Returns:
            The episode ending on ``day`` when it lasts beyond it.
        """
        return self if self.ended_on <= day else replace(self, ended_on=day)

    def before(self, day: date) -> SicknessEpisode | None:
        """Return the part of the episode before ``day``.

        Returns:
            The episode cut on the day before ``day``, ``None`` when it
            starts on or after ``day``.
        """
        if self.started_on >= day:
            return None
        return self.through(day - timedelta(days=1))


@dataclass(frozen=True)
class SicknessHistory:
    """Episodes processed by earlier runs, as far as they processed them.

    Attributes:
        episodes: Recorded episodes, each cut at its last processed day.
    """

    episodes: tuple[SicknessEpisode, ...] = ()

    def _find(self, episode_id: str) -> SicknessEpisode | None:
        return next((e for e in self.episodes if e.episode_id == episode_id), None)

    def offset(self, episode: SicknessEpisode) -> int:
        """Return the days counted before ``episode`` in its relapse chain.

        Returns:
            Zero for a new episode; for a relapse, the days of the episodes
            it continues.

        Raises:
            InvalidInputError: When the episode it continues is not
                recorded.
        """
        if episode.relapse_of is None:
            return 0
        previous = self._find(episode.relapse_of)
        if previous is None or previous.started_on >= episode.started_on:
            msg = (
                f"episode '{episode.episode_id}' continues '{episode.relapse_of}', "
                "which no earlier run recorded"
            )
            raise InvalidInputError(msg, field=f"{_OWNER}.relapse_of", feature=_FEATURE)
        return self.offset(previous) + previous.days

    def check(self, episode: SicknessEpisode, first: date | None = None) -> None:
        """Check ``episode`` against the recorded ones.

        Args:
            episode: The episode a run is about to pay.
            first: First day the run pays, when it pays any.

        Raises:
            InvalidInputError: When a recorded episode of the same id starts
                on another day or was already paid on or after ``first``, or
                another episode overlaps it.
        """
        for other in self.episodes:
            same = other.episode_id == episode.episode_id
            if same and other.started_on != episode.started_on:
                msg = (
                    f"episode '{episode.episode_id}' was recorded from "
                    f"{other.started_on}, not {episode.started_on}"
                )
                raise InvalidInputError(
                    msg, field=f"{_OWNER}.started_on", feature=_FEATURE
                )
            if same and first is not None and other.ended_on >= first:
                msg = (
                    f"episode '{episode.episode_id}' was already paid through "
                    f"{other.ended_on}, on or after {first}"
                )
                raise InvalidInputError(
                    msg, field=f"{_OWNER}.ended_on", feature=_FEATURE
                )
            if not same and other.within(episode.started_on, episode.ended_on):
                msg = (
                    f"episode '{episode.episode_id}' overlaps recorded episode "
                    f"'{other.episode_id}'"
                )
                raise InvalidInputError(
                    msg, field=f"{_OWNER}.started_on", feature=_FEATURE
                )

    def with_episode(self, episode: SicknessEpisode) -> tuple[SicknessEpisode, ...]:
        """Return the recorded episodes with ``episode`` recorded or replaced.

        Returns:
            The episodes in start order.
        """
        others = [e for e in self.episodes if e.episode_id != episode.episode_id]
        return tuple(sorted((*others, episode), key=lambda e: e.started_on))

    def earlier(self, episode: SicknessEpisode) -> tuple[SicknessEpisode, ...]:
        """Return the recorded episodes other than ``episode``, in start order.

        Returns:
            The episodes that started before ``episode``.
        """
        return tuple(
            sorted(
                (
                    e
                    for e in self.episodes
                    if e.episode_id != episode.episode_id
                    and e.started_on < episode.started_on
                ),
                key=lambda e: e.started_on,
            )
        )
