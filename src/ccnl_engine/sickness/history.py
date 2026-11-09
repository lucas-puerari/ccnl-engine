"""Recorded sickness episodes and their relapse chains."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.sickness.models import SicknessEpisode

_FEATURE = "sickness"
_OWNER = "SicknessEpisode"


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

    def chain_days(self, episode: SicknessEpisode) -> int:
        """Return the days in the known relapse chain including later certificates.

        Returns:
            Earlier, current and recorded later days in the same chain.
        """
        total = self.offset(episode) + episode.days
        members = {episode.episode_id}
        for later in sorted(self.episodes, key=lambda item: item.started_on):
            if later.started_on > episode.started_on and later.relapse_of in members:
                members.add(later.episode_id)
                total += later.days
        return total

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
