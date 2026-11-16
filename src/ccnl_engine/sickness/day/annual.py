"""Annual day counters and the optional reference-wage employer supplement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
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
    limit = _annual_limit(rules, day)
    if share is None or minimum is None or limit is None or beyond_comporto:
        return _ZERO
    if (
        episode.inps_recognized is not True
        or day.year not in (episode.contractual_daily_wage_by_year or {})
        or chain_days <= minimum
    ):
        return _ZERO
    return share if take(days.employer_share, day, limit) else _ZERO


def _annual_limit(rules: SickPayRules, day: date) -> int | None:
    """Return the days a year the share is paid on ``day``, if any.

    A fixed-term worker takes the share of ``fixed_term_daily_share`` from
    its day of the employment (the hiring day being the first), when the
    hiring day is known.

    Returns:
        The annual limit; ``None`` when the worker is not paid the share.
    """
    if not rules.fixed_term:
        return rules.ccnl.daily_share_annual_max_days
    fixed = rules.ccnl.fixed_term_daily_share
    hired = rules.worker.hired_on
    if fixed is None or hired is None:
        return None
    if day < hired + timedelta(days=fixed.from_day - 1):
        return None
    return fixed.annual_max_days
