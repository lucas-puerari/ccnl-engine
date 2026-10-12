"""Rest-day overtime: its own band where the CCNL has one, else the holiday band.

- logistica-trasporto-confetra-viaggiante (art. 13 c. 6): the travelling
  staff's Sunday overtime is paid 30% (OT_RIPOSO), the festività 65%;
- metalmeccanico-federmeccanica has no rest-day band: Sunday overtime is
  straordinario festivo, OT_FESTIVO 0.55.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from ccnl_engine.period.decision.override.services import caller_supplied_decisions
from ccnl_engine.working_time.overtime.policies import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)

_SUNDAY = date(2026, 3, 8)
_DRIVERS = "logistica-trasporto-confetra-viaggiante.json"
_METAL = "metalmeccanico-federmeccanica.json"


def _overtime(kind: OvertimeKind, multiplier: Decimal | None = None) -> OvertimeEvent:
    return OvertimeEvent(_SUNDAY, Decimal(4), Decimal("12.00"), multiplier, kind)


@pytest.mark.parametrize(
    ("slug", "kind", "code", "multiplier"),
    [
        (_DRIVERS, OvertimeKind.REST_DAY, "OT_RIPOSO", "1.3"),
        (_DRIVERS, OvertimeKind.HOLIDAY, "OT_FESTIVO", "1.65"),
        (_METAL, OvertimeKind.REST_DAY, "OT_FESTIVO", "1.55"),
    ],
    ids=["drivers_sunday", "drivers_festivita", "metal_falls_back_on_holiday"],
)
def test_rest_day_band(
    slug: str, kind: OvertimeKind, code: str, multiplier: str
) -> None:
    """The rest-day band applies where it exists, else the holiday band."""
    rate = resolve_overtime_rate(
        _overtime(kind), CCNLOvertimeBands.of(load_ccnl(slug), 2026)
    )

    assert rate.band is not None
    assert rate.band.code == code
    assert rate.multiplier == Decimal(multiplier)


@pytest.mark.parametrize(
    ("slug", "code", "supplement"),
    [(_DRIVERS, "OT_RIPOSO", "0.3"), (_METAL, "OT_FESTIVO", "0.55")],
    ids=["own_band", "holiday_band"],
)
def test_caller_multiplier_is_compared_with_the_band_it_stands_for(
    slug: str, code: str, supplement: str
) -> None:
    """The decision lists the band the rest-day overtime is paid with."""
    (decision,) = caller_supplied_decisions(
        (_overtime(OvertimeKind.REST_DAY, Decimal("1.40")),), load_ccnl(slug)
    )

    assert decision.inputs[f"bundle_band[{code}]"] == Decimal(supplement)
