"""The CCNL daily share of the reference wage on a segment's pay."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.sickness.day.rules import SickDayKind, SickDaySegment
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.sickness.pay.daily_share import with_daily_share

_DAY = date(2026, 3, 2)
_SEGMENT = SickDaySegment(
    _DAY, _DAY, 1, SickDayKind.CARENZA, Decimal(0), Decimal(1), daily_share=Decimal(1)
)
_EPISODE = SicknessEpisode(
    "e", _DAY, _DAY, contractual_daily_wage_by_year={2026: Decimal(50)}
)


def test_an_excluded_worker_takes_no_share() -> None:
    """A worker the CCNL excludes keeps the pay without the share."""
    paid = (Decimal(1), Decimal(2), Decimal(3))
    assert with_daily_share(paid, _SEGMENT, _EPISODE, excluded=True) == paid


def test_a_waiting_day_takes_the_share_on_the_carenza() -> None:
    """One waiting day at a share of 1 on a wage of 50 adds 50 to the carenza."""
    paid = (Decimal(0), Decimal(0), Decimal(3))
    assert with_daily_share(paid, _SEGMENT, _EPISODE, excluded=False) == (
        Decimal(0),
        Decimal(0),
        Decimal(53),
    )
