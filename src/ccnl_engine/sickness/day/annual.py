"""Annual day counters and the optional reference-wage employer supplement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.sickness.day.models import SickPayRules
    from ccnl_engine.sickness.models import SicknessEpisode

_ZERO = Decimal(0)


@dataclass
class InpsDays:
    """Days paid per calendar year, counted as days are walked.

    ``used`` counts the INPS days, ``short_term`` the days of a yearly
    fixed-term limit (D.L. 463/1983 art. 5 c. 3, the agricultural lists).
    """

    used: dict[int, int] = field(default_factory=dict)
    short_term: dict[int, int] = field(default_factory=dict)
    employer_share: dict[int, int] = field(default_factory=dict)

    def take(self, day: date, limit: int) -> bool:
        """Count ``day`` as paid when the year has room left.

        Returns:
            Whether INPS pays ``day``.
        """
        return take(self.used, day, limit)


def take(used: dict[int, int], day: date, limit: int) -> bool:
    """Count the day against the annual limit.

    Returns:
        Whether there is room for this day.
    """
    count = used.get(day.year, 0)
    if count >= limit:
        return False
    used[day.year] = count + 1
    return True


def daily_share(
    episode: SicknessEpisode,
    day: date,
    rules: SickPayRules,
    days: InpsDays,
    *,
    beyond_comporto: bool,
    chain_days: int,
) -> Decimal:
    """Select and count the employer share only on eligible days.

    Returns:
        The additional fraction of the reference wage, or zero.
    """
    share = rules.ccnl.annual_daily_share
    minimum = rules.ccnl.daily_share_min_days
    limit = rules.ccnl.daily_share_annual_max_days
    if (
        share is None
        or minimum is None
        or limit is None
        or rules.fixed_term
        or beyond_comporto
    ):
        return _ZERO
    if (
        episode.inps_recognized is not True
        or day.year not in (episode.contractual_daily_wage_by_year or {})
        or chain_days <= minimum
    ):
        return _ZERO
    return share if take(days.employer_share, day, limit) else _ZERO
