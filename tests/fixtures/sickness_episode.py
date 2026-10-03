"""Builder of a structured sick-leave episode for public API tests.

:class:`~ccnl_engine.SicknessCaseEvent` is public but the episode it wraps
is not exported from the package root, so acceptance tests build it here.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import SicknessCaseEvent
from ccnl_engine.payroll.domain.sickness import SicknessCase

__all__ = ["march_sickness_episode"]

_START = date(2026, 3, 9)


def march_sickness_episode(cumulative_sick_days_ytd: int) -> SicknessCaseEvent:
    """Return a five-day episode from Monday 9 March 2026, three of carenza.

    Args:
        cumulative_sick_days_ytd: Sick days of the year before the episode.

    Returns:
        The episode as a work event.
    """
    case = SicknessCase(
        episode_start=_START,
        episode_end=date(2026, 3, 13),
        working_days=5,
        waiting_period_days=3,
        gross_daily=Decimal("83.01"),
        inps_daily_rate=Decimal("0.5"),
        integration_rate=Decimal(1),
        cumulative_sick_days_ytd=cumulative_sick_days_ytd,
    )
    return SicknessCaseEvent(event_date=_START, case=case)
