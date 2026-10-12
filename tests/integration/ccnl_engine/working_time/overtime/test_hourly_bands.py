"""Overtime bands in EUR per hour, by level.

Istruzione e Ricerca, CCNL 2019-2021 art. 80 c. 2 and Tabella E1.7 (from 1
January 2024, not amended since): the ATA 'prestazioni aggiuntive' are paid
per hour by area, diurne / notturne o festive / notturne e festive:
operatori and collaboratori 13.75 / 15.95 / 18.70, assistenti 15.95 /
18.15 / 20.90, funzionari 20.35 / 22.54 / 26.95.  The docenti have no band.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.facade import OvertimeEvent, OvertimeKind
from ccnl_engine.working_time.models import OvertimeBand, TimeSupplements
from ccnl_engine.working_time.overtime.policies import (
    CCNLOvertimeBands,
    band_decision,
    resolve_overtime_rate,
)

_IR = load_ccnl("istruzione-ricerca-aran.json")
_DAY = date(2026, 3, 10)


def _event(kind: OvertimeKind, multiplier: Decimal | None = None) -> OvertimeEvent:
    # The hourly rate is replaced by the band amount.
    return OvertimeEvent(_DAY, Decimal(3), Decimal("99.00"), multiplier, kind)


@pytest.mark.parametrize(
    ("level", "kind", "amount"),
    [
        ("COLLABORATORE_SCOLASTICO", OvertimeKind.WEEKDAY, "13.75"),
        ("OPERATORE", OvertimeKind.NIGHT, "15.95"),
        ("ASSISTENTE", OvertimeKind.HOLIDAY, "18.15"),
        ("ASSISTENTE", OvertimeKind.REST_DAY, "18.15"),
        ("FUNZIONARIO_ED_ESPERTO", OvertimeKind.NIGHT_HOLIDAY, "26.95"),
    ],
)
def test_the_amount_of_the_area_is_paid_per_hour(
    level: str, kind: OvertimeKind, amount: str
) -> None:
    """3 hours at the amount of the area and time of day, multiplier 1."""
    bands = CCNLOvertimeBands.of(_IR, 2026, level)
    rate = resolve_overtime_rate(_event(kind), bands)
    paid = rate.paid(_event(kind))

    assert rate.hourly_amount == Decimal(amount)
    assert (paid.hourly_rate, paid.multiplier) == (Decimal(amount), Decimal(1))
    decision = band_decision(paid, rate, bands, Decimal(3) * Decimal(amount))
    assert decision is not None
    assert decision.inputs["band_hourly_amount"] == Decimal(amount)


def test_a_level_without_band_fails_closed() -> None:
    """The docenti ore aggiuntive are by activity: no band, an explicit rate."""
    bands = CCNLOvertimeBands.of(_IR, 2026, "DOCENTE_SECONDARIA")
    with pytest.raises(InvalidInputError, match="no first-tier"):
        resolve_overtime_rate(_event(OvertimeKind.WEEKDAY), bands)


def test_the_caller_multiplier_prevails() -> None:
    """An explicit multiplier keeps the caller's hourly rate."""
    bands = CCNLOvertimeBands.of(_IR, 2026, "ASSISTENTE")
    event = _event(OvertimeKind.WEEKDAY, Decimal(1))
    rate = resolve_overtime_rate(event, bands)

    assert not rate.derived
    assert rate.paid(event).hourly_rate == Decimal("99.00")


def test_dirigenza_hourly_band_is_paid() -> None:
    """A CCNL-wide band in EUR per hour applies to every level."""
    ccnl = load_ccnl("dirigenza-sanitaria-area-sanita-aran.json")
    rate = resolve_overtime_rate(
        _event(OvertimeKind.WEEKDAY), CCNLOvertimeBands.of(ccnl, 2026)
    )
    assert rate.hourly_amount == Decimal("30.72")


def _band(code: str, levels: tuple[str, ...]) -> dict[str, object]:
    return {
        "code": code,
        "description": code,
        "kind": "indennita_per_hour",
        "rate": {
            "periods": [
                {"valid_from": "2024-01-01", "valid_until": None, "value": "10"}
            ]
        },
        "applies_to_kinds": ["weekday"],
        "levels": levels,
    }


@pytest.mark.parametrize(
    ("first", "second", "collide"),
    [(("A",), ("B",), False), (("A",), ("A", "B"), True), ((), ("B",), True)],
    ids=["disjoint", "shared_level", "every_level"],
)
def test_bands_of_one_kind_collide_only_on_a_shared_level(
    first: tuple[str, ...], second: tuple[str, ...], collide: bool
) -> None:
    """Two unconditional bands of a kind are ambiguous only for a shared level."""
    supplements = {
        "overtime_bands": [_band("OT_A", first), _band("OT_B", second)],
    }
    if collide:
        with pytest.raises(ValueError, match="Ambiguous"):
            TimeSupplements.model_validate(supplements)
    else:
        bands = TimeSupplements.model_validate(supplements).overtime_bands
        assert all(isinstance(b, OvertimeBand) for b in bands)
