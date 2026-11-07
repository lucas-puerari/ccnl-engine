"""Saturday overtime: its own band where the CCNL has one, else the weekday band.

- metalmeccanico-artigianato (2021 text, PDF p. 84): with a Monday-Friday
  week, Saturday overtime is paid 25% for the first 3 hours and 50% after;
- metalmeccanico-federmeccanica has no Saturday band: Saturday overtime is
  straordinario diurno, OT_DIURNO.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from ccnl_engine.working_time.overtime.policies import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)

_SATURDAY = date(2026, 3, 7)


@pytest.mark.parametrize(
    ("slug", "code", "multiplier"),
    [
        ("metalmeccanico-artigianato", "OT_SABATO", "1.25"),
        ("metalmeccanico-federmeccanica", "OT_DIURNO", None),
    ],
    ids=["artisan_saturday_band", "metal_falls_back_on_weekday"],
)
def test_saturday_band(slug: str, code: str, multiplier: str | None) -> None:
    """The Saturday band applies where it exists, else the weekday band."""
    event = OvertimeEvent(
        _SATURDAY, Decimal(5), Decimal("12.00"), None, OvertimeKind.SATURDAY
    )
    rate = resolve_overtime_rate(event, CCNLOvertimeBands.of(load_ccnl(slug), 2026))

    assert rate.band is not None
    assert rate.band.code == code
    if multiplier is not None:
        assert rate.multiplier == Decimal(multiplier)
        assert [b.code for b, _ in rate.tiers] == ["OT_SABATO_OLTRE_3_ORE"]
