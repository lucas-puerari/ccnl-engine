"""Reconstruct the annual counters from previously recorded sick days."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.sickness.day.annual import InpsDays

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ccnl_engine.sickness.day.models import SickPayRules
    from ccnl_engine.sickness.day.rules import _Day
    from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory


class DayWalker(Protocol):
    """Walk the classified days, optionally using a known relapse length."""

    def __call__(
        self,
        episode: SicknessEpisode,
        span: tuple[date, date],
        history: SicknessHistory,
        rules: SickPayRules,
        inps: InpsDays,
        *,
        chain_days: int | None = None,
    ) -> Iterator[tuple[date, int, _Day]]:
        """Yield the classified days in the requested span."""


def used_before(
    episode: SicknessEpisode,
    first: date,
    history: SicknessHistory,
    rules: SickPayRules,
    walk: DayWalker,
) -> InpsDays:
    """Return the INPS days paid before ``first``, walking every earlier day.

    Returns:
        The days paid per calendar year by the earlier episodes and by the
        days of ``episode`` before ``first``.
    """
    inps = InpsDays()
    chain_days = history.offset(episode) + episode.days
    ancestors: set[str] = set()
    parent = episode.relapse_of
    while parent is not None:
        ancestors.add(parent)
        previous = next(e for e in history.episodes if e.episode_id == parent)
        parent = previous.relapse_of
    for earlier in history.earlier(episode):
        span = (earlier.started_on, earlier.ended_on)
        for _ in walk(
            earlier,
            span,
            history,
            rules,
            inps,
            chain_days=chain_days if earlier.episode_id in ancestors else None,
        ):
            pass
    head = episode.before(first)
    if head is not None:
        span = (head.started_on, head.ended_on)
        for _ in walk(episode, span, history, rules, inps):
            pass
    return inps
