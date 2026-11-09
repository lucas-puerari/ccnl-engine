"""Apply independent hourly employer coefficients to sick-day segment pay."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.sickness.day.rules import SickDayKind, SickDaySegment
from ccnl_engine.sickness.integration.hourly import hourly_employer_pay

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.sickness.integration.hourly import HourlyEmployerIntegration
    from ccnl_engine.sickness.models import SicknessEpisode
    from ccnl_engine.sickness.term.rules import SicknessTerms

_ZERO = Decimal(0)


def hourly_segment_pay(
    paid: tuple[Decimal, Decimal, Decimal],
    spec: HourlyEmployerIntegration | None,
    segment: SickDaySegment,
    episode: SicknessEpisode,
    terms: SicknessTerms,
    chain: MonthlyPayChain,
    divisor: Decimal,
    *,
    excluded: bool,
) -> tuple[Decimal, Decimal, Decimal]:
    """Replace a target-rate top-up with an independent hourly coefficient.

    Returns:
        The INPS amount unchanged and the direct employer cash for the
        waiting or indemnified segment. Other CCNLs retain their pay.
    """
    if spec is None or not terms.paid_by_the_hour or excluded:
        return paid
    direct = hourly_employer_pay(
        spec,
        segment,
        terms.hourly_chain or chain,
        divisor,
        terms.weekly_hours or spec.standard_weekly_hours,
        frozenset()
        if terms.holidays is None
        else terms.holidays.between(segment.first, segment.last),
        terms.history.offset(episode)
        + (episode.ended_on - episode.started_on).days
        + 1,
    )
    return (
        paid[0],
        direct if segment.kind is not SickDayKind.CARENZA else _ZERO,
        direct if segment.kind is SickDayKind.CARENZA else _ZERO,
    )
