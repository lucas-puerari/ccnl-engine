"""Part-time hours under an elastic clause: Federmeccanica art. 4.

"Nel caso di variazione della collocazione temporale della prestazione [...]
per le ore oggetto di modifica una maggiorazione [...] pari al 10%"; "per le
ore di lavoro prestate in aumento [...] pari al 15%".  D1, hourly 10.0695:
10 moved hours take 10.07, 10 added hours 115.80.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from tests.mutation.ccnl_engine.working_time.overtime.test_supplementary import (
    _pay,
    _run,
)

_DAY = date(2026, 3, 10)


@pytest.mark.parametrize(
    ("kind", "pay"),
    [
        (OvertimeKind.ELASTIC_PLACEMENT, Decimal("10.07")),
        (OvertimeKind.ELASTIC_INCREASE, Decimal("115.80")),
    ],
)
def test_the_elastic_hours_take_their_premium(kind: OvertimeKind, pay: Decimal) -> None:
    """Moved hours: the 10% alone; added hours: paid at 115%."""
    event = OvertimeEvent(_DAY, hours=Decimal(10), kind=kind)
    assert _pay(_run("metalmeccanico-federmeccanica", "D1", event)) == pay


def test_a_ccnl_without_the_clause_has_no_band() -> None:
    """Logistica sets no elastic band: the rate is the caller's."""
    event = OvertimeEvent(_DAY, hours=Decimal(10), kind=OvertimeKind.ELASTIC_PLACEMENT)
    with pytest.raises(MissingRuleError, match="elastica_collocazione"):
        _run("logistica-trasporto-confetra", "3", event)
