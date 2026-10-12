"""Leave tiers by seniority and by date.

CCNL Funzioni Centrali 2022-2024 art. 21 cc. 2, 4-5: 28 days, 26 for the
first three years of a first public employment; the CCNL 2025-2027 art. 21,
in force from 1 January 2027, gives 28 days to every worker.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.working_time.models import LeaveEntitlementTier, LeaveRules

_RULES = LeaveRules(
    default_annual_days=Decimal(28),
    entitlement_tiers=(
        LeaveEntitlementTier(
            service_months_min=0, annual_days=Decimal(26), valid_until=date(2027, 1, 1)
        ),
        LeaveEntitlementTier(service_months_min=36, annual_days=Decimal(28)),
    ),
)


@pytest.mark.parametrize(
    ("months", "day", "days"),
    [
        (12, date(2026, 6, 1), 26),
        (12, date(2027, 1, 1), 28),
        (40, date(2026, 6, 1), 28),
        (None, date(2026, 6, 1), 28),
    ],
)
def test_tier_in_force_on_the_day(months: int | None, day: date, days: int) -> None:
    """The 26 days end on 1 January 2027; seniority unknown takes the default."""
    assert _RULES.annual_days(months, day) == Decimal(days)


def test_tier_from_a_date() -> None:
    """A tier that starts later is not in force before."""
    tier = LeaveEntitlementTier(annual_days=Decimal(30), valid_from=date(2027, 1, 1))

    assert not tier.in_force(date(2026, 12, 31))
    assert tier.in_force(date(2027, 1, 1))
