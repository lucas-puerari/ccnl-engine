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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from ccnl_engine.working_time.overtime.policies import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)
from ccnl_engine.working_time.subsector.rules import with_subsector

_TUESDAY = date(2026, 3, 10)


@pytest.mark.parametrize(
    ("slug", "multiplier"),
    [
        ("metalmeccanico-federmeccanica", "1.10"),
        ("logistica-trasporto-confetra", "1.18"),
        ("edilizia-ance", "1.20"),
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
    """The annual Confetra boundary and Edilizia incidence remain open."""
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

    assert status("metalmeccanico-federmeccanica") == "open"
    assert status("logistica-trasporto-confetra") == "open"
    assert status("edilizia-ance") == "open"


@pytest.mark.parametrize(
    ("category", "available"),
    [(WorkerCategory.OPERAIO, True), (WorkerCategory.IMPIEGATO, False)],
)
def test_edilizia_direct_pay_band_only_covers_manual_workers(
    category: WorkerCategory, available: bool
) -> None:
    """At EUR 12/hour, three manual supplementary hours pay EUR 43.20, not EUR 36."""
    ccnl, _ = with_subsector(load_ccnl("edilizia-ance"), None, category)
    bands = CCNLOvertimeBands.of(ccnl, 2026)
    event = OvertimeEvent(
        _TUESDAY, Decimal(3), Decimal(12), kind=OvertimeKind.SUPPLEMENTARY
    )
    if not available:
        with pytest.raises(MissingRuleError):
            resolve_overtime_rate(event, bands)
    else:
        rate = resolve_overtime_rate(event, bands)
        assert event.hours * Decimal(12) * rate.multiplier == Decimal("43.20")


def test_confetra_supplementary_boundary_with_caller_split() -> None:
    """At EUR 12/hour, 1 hour at 18% plus 2 at 40% pays EUR 47.76 (vs EUR 42.48)."""
    bands = CCNLOvertimeBands.of(load_ccnl("logistica-trasporto-confetra"), 2026)
    below = OvertimeEvent(
        _TUESDAY, Decimal(1), Decimal(12), kind=OvertimeKind.SUPPLEMENTARY
    )
    above = OvertimeEvent(
        _TUESDAY,
        Decimal(2),
        Decimal(12),
        multiplier=Decimal("1.40"),
        kind=OvertimeKind.SUPPLEMENTARY,
    )
    low_rate = resolve_overtime_rate(below, bands)
    high_rate = resolve_overtime_rate(above, bands)
    assert low_rate.derived
    assert low_rate.multiplier == Decimal("1.18")
    assert not high_rate.derived
    assert high_rate.multiplier == Decimal("1.40")
    assert (
        below.hours * Decimal(12) * low_rate.multiplier
        + above.hours * Decimal(12) * high_rate.multiplier
    ) == Decimal("47.76")


def test_federmeccanica_supplementary_boundary_with_caller_split() -> None:
    """At EUR 12/hour, 1 hour at 10% plus 2 at 20% pays EUR 42 (vs EUR 39.60)."""
    bands = CCNLOvertimeBands.of(load_ccnl("metalmeccanico-federmeccanica"), 2026)
    below = OvertimeEvent(
        _TUESDAY, Decimal(1), Decimal(12), kind=OvertimeKind.SUPPLEMENTARY
    )
    above = OvertimeEvent(
        _TUESDAY,
        Decimal(2),
        Decimal(12),
        multiplier=Decimal("1.20"),
        kind=OvertimeKind.SUPPLEMENTARY,
    )
    low_rate = resolve_overtime_rate(below, bands)
    high_rate = resolve_overtime_rate(above, bands)
    assert low_rate.derived
    assert low_rate.multiplier == Decimal("1.10")
    assert not high_rate.derived
    assert high_rate.multiplier == Decimal("1.20")
    assert (
        below.hours * Decimal(12) * low_rate.multiplier
        + above.hours * Decimal(12) * high_rate.multiplier
    ) == Decimal(42)


def test_a_ccnl_without_the_band_asks_for_a_multiplier() -> None:
    """Without a supplementare band the event needs the caller's multiplier."""
    event = OvertimeEvent(
        _TUESDAY, Decimal(3), Decimal("12.00"), kind=OvertimeKind.SUPPLEMENTARY
    )
    bands = CCNLOvertimeBands.of(load_ccnl("terziario-confesercenti"), 2026)

    with pytest.raises(Exception, match="supplementare"):
        resolve_overtime_rate(event, bands)
