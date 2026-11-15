"""The additional hours of the docenti: scuola, Tabella E1.6 (CCNL 18/1/2024).

"Docenti diplomati e laureati [...] € 55,00 € 38,50 € 19,25": a recovery
course, additional teaching and additional non-teaching hours, the whole
pay of the hour.  Two hours each.
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
        (OvertimeKind.RECOVERY_COURSE, Decimal("110.00")),
        (OvertimeKind.EXTRA_TEACHING, Decimal("77.00")),
        (OvertimeKind.EXTRA_NON_TEACHING, Decimal("38.50")),
    ],
)
def test_each_activity_takes_its_hourly_amount(
    kind: OvertimeKind, pay: Decimal
) -> None:
    """Two hours at the E1.6 amount of the activity."""
    event = OvertimeEvent(date(2026, 3, 10), hours=Decimal(2), kind=kind)

    assert _pay(_run("istruzione-ricerca-aran", "DOCENTE_SECONDARIA", event)) == pay
