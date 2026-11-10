"""Art. 35 weekly weekday overtime bands across the 48th and 49th hours."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
from ccnl_engine.working_time.overtime.policies import (
    overtime_issues,
    resolve_overtime_rate,
)


@pytest.mark.parametrize(
    ("hours_before", "hours", "expected"),
    [
        ("47", "4", "51.00"),
        ("48", "2", "26.00"),
    ],
)
def test_weekday_event_crosses_weekly_tiers(
    hours_before: str, hours: str, expected: str
) -> None:
    """At EUR 10/h, hours 48-51 pay 11.50 + 12.50 + 13.50 + 13.50 = 51.

    Starting at 48, hours 49-50 instead pay 12.50 + 13.50 = 26;
    the former first-tier-only result would have been EUR 46 (or EUR 23).
    """
    rules = load_ccnl("concia-unic").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    bands = rules.time_supplements.overtime_bands
    event = OvertimeEvent(
        date(2026, 6, 10),
        Decimal(hours),
        Decimal(10),
        weekly_hours_before=Decimal(hours_before),
    )
    rate = resolve_overtime_rate(event, CCNLOvertimeBands(bands))
    assert Decimal(hours) * Decimal(10) * rate.multiplier == Decimal(expected)
    assert not overtime_issues(event, rate)
    assert [slice_[0].code for slice_ in rate.weekly_slices] == (
        ["OT_DIURNO", "OT_DIURNO_EXTRA", "OT_DIURNO_EXTRA_2"]
        if hours_before == "47"
        else ["OT_DIURNO_EXTRA", "OT_DIURNO_EXTRA_2"]
    )


def test_night_daily_tier_stays_unresolved_with_weekly_position() -> None:
    """Weekly position cannot disambiguate the second night hour at 76%."""
    rules = load_ccnl("concia-unic").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    event = OvertimeEvent(
        date(2026, 6, 10),
        Decimal(2),
        Decimal(10),
        kind=OvertimeKind.NIGHT,
        weekly_hours_before=Decimal(48),
    )
    rate = resolve_overtime_rate(
        event, CCNLOvertimeBands(rules.time_supplements.overtime_bands)
    )
    assert rate.multiplier == Decimal("1.61")
    assert {issue.code for issue in overtime_issues(event, rate)} == {
        "overtime_tier_not_applied"
    }
