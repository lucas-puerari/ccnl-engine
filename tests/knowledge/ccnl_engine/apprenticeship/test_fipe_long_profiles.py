"""The 48- and 42-month apprentices of the Pubblici esercizi (artt. 68, 72).

Art. 72 c. 2 (PDF p. 75): "la durata massima è fissata in quarantotto mesi"
for named profiles of levels 2 and 3, 42 months for those of level 4; art. 68
c. 1 (p. 74): 80, 85, 90 and 95% in the fourth year, "nei casi in cui la
durata massima [...] sia superiore a 36 mesi".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.errors import OutOfScopeError


def _rate(slug: str, level: str, months: int, track: str | None) -> Decimal | None:
    ccnl = load_ccnl(slug)
    _, rate, _ = _apprentice_chain(
        ccnl,
        ccnl.level_by_code(level),
        Apprentice(months_elapsed=months, track=track),
        0,
        frozenset(),
        date(2026, 6, 1),
    )
    return rate


@pytest.mark.parametrize(
    "slug",
    [
        "pubblici-esercizi-fipe-angem",
        "pubblici-esercizi-fipe-angem-ristorazione-collettiva",
    ],
)
@pytest.mark.parametrize(
    ("level", "track", "months", "rate"),
    [
        ("2", "professionalizzante_48_mesi", 36, "0.95"),
        ("3", "professionalizzante_48_mesi", 47, "0.95"),
        ("3", "professionalizzante_48_mesi", 48, "1.00"),
        ("4", "professionalizzante_42_mesi", 41, "0.95"),
        ("4", "professionalizzante_42_mesi", 42, "1.00"),
        ("4", "professionalizzante", 36, "1.00"),
    ],
)
def test_the_fourth_year_is_paid_at_95_percent(
    slug: str, level: str, track: str, months: int, rate: str
) -> None:
    """95% from month 37 to the end of the long track, 100% after it."""
    assert _rate(slug, level, months, track) == Decimal(rate)


def test_a_level_with_a_long_track_needs_the_track() -> None:
    """Levels 2, 3 and 4 have two tracks: the profile picks one."""
    with pytest.raises(OutOfScopeError, match="several apprenticeship tracks"):
        _rate("pubblici-esercizi-fipe-angem", "3", 0, None)
