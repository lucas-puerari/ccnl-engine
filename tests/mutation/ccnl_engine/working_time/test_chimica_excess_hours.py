"""Art. 9 point 1: a hand-computed week at the 37h45 and 40h boundaries."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
from ccnl_engine.working_time.overtime.policies import resolve_overtime_rate


def test_weekly_excess_and_overtime_crossing_40() -> None:
    """At EUR 10/h, 2.25h x 1.05 + 2h x 1.10 = EUR 45.625.

    Before the point-1 band this event used the 10% weekday first tier for
    all 4.25h, EUR 46.75. The 5% supplement is on the hourly Art. 15(1)
    base; underlying pay or compensatory rest is a separate arrangement.
    """
    bands = CCNLOvertimeBands.of(
        load_ccnl("chimica-farmaceutica-federchimica"), 2026, "D1"
    )
    event = OvertimeEvent(
        date(2026, 11, 10),
        Decimal("4.25"),
        Decimal(10),
        weekly_hours_before=Decimal("37.75"),
    )
    rate = resolve_overtime_rate(event, bands)
    assert [(band.code, hours) for band, _, hours in rate.weekly_slices] == [
        ("OT_ECCEDENTE", Decimal("2.25")),
        ("OT_DIURNO_WEEKLY", Decimal(2)),
    ]
    assert sum(
        (
            hours * (1 + supplement) * Decimal(10)
            for _, supplement, hours in rate.weekly_slices
        ),
        Decimal(0),
    ) == Decimal("45.625")


def test_full_weekly_tiers_and_legacy_first_tier() -> None:
    """At EUR 10/h, 2.25h x 1.05 + 4h x 1.10 + 1h x 1.25 = EUR 80.125."""
    bands = CCNLOvertimeBands.of(
        load_ccnl("chimica-farmaceutica-federchimica"), 2026, "D1"
    )
    event = OvertimeEvent(
        date(2026, 11, 10),
        Decimal("7.25"),
        Decimal(10),
        weekly_hours_before=Decimal("37.75"),
    )
    rate = resolve_overtime_rate(event, bands)
    assert [(band.code, hours) for band, _, hours in rate.weekly_slices] == [
        ("OT_ECCEDENTE", Decimal("2.25")),
        ("OT_DIURNO_WEEKLY", Decimal(4)),
        ("OT_DIURNO_EXTRA", Decimal(1)),
    ]
    assert sum(
        (
            hours * (1 + supplement) * Decimal(10)
            for _, supplement, hours in rate.weekly_slices
        ),
        Decimal(0),
    ) == Decimal("80.125")
    no_position = OvertimeEvent(date(2026, 11, 10), Decimal(1), Decimal(10))
    assert resolve_overtime_rate(no_position, bands).multiplier == Decimal("1.10")
