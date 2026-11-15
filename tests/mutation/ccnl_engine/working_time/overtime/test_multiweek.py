"""The hours above the normal week of a multi-week schedule: Federmeccanica.

Art. 5 as renewed on 22 November 2025: the workers "percepiranno la
retribuzione relativa all'orario contrattuale settimanale normale" and the
hours above it take "una maggiorazione [...] del 15% per le ore prestate dal
lunedì al venerdì e del 25% per le ore prestate al sabato", 20% and 30% for
sudden needs.  D1, hourly 10.0695: 10 hours take 15.10, 25.17, 20.14, 30.21.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from tests.mutation.ccnl_engine.working_time.overtime.test_supplementary import (
    _pay,
    _run,
)


@pytest.mark.parametrize(
    ("kind", "pay"),
    [
        (OvertimeKind.MULTIWEEK, Decimal("15.10")),
        (OvertimeKind.MULTIWEEK_SATURDAY, Decimal("25.17")),
        (OvertimeKind.MULTIWEEK_SUDDEN, Decimal("20.14")),
        (OvertimeKind.MULTIWEEK_SUDDEN_SATURDAY, Decimal("30.21")),
    ],
)
def test_the_hours_above_the_week_take_the_premium(
    kind: OvertimeKind, pay: Decimal
) -> None:
    """Premium only: the hours are in the pay of the normal week."""
    event = OvertimeEvent(date(2026, 3, 10), hours=Decimal(10), kind=kind)
    assert _pay(_run("metalmeccanico-federmeccanica", "D1", event)) == pay
