"""The CCNL daily share of the reference wage on a sick segment."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.sickness.day.rules import SickDayKind

if TYPE_CHECKING:
    from ccnl_engine.sickness.day.rules import SickDaySegment
    from ccnl_engine.sickness.models import SicknessEpisode

__all__ = ["with_daily_share"]

_ZERO = Decimal(0)


def with_daily_share(
    paid: tuple[Decimal, Decimal, Decimal],
    segment: SickDaySegment,
    episode: SicknessEpisode,
    *,
    excluded: bool,
) -> tuple[Decimal, Decimal, Decimal]:
    """Add the CCNL daily share of the reference wage to a segment's pay.

    The share (``segment.daily_share``) of the contractual daily wage of the
    segment's year is paid for each of its days, on the carenza line for
    the waiting days and on the integration line otherwise.

    Returns:
        ``paid`` (INPS, integration, carenza) with the share added; unchanged
        for a worker the CCNL excludes.
    """
    if excluded:
        return paid
    reference_wage = (episode.contractual_daily_wage_by_year or {}).get(
        segment.first.year, _ZERO
    )
    extra = money(
        reference_wage
        * Decimal((segment.last - segment.first).days + 1)
        * segment.daily_share
    )
    if segment.kind is SickDayKind.CARENZA:
        return paid[0], paid[1], paid[2] + extra
    return paid[0], paid[1] + extra, paid[2]
