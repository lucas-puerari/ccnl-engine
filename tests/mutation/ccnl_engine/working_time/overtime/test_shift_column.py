"""Federmeccanica art. 7: the shift column of night overtime.

CCNL 5 February 2021 (FIOM text, sha256
ff182dd8aeb42b15b236c48775030a12720b9affabba460d38e426ec7be5c151, PDF p.
161): "g) straordinario notturno (prime 2 ore) 50% 40%, (ore successive)
50% 45% [...] l) straordinario notturno festivo 75% 65%", the first column
"per lavoro non a turni", the second "a turni".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.event.facade import OvertimeEvent
from ccnl_engine.working_time.inputs import OvertimeKind
from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
from ccnl_engine.working_time.overtime.policies import resolve_overtime_rate

_DAY = date(2026, 3, 10)


def _bands() -> CCNLOvertimeBands:
    rules = load_ccnl("metalmeccanico-federmeccanica").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    return CCNLOvertimeBands(bands=rules.time_supplements.overtime_bands)


@pytest.mark.parametrize(
    ("kind", "shift", "supplement", "tiers"),
    [
        (OvertimeKind.NIGHT, True, "0.40", ["0.45"]),
        (OvertimeKind.NIGHT, False, "0.50", []),
        (OvertimeKind.NIGHT, None, "0.50", []),
        (OvertimeKind.NIGHT_HOLIDAY, True, "0.65", []),
        (OvertimeKind.NIGHT_HOLIDAY, False, "0.75", []),
        (OvertimeKind.WEEKDAY, True, "0.25", ["0.30"]),
    ],
)
def test_night_overtime_takes_the_column_of_the_worker(
    kind: OvertimeKind, shift: bool | None, supplement: str, tiers: list[str]
) -> None:
    """A turnista takes the second column; an unknown status the first."""
    event = OvertimeEvent(_DAY, Decimal(3), kind=kind, in_periodic_shift=shift)
    rate = resolve_overtime_rate(event, _bands())
    assert rate.supplement == Decimal(supplement)
    assert rate.multiplier == 1 + Decimal(supplement)
    assert [str(r) for _, r in rate.tiers] == tiers
