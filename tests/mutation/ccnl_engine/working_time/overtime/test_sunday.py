"""Sunday overtime outside the weekly rest: its own band, else the weekday band.

- commercio-confcommercio and terziario-confesercenti (art. 149) and
  dmo-federdistribuzione (art. 132 c. 2): "le ore straordinarie di lavoro
  prestato nei giorni festivi o la domenica" are paid 30%, the OT_FESTIVO
  band, also when the weekly rest falls on another day;
- metalmeccanico-federmeccanica has no Sunday band: Sunday overtime of a
  worker who rests on another day is straordinario diurno, OT_DIURNO.
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

_SUNDAY = date(2026, 3, 8)


@pytest.mark.parametrize(
    ("slug", "code", "multiplier"),
    [
        ("commercio-confcommercio", "OT_FESTIVO", "1.30"),
        ("terziario-confesercenti", "OT_FESTIVO", "1.3"),
        ("dmo-federdistribuzione", "OT_FESTIVO", "1.30"),
        ("metalmeccanico-federmeccanica", "OT_DIURNO", None),
    ],
    ids=["commercio", "confesercenti", "dmo", "metal_falls_back_on_weekday"],
)
def test_sunday_band(slug: str, code: str, multiplier: str | None) -> None:
    """The Sunday band applies where it exists, else the weekday band."""
    event = OvertimeEvent(
        _SUNDAY, Decimal(4), Decimal("12.00"), None, OvertimeKind.SUNDAY
    )
    rate = resolve_overtime_rate(event, CCNLOvertimeBands.of(load_ccnl(slug), 2026))

    assert rate.band is not None
    assert rate.band.code == code
    if multiplier is not None:
        assert rate.multiplier == Decimal(multiplier)
