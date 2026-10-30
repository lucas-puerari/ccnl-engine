"""Validation of a sickness episode as the caller states it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.base.inputs import InpsSicknessBase
from ccnl_engine.validators import (
    require_bool,
    require_date,
    require_instance,
    require_int,
    require_str,
)

if TYPE_CHECKING:
    from ccnl_engine.sickness.models import SicknessEpisode

__all__ = ["validate_episode"]

_FEATURE = "sickness"
_OWNER = "SicknessEpisode"


def validate_episode(episode: SicknessEpisode) -> None:
    """Reject an episode whose fields are malformed or inconsistent.

    Raises:
        InvalidInputError: As :class:`~ccnl_engine.sickness.models.SicknessEpisode`
            documents.
    """
    require_str(
        episode.episode_id, f"{_OWNER}.episode_id", feature=_FEATURE, non_blank=True
    )
    require_date(episode.started_on, f"{_OWNER}.started_on", feature=_FEATURE)
    require_date(episode.ended_on, f"{_OWNER}.ended_on", feature=_FEATURE)
    require_str(
        episode.relapse_of,
        f"{_OWNER}.relapse_of",
        feature=_FEATURE,
        non_blank=True,
        optional=True,
    )
    if episode.short_absence_exempt is not None:
        require_bool(
            episode.short_absence_exempt,
            f"{_OWNER}.short_absence_exempt",
            feature=_FEATURE,
        )
    require_int(
        episode.daily_contributions,
        f"{_OWNER}.daily_contributions",
        feature=_FEATURE,
        minimum=0,
        maximum=1000,
        optional=True,
    )
    require_int(
        episode.prior_worked_days,
        f"{_OWNER}.prior_worked_days",
        feature=_FEATURE,
        minimum=0,
        maximum=366,
        optional=True,
    )
    for flag in ("serious_illness", "periodic_check"):
        value = getattr(episode, flag)
        if value is not None:
            require_bool(value, f"{_OWNER}.{flag}", feature=_FEATURE)
    for first, last in episode.hospital_stays or ():
        require_date(first, f"{_OWNER}.hospital_stays", feature=_FEATURE)
        require_date(last, f"{_OWNER}.hospital_stays", feature=_FEATURE)
        if not episode.started_on <= first <= last <= episode.ended_on:
            msg = (
                f"{_OWNER}.hospital_stays: the stay {first} - {last} must lie "
                f"within the episode {episode.started_on} - {episode.ended_on}"
            )
            raise InvalidInputError(
                msg, field=f"{_OWNER}.hospital_stays", feature=_FEATURE
            )
    if episode.ended_on < episode.started_on:
        msg = (
            f"{_OWNER}.ended_on ({episode.ended_on}) must not precede "
            f"started_on ({episode.started_on})"
        )
        raise InvalidInputError(msg, field=f"{_OWNER}.ended_on", feature=_FEATURE)
    if episode.relapse_of == episode.episode_id:
        msg = f"{_OWNER} '{episode.episode_id}' cannot be a relapse of itself"
        raise InvalidInputError(msg, field=f"{_OWNER}.relapse_of", feature=_FEATURE)
    require_instance(
        episode.inps_base,
        InpsSicknessBase,
        f"{_OWNER}.inps_base",
        feature=_FEATURE,
        optional=True,
    )
