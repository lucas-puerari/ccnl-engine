"""Sickness episodes and employments for sickness tests.

The figures are those of the bundle for metalmeccanico Federmeccanica level
C3 in the first half of 2026: a monthly base salary of 2158.26 EUR, no
fixed allowance, daily quota ``by_26``, CCNL integration 100% from the
first day and comporto of 180 days; INPS tax sector ``industria``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import Employment
from ccnl_engine.events import SicknessEpisode

if TYPE_CHECKING:
    from ccnl_engine.inputs import WorkerCategory

__all__ = [
    "C3_MONTHLY",
    "march_sickness_episode",
    "metalmeccanico_c3",
    "sickness_episode",
]

#: Monthly base salary of metalmeccanico C3 from 1 June 2025 to 31 May 2026.
C3_MONTHLY = Decimal("2158.26")


def sickness_episode(
    episode_id: str,
    started_on: date,
    ended_on: date,
    relapse_of: str | None = None,
) -> SicknessEpisode:
    """Return an episode of the given days.

    Returns:
        The episode.
    """
    return SicknessEpisode(
        episode_id=episode_id,
        started_on=started_on,
        ended_on=ended_on,
        relapse_of=relapse_of,
    )


def march_sickness_episode() -> SicknessEpisode:
    """Return a five-day episode from Monday 9 to Friday 13 March 2026.

    Returns:
        The episode, id ``"2026-03-09"``.
    """
    return sickness_episode("2026-03-09", date(2026, 3, 9), date(2026, 3, 13))


def metalmeccanico_c3(category: WorkerCategory | None) -> Employment:
    """Return a metalmeccanico C3 employment of ``category``.

    Returns:
        The employment; ``None`` leaves the category to the level, which
        does not fix it.
    """
    return Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        category=category,
    )
