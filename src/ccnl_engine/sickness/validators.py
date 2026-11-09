"""Validation of a sickness episode as the caller states it."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.sickness.agricultural.inputs import AgriculturalDays
from ccnl_engine.sickness.base.inputs import InpsSicknessBase, SpettacoloSicknessBase
from ccnl_engine.sickness.diagnosis import SeriousIllnessKind
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
    if episode.inps_recognized is not None:
        require_bool(
            episode.inps_recognized,
            f"{_OWNER}.inps_recognized",
            feature=_FEATURE,
        )
    _validate_reference_wages(episode)
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
    _validate_serious(episode)
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
        (InpsSicknessBase, SpettacoloSicknessBase),
        f"{_OWNER}.inps_base",
        feature=_FEATURE,
        optional=True,
    )
    require_instance(
        episode.agricultural_days,
        AgriculturalDays,
        f"{_OWNER}.agricultural_days",
        feature=_FEATURE,
        optional=True,
    )


def _validate_reference_wages(episode: SicknessEpisode) -> None:
    """Reject invalid contractual daily wages by reference year.

    Raises:
        InvalidInputError: If a year or its wage is invalid.
    """
    wages = episode.contractual_daily_wage_by_year
    if wages is not None and (
        not isinstance(wages, dict)
        or any(
            type(year) is not int
            or not isinstance(wage, Decimal)
            or not wage.is_finite()
            or wage < 0
            for year, wage in wages.items()
        )
    ):
        field = f"{_OWNER}.contractual_daily_wage_by_year"
        msg = f"{field}: expected years mapped to nonnegative finite Decimal wages"
        raise InvalidInputError(msg, field=field, feature=_FEATURE)


def _validate_serious(episode: SicknessEpisode) -> None:
    """Validate the documented diagnosis and treatment dates.

    Raises:
        InvalidInputError: If either fact is not valid for the episode.
    """
    require_instance(
        episode.serious_illness_kind,
        SeriousIllnessKind,
        f"{_OWNER}.serious_illness_kind",
        feature=_FEATURE,
        optional=True,
    )
    excluded = episode.excluded_comporto_days or ()
    for day in excluded:
        require_date(day, f"{_OWNER}.excluded_comporto_days", feature=_FEATURE)
        if not episode.started_on <= day <= episode.ended_on:
            msg = "SicknessEpisode.excluded_comporto_days: day outside episode"
            raise InvalidInputError(
                msg, field=f"{_OWNER}.excluded_comporto_days", feature=_FEATURE
            )
    if len(set(excluded)) != len(excluded):
        msg = "SicknessEpisode.excluded_comporto_days: duplicate day"
        raise InvalidInputError(
            msg, field=f"{_OWNER}.excluded_comporto_days", feature=_FEATURE
        )
