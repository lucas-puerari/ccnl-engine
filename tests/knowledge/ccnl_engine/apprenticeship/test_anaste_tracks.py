"""The two apprenticeships of ANASTE (Art. 22 c. 12-15, p. 19).

Levels 1-5: "dal 1° al 6° mese: 90% [...] dal 7° mese: 95%", for "12 mesi";
levels 6-10: "dal 1°al 28° mese: 90% [...] dal 29° mese: 95%", for "32 mesi";
then "la retribuzione [...] corrispondenti alla qualifica" (c. 13).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice


def _rate(level: str, months: int) -> Decimal | None:
    ccnl = load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
    _, rate, _ = _apprentice_chain(
        ccnl,
        ccnl.level_by_code(level),
        Apprentice(months_elapsed=months),
        0,
        frozenset(),
        date(2026, 3, 1),
    )
    return rate


@pytest.mark.parametrize(
    ("level", "months", "rate"),
    [
        ("3", 5, "0.90"),
        ("3", 6, "0.95"),
        ("3", 12, "1.00"),
        ("8", 27, "0.90"),
        ("8", 28, "0.95"),
        ("8", 32, "1.00"),
    ],
)
def test_each_level_follows_its_track(level: str, months: int, rate: str) -> None:
    """12 months for levels 1-5, 32 for levels 6-10, full pay after."""
    assert _rate(level, months) == Decimal(rate)
