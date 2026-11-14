"""Logistica art. 13 c. 6: the overtime of the sixth day of a five-day week.

Testo unico Confetra (sha256
99d743d0924958c9cea8e80ec97377763090ad2b3b84d1a4bb8aa5900f0d6e24, PDF p.
39): "lavoro straordinario prestato nella sesta giornata per il personale non
viaggiante con orario normale settimanale distribuito su 5 giorni:
maggiorazione 50%"; the weekday overtime takes 30%.
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


@pytest.mark.parametrize(
    ("kind", "supplement"),
    [(OvertimeKind.SATURDAY, "0.50"), (OvertimeKind.WEEKDAY, "0.3")],
)
def test_sixth_day_pays_fifty_percent(kind: OvertimeKind, supplement: str) -> None:
    """The saturday kind takes the sixth-day band, a weekday the 30%."""
    rules = load_ccnl("logistica-trasporto-confetra").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    bands = CCNLOvertimeBands(bands=rules.time_supplements.overtime_bands)
    rate = resolve_overtime_rate(
        OvertimeEvent(date(2026, 3, 14), Decimal(4), kind=kind), bands
    )
    assert rate.supplement == Decimal(supplement)
