"""Supplementary hours of a part-time worker: the CCNL supplementare band.

D.Lgs. 81/2015 art. 6 c. 2 leaves the rate of the lavoro supplementare to
the CCNL:

- metalmeccanico-federmeccanica (CCNL 5 February 2021, PDF p. 58): an
  all-inclusive 10%;
- logistica-trasporto-confetra (testo unico, Art. 56, p. 71): 18%;
- edilizia-ance (CCNL 19 April 2010, Art. 78, pp. 90-91): 20% for the
  operai.
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

_TUESDAY = date(2026, 3, 10)


@pytest.mark.parametrize(
    ("slug", "multiplier"),
    [
        ("metalmeccanico-federmeccanica.json", "1.10"),
        ("logistica-trasporto-confetra.json", "1.18"),
        ("edilizia-ance.json", "1.20"),
    ],
    ids=["federmeccanica", "logistica", "edilizia"],
)
def test_supplementary_hours_take_the_supplementare_band(
    slug: str, multiplier: str
) -> None:
    """The supplementary kind selects the supplementare band, not overtime."""
    event = OvertimeEvent(
        _TUESDAY, Decimal(3), Decimal("12.00"), kind=OvertimeKind.SUPPLEMENTARY
    )
    rate = resolve_overtime_rate(event, CCNLOvertimeBands.of(load_ccnl(slug), 2026))

    assert rate.derived
    assert rate.band is not None
    assert rate.band.code == "OT_SUPPLEMENTARE"
    assert rate.multiplier == Decimal(multiplier)


def test_supplementary_resolution_of_the_limitations() -> None:
    """Federmeccanica and logistica resolve it; edilizia keeps the incidence."""
    variant = "part_time_supplementary_rate"

    def status(slug: str) -> str:
        ccnl = load_ccnl(slug)
        (note,) = [
            n
            for n in ccnl.coverage.notes
            if n.limitation and n.limitation.variant == variant
        ]
        assert note.limitation is not None
        return str(note.limitation.status)

    assert status("metalmeccanico-federmeccanica.json") == "resolved"
    assert status("logistica-trasporto-confetra.json") == "resolved"
    assert status("edilizia-ance.json") == "open"


def test_a_ccnl_without_the_band_asks_for_a_multiplier() -> None:
    """Without a supplementare band the event needs the caller's multiplier."""
    event = OvertimeEvent(
        _TUESDAY, Decimal(3), Decimal("12.00"), kind=OvertimeKind.SUPPLEMENTARY
    )
    bands = CCNLOvertimeBands.of(load_ccnl("terziario-confesercenti.json"), 2026)

    with pytest.raises(Exception, match="supplementare"):
        resolve_overtime_rate(event, bands)
